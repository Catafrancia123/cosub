BOTVER = "0.2.2-dev3"
""" Version 0.2.2-dev3: 
    - New version check to confirm python and config file versions.
    - Event system fully finished.
    - You can now check any user's information via user id.

    DON'T FORGET TO DO `/SETUP` FIRST!
"""

#! use better comments on vscode.

import discord, os, sys, asyncio, playsound3, logging, logging.handlers, asqlite, toml, pathlib
from datetime import datetime
from schemas.saveloader import check_table, add, edit, load, load_column
from schemas.functions import Functions, VersionError, ChecksumMismatchError
from aiohttp.client_exceptions import ClientConnectorDNSError
from extensions import EXT_LIST
from discord.ext import commands
from rich import print as rprint

def clear():
    if sys.platform.startswith(('win32')):
        os.system('cls')
    elif sys.platform.startswith(('linux', 'cygwin', 'darwin', 'freebsd')):
        os.system('clear')

    
if "src" not in str(pathlib.Path("./").cwd()):
    raise FileNotFoundError("Please run this file from the src directory and not from anywhere else.\nThis is to prevent import errors.")

checksum = os.system("curl https://raw.githubusercontent.com/Catafrancia123/cosub/releases/latest/download/checksum.txt")
#* get config data
SAVE = "save.db"
with open("config.toml", "r") as file:
    config_data = toml.load(file)

    if config_data["version"] != BOTVER:
        raise VersionError(BOTVER, config_data["version"])
    #elif config_data["checksum"] != checksum:
    #    raise ChecksumMismatchError(checksum, config_data["checksum"]) 

    in_testing = config_data["bot_settings"]["in_testing"]

