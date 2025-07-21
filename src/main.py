BOTVER = "0.2.0"
""" Version 0.2.0:
    - Local error handling (every cog)
    - Shift system
    - Added settings system"""

""" TOML vs DB
TOML guilds are written with a dash (-): bot-test
DB guilds are written with a underscore (_): bot_test
"""
#! use better commands on vscode.

import discord, datetime, os, sys, asyncio, playsound3, logging, logging.handlers, asqlite, toml, pathlib
from utils.logs import write_traceback
from schemas.saveloader import check_table
from aiohttp.client_exceptions import ClientConnectorDNSError
from dotenv import load_dotenv
from extensions import EXT_LIST
from discord.ext import commands
from rich import print as rprint

def clear():
    if sys.platform.startswith(('win32')):
        os.system('cls')
    elif sys.platform.startswith(('linux', 'cygwin', 'darwin', 'freebsd')):
        os.system('clear')

SAVE = "save.db"
with open("config.toml", "r") as file:
    config_data = toml.load(file)

class Bot(commands.Bot):
    def __init__(self, *args, ext: list[str], **kwargs):
        self.__version__ = BOTVER
        self.interaction_id = 0
        self.ext = ext
        super().__init__(*args, **kwargs)
    
    def make_error_embed(self, username : str, error_code : int = 99, error_msg : str = None) -> discord.Embed:
        time_format = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        #! errors with "BLANK" can be changed later on
        errors = {1:"Command not found/doesn't exist.", 
                2:"An input is missing, please try again.",
                3:"An input is invalid/unprocessable.",
                4:"You don't have permission to run this command.",
                5:"Server Error. Please try again later.",
                6:"This server doesnt allow the command above to be run. Please contact your server admin.",
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
            timestamp=datetime.datetime.now()
        )
        embedvar.set_footer(text=f"ID: {self.interaction_id}")
        if error_code != 99:
            rprint(f'[grey]{time_format}[/grey] [[bright_red]ERR {error_code:02d}[/bright_red]] by {username}')
        else:
            rprint(f"{time_format} [[bright_red]ERROR[/bright_red]] Python error: {error_msg}")

        return embedvar

    async def setup_hook(self):
        time_format = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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
        await self.tree.sync()
        rprint(f'[grey]{time_format}[/grey] [[light_green]SUCCESSFUL[/light_green]] Synced slash commands and loaded jishaku.')
        rprint(f"[grey]{time_format}[/grey] [[bright_yellow]WARNING[/bright_yellow]] Please ping catamapp for bot maintenance/unknown errors.")
        rprint(f'[grey]{time_format}[/grey] [[light_green]COMPLETE[/light_green]] Bot has completed startup and now can be used.')
        try:
            await asyncio.run(playsound3.playsound("sounds/beep.wav"))
        except Exception as e:
            pass
    
    def on_interaction(self):
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
        else:
            await ctx.reply(embed=self.make_error_embed(user.name,99,error))
            write_traceback(error)
        
async def main():
    time_format = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #* 1. The logger
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

    #* 2. The main function
    unloaded_modules = config_data["bot-settings"]["unloaded_modules"]
    intents = discord.Intents.default()
    intents.members = True #! can see members
    intents.message_content = True #! can see message content
    intents.reactions = True #! can see reactions
    async with Bot(
        command_prefix="!",
        intents=intents,
        allowed_mentions=discord.AllowedMentions(roles=True, users=True, replied_user=True, everyone=True),
        description="Check out the code at: https://github.com/Catafrancia123/cosub",
        ext=EXT_LIST[:-unloaded_modules],
    ) as bot:
        #* 2.1 Database
        server_names = [server.name.replace(" ", "_") for server in bot.guilds]
        for name in server_names:
            try:
                await check_table(name)
            except Exception as e:
                rprint(f'[grey]{time_format}[/grey] [[bright_red]ERROR[/bright_red]] Database table \"{name}\" failed to initialize.')
                write_traceback(e)
        rprint(f'[grey]{time_format}[/grey] [[light_green]SUCCESSFUL[/light_green]] Database ({asqlite.__name__} version [bright_yellow]{asqlite.__version__}[/bright_yellow]) has been set up.')

        load_dotenv()
        data = os.getenv("bot_token")
        if data is None:
            data = config_data["bot-settings"]["bot_token"]
        if "src" not in str(pathlib.Path("./").cwd()):
            raise Exception("Please run this file from the src directory and not from anywhere else.\nThis is to prevent import errors.")

        try:
            await bot.start(data, reconnect=True)
        except ClientConnectorDNSError:
            print("Your device has no internet, please connect your device to the internet and try again")
            
if __name__ == "__main__":
    clear()
    asyncio.run(main())