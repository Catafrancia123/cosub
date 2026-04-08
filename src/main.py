BOTVER = "0.2.1-dev1"
""" Version 0.2.1-dev1:
    - Modified config.toml structure for better organization
    - Rewrote README.md
    - Added checks for faction-based commands
    - Added settings system"""

""" TOML vs DB
TOML guilds are written with a dash (-): bot-test
DB guilds are written with a underscore (_): bot_test
"""
#! use better comments on vscode.

import discord, os, sys, asyncio, playsound3, logging, logging.handlers, asqlite, toml, pathlib
from datetime import datetime
from utils.logs import write_traceback
from schemas.saveloader import check_table
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
with open("config.toml", "r") as file:
    config_data = toml.load(file)

class Bot(commands.Bot):
    def __init__(self, *args, ext: list[str], **kwargs):
        #* interaction_id is basically for the embeds
        self.__version__ = BOTVER
        self.interaction_id = 1
        self.ext = ext
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
        errors = {1:"Command not found/doesn't exist.", 
                2:"An input is missing, please try again.",
                3:"An input is invalid/unprocessable.",
                4:"You don't have permission to run this command.",
                5:"Server Error. Please try again later.",
                6:"This server doesnt allow the command above to be run. Please contact your server administrator.",
                7:"BLANK",
                8:"Intents not properly enabled. Please contact a developer.",
                9:"Connection with Discord has closed. Please contact a developer.",
                10:"Database failed to save/load data. Please contact a developer.", 
                11:"Connection with Discord failed. Please try again later.", 
                12:"You don't have permission to run this command. Please contact a developer to run the command.",
                99:f"A Python error happened. Please contact the developers.\nError message: ```{error_msg}```"}

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

        return embedvar

    async def startup_setup(self):
        #* Make embed for startup
        await self.wait_until_ready()
        time_format = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        startup_embed = discord.Embed(
            title="Bot Status",
            description=f"> Bot has been online since:\n<t:{round(datetime.now().timestamp())}:f>",
            color=discord.Color.brand_green(),
        )
        startup_embed.set_thumbnail(url=self.user.avatar.url)
        startup_embed.set_footer(text=f"ID: {self.interaction_id}")
        server_names = [server.name.replace(" ", "-") for server in self.guilds]
        for name in server_names:
            try:
                channel_id = config_data["guild-settings"][name]["startup_channel"]
                if channel_id != 0:
                    print("hello world")
                    startup_channel = self.get_channel(channel_id)
                    print(startup_channel.message_count)
                    await startup_channel.delete_messages([startup_channel.last_message_id])
                    await startup_channel.send(embed=startup_embed)
                    rprint(f"[grey]{time_format}[/grey] [[light_green]SUCCESSFUL[/light_green]] Sent status message to guild: {name}")
            except Exception:
                pass

    async def setup_hook(self):
        time_format = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        rprint(f"[grey]{time_format}[/grey] [[light_green]VERSION[/light_green]] Discord.py version [bright_yellow]{discord.__version__}[/bright_yellow], Bot version [bright_yellow]{self.__version__}[/bright_yellow]")      
        for ext in self.ext:
            try:   
                await self.load_extension(ext.name)
                rprint(f'[grey]{time_format}[/grey] [[light_green]SUCCESSFUL[/light_green]] Module \"{ext.name}\" has been loaded.')
            except Exception as e:               
                rprint(f'[grey]{time_format}[/grey] [[bright_red]ERROR[/bright_red]] Module \"{ext.name}\" failed to load.')
                print(e)
                write_traceback(e)
    
        await self.load_extension("jishaku")
        rprint(f'[grey]{time_format}[/grey] [[light_green]SUCCESSFUL[/light_green]] Module \"jishaku\" has been loaded.')
        rprint(f"[grey]{time_format}[/grey] [[bright_yellow]WARNING[/bright_yellow]] Please ping catamapp for bot maintenance/unknown errors.")
        asyncio.create_task(self.startup_setup())
        rprint(f'[grey]{time_format}[/grey] [[light_green]COMPLETE[/light_green]] Bot has completed startup and now can be used.')
        try:
            await asyncio.run(playsound3.playsound("sounds/beep.wav"))
        except Exception as e:
            pass
        
    
    def on_app_command_completion(self):
        self.interaction_id += 1

    async def on_command_error(self, ctx, error):
        #! Refer to the error dict for the error codes.
        user = ctx.author
        if isinstance(error, commands.CommandNotFound):
            await ctx.reply(embed=self.make_error_embed(user.name,1))
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply(embed=self.make_error_embed(user.name,2))
        elif isinstance(error, commands.BadArgument):
            await ctx.reply(embed=self.make_error_embed(user.name,3))
        elif isinstance(error, commands.MissingAnyRole):
            await ctx.reply(embed=self.make_error_embed(user.name,4))
        elif isinstance(error, discord.HTTPException):
            await ctx.reply(embed=self.make_error_embed(user.name,5))
        elif isinstance(error, commands.CheckFailure):
            await ctx.reply(embed=self.make_error_embed(user.name,6))
        else:
            await ctx.reply(embed=self.make_error_embed(user.name,99,error))
            write_traceback(error)
        
async def main():
    time_format = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #* 1. Set up logger
    logs = ["error", "bot"]
    for log_file in logs:
        open(f"{log_file}.log", "w").close()
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)

    handler = logging.handlers.RotatingFileHandler(
        filename='bot.log',
        encoding='utf-8',
        mode="w",
        maxBytes=16 * 1024 * 1024,  #! 16mb
        backupCount=5,  #! Rotate through 5 files
    )
    dt_fmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter('[{asctime}] {name}: {message}', dt_fmt, style='{')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    rprint(f'[grey]{time_format}[/grey] [[light_green]SUCCESSFUL[/light_green]] Logger has been set up.')

    #* 2. Add stuff to bot
    loaded_modules = config_data["bot-settings"]["loaded_modules"]
    for ext in EXT_LIST:
        if ext.name.replace("extensions.", "") not in loaded_modules:
            EXT_LIST.remove(ext)
    intents = discord.Intents.default()
    intents.members = True #! can see members
    intents.message_content = True #! can see message content``
    async with Bot(
        command_prefix="!",
        intents=intents,
        allowed_mentions=discord.AllowedMentions(roles=True, users=True, replied_user=True, everyone=True),
        description="Check out the code at: https://github.com/Catafrancia123/cosub",
        ext=EXT_LIST,
    ) as bot:
        #* 2.1 Check Database
        server_names = [server.name.replace(" ", "_") for server in bot.guilds]
        for name in server_names:
            try:
                await check_table(name)
            except Exception as e:
                rprint(f'[grey]{time_format}[/grey] [[bright_red]ERROR[/bright_red]] Database table \"{name}\" failed to initialize.')
                write_traceback(e)
        rprint(f'[grey]{time_format}[/grey] [[light_green]SUCCESSFUL[/light_green]] Database ({asqlite.__name__} version [bright_yellow]{asqlite.__version__}[/bright_yellow]) has been set up.')

        #* 2.2 Load token and check cwd
        token = config_data["bot-settings"]["bot_token"]
        if "src" not in str(pathlib.Path("./").cwd()):
            raise Exception("Please run this file from the src directory and not from anywhere else.\nThis is to prevent import errors.")

        try:
            await bot.start(token, reconnect=True)
        except ClientConnectorDNSError:
            print("Your device has no internet, please connect your device to the internet and try again")
            
if __name__ == "__main__":
    clear()
    asyncio.run(main())