class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        #* interaction_id is basically for the embeds
        self.__version__ = BOTVER
        self.interaction_id = 1
        self.ext = kwargs["ext"]
        self.unloaded_ext = kwargs["unloaded_ext"]
        self.logger = kwargs["logger"]
        self.error_logger = kwargs["error_logger"]

        # global file definition
        self.discord_icon = discord.File("images/discord_icon.ico", filename="discord_icon.ico")
        super().__init__(*args, **kwargs)
    
    async def startup_setup(self):
        #* Make embed for startup
        await self.wait_until_ready()
        time_format = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        startup_embed = discord.Embed(
            title="Bot Status",
            description=f"Bot has been online since:\n<t:{round(datetime.now().timestamp())}:f>\nBot Version: {BOTVER}",
            color=discord.Color.green(),
        )
        startup_embed.set_thumbnail(url=self.user.avatar.url)
        startup_embed.set_footer(text=f"ID: {self.interaction_id}")
        
        try:
            username = config_data['bot_settings']['local_username']
        except Exception:
            username = "admin"
        startup_embed.set_author(name=f"Bot startup by: {username}")

        #* 2.2 Check Database
        is_activated = config_data["bot_settings"]["send_startup_message"]
        if not is_activated:
            self.logger.info("Bot config: startup messsage feature deactivated (due to config)")
            rprint(f'[grey]{time_format}[/grey] [[bright_yellow]WARNING[/bright_yellow]] Startup message feature deactivated, due to configuration.\n[cyan1]INSTRUCTIONS:[/cyan1] Set [code]send_startup_message = true[/code] in [code]config.toml[/code].')
        elif in_testing:
            self.logger.info("Bot config: startup messsage feature deactivated (due to testing)")
            rprint(f'[grey]{time_format}[/grey] [[bright_yellow]WARNING[/bright_yellow]] Startup message feature deactivated, due to being in testing mode.\n[cyan1]INSTRUCTIONS:[/cyan1] Set [code]in_testing = false[/code] in [code]config.toml[/code].')

        await check_table(SAVE)
        for server in self.guilds:
            #* check if every server has its own table
            base = await load_column(SAVE, "server_info", "server_id")
            check = [i[0] for i in base]
            if server.id not in check:
                await add(SAVE, "server_info", "server_id", server.id)
                await edit(SAVE, "server_info", "server_name", "server_id", server.id, server.name)
            #* startup message id thing
            if is_activated and not in_testing:
                try:
                    channel_id = await load(SAVE, "server_info", "log_channel", "server_id", server.id)
                    if channel_id == 0: continue
                except Exception as e:
                    rprint(f'[grey]{time_format}[/grey] [[bright_yellow]WARNING[/bright_yellow]] No startup channel defined for guild: {server.name}')
                    self.logger.exception(e)
                    continue
                message_id = await load(SAVE, "server_info", "startup_message_id", "server_id", server.id)
                log_channel = await self.fetch_channel(channel_id)
                if message_id != 0:
                    log_message = await log_channel.fetch_message(message_id)
                    try:
                        await log_message.edit(embed=startup_embed)
                    except Exception as e:
                        rprint(f'[grey]{time_format}[/grey] [[bright_yellow]WARNING[/bright_yellow]] Unable to edit message for: {server.name}')
                        self.logger.exception(e)

                        await log_channel.send(embed=startup_embed)
                        await edit(SAVE, "server_info", "startup_message_id", "server_id", server.id, log_channel.last_message_id)
                else:
                    await log_channel.send(embed=startup_embed)
                    await edit(SAVE, "server_info", "startup_message_id", "server_id", server.id, log_channel.last_message_id)
                self.logger.info(f"Bot startup: startup message sent to {server.name}")
                rprint(f"[grey]{time_format}[/grey] [[light_green]SUCCESSFUL[/light_green]] Sent status message to guild: {server.name}")

            for member in server.members:
                if member.bot: continue
                try:
                    check = await load(SAVE, f"{server.id}", "points", "server_id", member.id)
                    if check > 0: continue
                except Exception: pass
                await add(SAVE, "server_data", "user_id", member.id)
                await edit(SAVE, "server_data", "server_id", "user_id", member.id, server.id)
       
        self.logger.info("Bot operations: Database operational and ready.")
        rprint(f'[grey]{time_format}[/grey] [[light_green]SUCCESSFUL[/light_green]] Database ({asqlite.__name__} version [bright_yellow]{asqlite.__version__}[/bright_yellow]) has been set up.')

    async def setup_hook(self):
        time_format = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        rprint(f"[grey]{time_format}[/grey] [[bright_yellow]VERSION[/bright_yellow]] Discord.py version [bright_yellow]{discord.__version__}[/bright_yellow], Bot version [bright_yellow]{self.__version__}[/bright_yellow]")
        for ext in self.ext:
            try:   
                await self.load_extension(ext.name)
                rprint(f'[grey]{time_format}[/grey] [[light_green]SUCCESSFUL[/light_green]] Module \"{ext.name}\" has been loaded.')
            except Exception as e:               
                rprint(f'[grey]{time_format}[/grey] [[bright_red]ERROR[/bright_red]] Module \"{ext.name}\" failed to load.\n[cyan1]INSTRUCTIONS:[/cyan1] Fix the problem by checking the error type in [code]error.log[/code] or [code]bot.log[/code], then sync the bot.')
                self.unloaded_ext.append(ext)
                self.logger.exception(e)
        self.logger.info("Bot setup: 4/6, loaded all extensions required (check config.toml for extensions loaded)")
    
        await self.load_extension("jishaku")
        rprint(f'[grey]{time_format}[/grey] [[light_green]SUCCESSFUL[/light_green]] Module \"jishaku\" has been loaded.')
        rprint(f"[grey]{time_format}[/grey] [[bright_yellow]WARNING[/bright_yellow]] Please ping catamapp for bot maintenance/unknown errors.")
        asyncio.create_task(self.startup_setup())
        self.logger.info("Bot setup: 5/6, startup complete.")
        rprint(f'[grey]{time_format}[/grey] [[light_green]COMPLETE[/light_green]] Bot has completed startup and now can be used.')
       
        startup_beep = config_data["bot_settings"]["play_startup_beep"]
        if startup_beep:
            playsound3.playsound("sounds/beep.wav")
        else:
            self.logger.info("Bot config: no startup beep :(")
            rprint(f"[grey]{time_format}[/grey] [[bright_yellow]WARNING[/bright_yellow]] Startup beep deactivated.\n[cyan1]INSTRUCTIONS:[/cyan1] Set [code]play_startup_beep = true[/code] in [code]config.toml[/code]. If you don't have a speaker, ignore this.")
 
    def on_command_completion(self, *args):
        self.logger.info(f"Command ran successfully with ID: {self.interaction_id}.")
        self.interaction_id += 1

    def on_error(self, *args):
        exc = sys.exc_info()
        self.logger.exception(exc)

    async def on_command_error(self, ctx, error):
        #! Refer to the error dict (s/functions.py) for the error codes.
        funcs = Functions()
        if isinstance(error, commands.CommandNotFound): pass # ignore typos
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply(embed=await funcs.make_error_embed(ctx=ctx,error_code=1))
        elif isinstance(error, commands.BadArgument):
            await ctx.reply(embed=await funcs.make_error_embed(ctx=ctx,error_code=2))
        elif isinstance(error, commands.MissingAnyRole):
            await ctx.reply(embed=await funcs.make_error_embed(ctx=ctx,error_code=4))
        elif isinstance(error, discord.HTTPException):
            await ctx.reply(embed=await funcs.make_error_embed(ctx=ctx,error_code=5))
        elif isinstance(error, commands.CheckFailure):
            await ctx.reply(embed=await funcs.make_error_embed(ctx=ctx,error_code=6))
        elif isinstance(error, discord.Forbidden):
            await ctx.reply(embed=await funcs.make_error_embed(ctx=ctx,error_code=7))
        else:
            await ctx.reply(embed=await funcs.make_error_embed(ctx=ctx,error_code=99,error_msg=error))
        self.logger.exception(f"BOT ERROR: {error}")
 
