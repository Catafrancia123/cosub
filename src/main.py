BOTVER = "0.2.2-dev1"
""" Version 0.2.2-dev1:
    - Overhauled Events system
    - Information extension added (user info, bot info, etc)

    - Fixed ID logger for commands
"""

""" TOML vs DB
TOML guilds are written with a dash (-): bot-test
DB guilds are written with a underscore (_): bot_test
"""
#! use better comments on vscode.

import discord, os, sys, asyncio, playsound3, logging, logging.handlers, asqlite, toml, pathlib
from datetime import datetime
from utils.logs import write_traceback
from schemas.saveloader import check_table, add, edit, load, check_data
from aiohttp.client_exceptions import ClientConnectorDNSError
from extensions import EXT_LIST
from discord.ext import commands
from rich import print as rprint

def clear():
    if sys.platform.startswith(('win32')):
        os.system('cls')
    elif sys.platform.startswith(('linux', 'cygwin', 'darwin', 'freebsd')):
        os.system('clear')

#* get config data
SAVE = "save.db"
try:
    with open("config.toml", "r") as file:
        config_data = toml.load(file)
except Exception:
    if "src" not in str(pathlib.Path("./").cwd()):
        raise Exception("Please run this file from the src directory and not from anywhere else.\nThis is to prevent import errors.")