async def main():
    time_format = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #* 1. Set up error and bot loggers
    logs = ["error", "bot"]
    for log_file in logs:
        open(f"{log_file}.log", "w").close()

    # BOT
    logger = logging.getLogger("bot")

    handler = logging.handlers.RotatingFileHandler( 
        filename=f'bot.log',
        encoding='utf-8',
        mode="w",
        maxBytes=16 * 1024 * 1024,  #! 16mb
        backupCount=5,  #! Rotate through 5 files
    )
    dt_fmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter('[{asctime}] {name}: {message}', dt_fmt, style='{')
    handler.setFormatter(formatter)

    discord.utils.setup_logging(handler=handler, formatter=formatter, level=10)
    logger.addHandler(handler)

    # ERROR
    error_logger = logging.getLogger("error")
    error_logger.setLevel(40)

    handler = logging.handlers.RotatingFileHandler( 
        filename=f'error.log',
        encoding='utf-8',
        mode="w",
        maxBytes=16 * 1024 * 1024,  #! 16mb
        backupCount=5,  #! Rotate through 5 files
    )
    handler.setFormatter(formatter)
    error_logger.addHandler(handler)

    logger.info("Bot setup: 1/6, logger set up.")
    rprint(f'[grey]{time_format}[/grey] [[light_green]SUCCESSFUL[/light_green]] Logger has been set up.')

    #* 2. Add stuff to bot
    try:
        loaded_modules = config_data["bot_settings"]["loaded_modules"]
        loaded_ext = unloaded_ext = []
        for ext in EXT_LIST:
            if ext.name.replace("extensions.", "") in loaded_modules:
                loaded_ext.append(ext)
            else:
                unloaded_ext.append(ext)

    except Exception:
        rprint(f"[[bright_yellow]WARNING[/bright_yellow]] All extensions will be loaded.\n[cyan1]INSTRUCTIONS:[/cyan1] To load certain modules, insert the name of the required modules inside [code]config.toml[/code] under [code]loaded_modules[/code]")
        loaded_modules = config_data["bot_settings"]["loaded_modules"]
        loaded_ext = []
        for ext in EXT_LIST:
            if ext.name.replace("extensions.", "") in loaded_modules:
                loaded_ext.append(ext)

    intents = discord.Intents.default()
    intents.members = True #! can see members
    intents.message_content = True #! can see message content
    async with Bot(
        command_prefix="!",
        intents=intents,
        allowed_mentions=discord.AllowedMentions(roles=True, users=True, replied_user=True, everyone=True),
        description="Check out the code at: https://github.com/Catafrancia123/cosub",
        ext=loaded_ext,
        unloaded_ext=unloaded_ext,
        logger=logger,
        error_logger=error_logger,
    ) as bot:
        logger.info("Bot setup: 2/6, bot class created")
        
        #* 2.1 Load token
        token = config_data["bot_settings"]["bot_token"]
        logger.info("Bot setup: 3/6, starting up on discord")
        try:
            await bot.start(token, reconnect=True)
        except ClientConnectorDNSError:
            print("Your device has no internet, please connect your device to the internet and try again")
            
if __name__ == "__main__":
    clear()
    asyncio.run(main())