class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        #* interaction_id is basically for the embeds
        self.__version__ = BOTVER
        self.interaction_id = 1
        self.ext = kwargs["ext"]
        self.unloaded_ext = []
        self.logger = kwargs["logger"]

        # global file definition
        self.discord_icon = discord.File("images/discord_icon.ico", filename="discord_icon.ico")
        super().__init__(*args, **kwargs)
    
    def make_error_embed(self, username : str, error_code : int, error_msg : str = None) -> discord.Embed:
        """Returns a embed with an informative error message.
        
        Args:
            username (str): The user's name who did the error.
            error_code (int): Refer to the dictionary inside the main file for the codes.
            error_msg (str) = None: Optional error message for python errors.
            
        Returns:
            discord.Embed: The embed that contains the error message.
        """
        time_format = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        #! errors with "BLANK" can be changed later on
        errors = {
                # input errors 
                1:"An input field is missing, please try again.",
                2:"An input has an invalid type, please try again.",

                # connection errors
                5:"An HTTP error happened, please try again later.",
                9:"Connection with Discord has closed, please try again later.",
                11:"Connection with Discord failed, please try again later.", 

                # permission errors
                4:"You don't have permission to run this command.", # no role
                6:"This server doesnt allow the command above to be run.\nPlease contact your server administrator.", # no setting for whole server
                7:"The bot does not have permissions to run the command.\nPlease contact your server administrator.", # bot perms
                12:"You don't have permission to run this command.\nPlease contact a developer to run the command.", # dev only

                # bot errors
                8:"Intents not properly enabled. Please contact a developer.",
                10:"Database failed to save/load data. Please contact a developer.", 
                99:f"A Python error happened.\nError message: ```{error_msg}```",

                # easter egg
                308:"My name is Walter Hartwell White.\nI live in 308 Negra Arroyo Lane, Albuquerque, NM, 87104.\nThis is my error.",

                # blank
                3:"BLANK",
            }

        embedvar = discord.Embed(
            title=f"Error {error_code:02d}",
            description=errors[error_code],
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        embedvar.set_footer(text=f"ID: {self.interaction_id}")
        if error_code != 99:
            rprint(f'[grey]{time_format}[/grey] [[bright_red]ERR {error_code:02d}[/bright_red]] by {username}')
        else:
            rprint(f"{time_format} [[bright_red]ERROR[/bright_red]] Python error: {error_msg}")
        self.interaction_id += 1
        return embedvar

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
            username = config_data['bot-settings']['local_username']
        except Exception:
            username = "admin"
        startup_embed.set_author(name=f"Bot startup by: {username}")

        #* 2.2 Check Database
        is_activated = config_data["bot-settings"][f"send_startup_message"]
        if not is_activated:
            self.logger.info("BOT CONFIG: startup messsage feature deactivated")
            rprint(f'[grey]{time_format}[/grey] [[bright_yellow]WARNING[/bright_yellow]] Startup message feature deactivated')
        for server in self.guilds:
            #* check if every server has its own table
            await check_table(SAVE, server.id)
            await add(SAVE, "server_info", "id", server.id) 
            #* startup message id thing
            if is_activated:
                try:
                    channel_id = config_data["guild-settings"][f"{server.id}"]["log_channel"]
                    if channel_id == 0: continue
                except Exception as e:
                    rprint(f'[grey]{time_format}[/grey] [[bright_yellow]WARNING[/bright_yellow]] No startup channel defined for guild: {server.name}')
                    write_traceback(e)
                    continue
                log_channel = self.get_channel(channel_id)
                check = await check_data(SAVE, "server_info", "last_startup_message_id", "id", server.id)
                if check:
                    last_message_id = await load(SAVE, "server_info", "last_startup_message_id", "id", server.id)
                    last_message = await log_channel.fetch_message(last_message_id)
                    await last_message.delete()
                await log_channel.send(embed=startup_embed)
                await edit(SAVE, "server_info", "startup_message_id", "id", server.id, log_channel.last_message_id)
                await edit(SAVE, "server_info", "last_startup_message_id", "id", server.id, log_channel.last_message_id)
                self.logger.info("Bot startup: startup message sent to {server.name}")
                rprint(f"[grey]{time_format}[/grey] [[light_green]SUCCESSFUL[/light_green]] Sent status message to guild: {server.name}")

            for member in server.members:
                if member.bot: continue
                try:
                    check = await load(SAVE, f"{server.id}", "points", "id", member.id)
                    if check > 0: continue
                except Exception: pass
                await add(SAVE, f"{server.id}", "id", member.id)

       
        self.logger.info("BOT SETUP: 4/6, database ready.")
        rprint(f'[grey]{time_format}[/grey] [[light_green]SUCCESSFUL[/light_green]] Database ({asqlite.__name__} version [bright_yellow]{asqlite.__version__}[/bright_yellow]) has been set up.')

    async def setup_hook(self):
        time_format = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        rprint(f"[grey]{time_format}[/grey] [[light_green]VERSION[/light_green]] Discord.py version [bright_yellow]{discord.__version__}[/bright_yellow], Bot version [bright_yellow]{self.__version__}[/bright_yellow]")      
        for ext in self.ext:
            try:   
                await self.load_extension(ext.name)
                rprint(f'[grey]{time_format}[/grey] [[light_green]SUCCESSFUL[/light_green]] Module \"{ext.name}\" has been loaded.')
            except Exception as e:               
                rprint(f'[grey]{time_format}[/grey] [[bright_red]ERROR[/bright_red]] Module \"{ext.name}\" failed to load.')
                self.unloaded_ext.append(ext)
                write_traceback(e)
        self.logger.info("BOT SETUP: 5/6, loaded all extensions required (check config.toml for extensions loaded)")
    
        await self.load_extension("jishaku")
        rprint(f'[grey]{time_format}[/grey] [[light_green]SUCCESSFUL[/light_green]] Module \"jishaku\" has been loaded.')
        rprint(f"[grey]{time_format}[/grey] [[bright_yellow]WARNING[/bright_yellow]] Please ping catamapp for bot maintenance/unknown errors.")
        asyncio.create_task(self.startup_setup())
        self.logger.info("BOT SETUP: 6/6, startup complete.")
        rprint(f'[grey]{time_format}[/grey] [[light_green]COMPLETE[/light_green]] Bot has completed startup and now can be used.')
        try:
            await asyncio.run(playsound3.playsound("sounds/beep.wav"))
        except Exception:
            pass
 
    def on_command_completion(self):
        self.logger.info(f"Command ran successfully with ID: {self.interaction_id}.")
        self.interaction_id += 1

    def on_error(self, event):
        exc = sys.exc_info()
        write_traceback(exc, event)

    async def on_command_error(self, ctx, error):
        #! Refer to the error dict for the error codes.
        user = ctx.author
        if isinstance(error, commands.CommandNotFound): pass # ignore typos
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply(embed=self.make_error_embed(user.name,2))
        elif isinstance(error, commands.BadArgument):
            write_traceback(error)
            await ctx.reply(embed=self.make_error_embed(user.name,3))
        elif isinstance(error, commands.MissingAnyRole):
            await ctx.reply(embed=self.make_error_embed(user.name,4))
        elif isinstance(error, discord.HTTPException):
            await ctx.reply(embed=self.make_error_embed(user.name,5))
        elif isinstance(error, commands.CheckFailure):
            await ctx.reply(embed=self.make_error_embed(user.name,6))
        elif isinstance(error, discord.Forbidden):
            await ctx.reply(embed=self.make_error_embed(user.name,7))
        else:
            await ctx.reply(embed=self.make_error_embed(user.name,99,error))
            write_traceback(error)
 
async def main():
    time_format = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #* 1. Set up error and bot loggers
    logs = ["error", "bot"]
    for log_file in logs:
        open(f"{log_file}.log", "w").close()
    logger = logging.getLogger(log_file)

    handler = logging.handlers.RotatingFileHandler( # error.log is special to our logging
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
    logger.info("BOT SETUP: 1/6, logger set up.")
    rprint(f'[grey]{time_format}[/grey] [[light_green]SUCCESSFUL[/light_green]] Logger has been set up.')

    #* 2. Add stuff to bot
    try:
        loaded_modules = config_data["bot-settings"]["loaded_modules"]
        for ext in EXT_LIST:
            if ext.name.replace("extensions.", "") not in loaded_modules:
                EXT_LIST.remove(ext)
    except Exception:
        rprint(f"[grey]{time_format}[/grey] [[bright_yellow]WARNING[/bright_yellow]] All extensions will be loaded.")
    intents = discord.Intents.default()
    intents.members = True #! can see members
    intents.message_content = True #! can see message content``
    async with Bot(
        command_prefix="!",
        intents=intents,
        allowed_mentions=discord.AllowedMentions(roles=True, users=True, replied_user=True, everyone=True),
        description="Check out the code at: https://github.com/Catafrancia123/cosub",
        ext=EXT_LIST,
        logger=logger,
    ) as bot:
        logger.info("BOT SETUP: 2/6, bot class created")
        
        #* 2.1 Load token
        token = config_data["bot-settings"]["bot_token"]
        logger.info("BOT SETUP: 3/6, starting up on discord")
        try:
            await bot.start(token, reconnect=True)
        except ClientConnectorDNSError:
            print("Your device has no internet, please connect your device to the internet and try again")
            
if __name__ == "__main__":
    clear()
    asyncio.run(main())
