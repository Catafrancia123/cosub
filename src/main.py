BOTVER = "0.1.1"
""" Version 0.1.1:
    - More rewrites
    - Better error handling"""

import discord, datetime, os, sys, asyncio, playsound3, logging, logging.handlers, tomllib, asqlite
from schemas.saveloader import check_table
from aiohttp.client_exceptions import ClientConnectorDNSError
from utils.logs import write_traceback
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
logo = discord.File("images/logo.png", filename="logo.png")

class Bot(commands.Bot):
    def __init__(self, *args, ext: list[str], **kwargs):
        self.ext = ext
        super().__init__(*args, **kwargs)
    
    def make_error_embed(self, username : str, error_code : int = 99, error_msg : str = None) -> discord.Embed:
        time_format = datetime.datetime.strftime(datetime.datetime.now(datetime.timezone.utc), "Today at %I:%M %p UTC.")
        #* add more later!!
        errors = {1:"Command not found/doesn't exist.", 
                2:"An input is missing, please try again.",
                3:"An input is invalid/unprocessable.",
                4:"You don't have permission to run this command.",
                5:"Server Error. Please try again later.",
                6:"Command failure. Please contact a developer.",
                7:"Command didn't register properly. Please contact a developer.",
                8:"Intents not properly enabled. Please contact a developer.",
                9:"Connection with Discord has closed. Please contact a developer.",
                10:"Database failed to save/load data. Please contact a developer.", 
                11:"Connection with Discord failed. Please try again later.", 
                12:"You don't have permission to run this command. Please contact a developer to run the command.",
                99:f"A code error happened. Please contact the developers.\nError essage: ```{error_msg}```"}

        embedvar = discord.Embed(
            title=f"Error {error_code:02d}",
            description=f"{errors[error_code]}",
            color=discord.Color.red(),
            timestamp=time_format
        )
        if error_code != 99:
            rprint(f'[grey]{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/grey] [[bright_red]ERR {error_code:02d}[/bright_red]] by {username}')

        return embedvar

    async def setup_hook(self):
        time_format = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        rprint(f"[grey]{time_format}[/grey] [[light_green]VERSION[/light_green]] Discord.py version [bright_yellow]{discord.__version__}[/bright_yellow], Bot version [bright_yellow]{BOTVER}[/bright_yellow]")
        
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

    async def on_command_error(self, ctx, error):
        user = ctx.author
        time = datetime.datetime.now()
        time_format = time.strftime('%A, %d %B %Y, %I:%M %p') 
        if isinstance(error, commands.CommandNotFound):
            #! command not found
            await ctx.send(embed=self.make_error_embed(user.name,1))
        elif isinstance(error, commands.MissingRequiredArgument):
            #! no input
            await ctx.send(embed=self.make_error_embed(user.name,2))
        elif isinstance(error, commands.BadArgument):
            #! input not valid/wrong
            await ctx.send(embed=self.make_error_embed(user.name,3))
        elif isinstance(error, commands.MissingAnyRole):
            #! no perms?
            await ctx.send(embed=self.make_error_embed(user.name,4))
        elif isinstance(error, discord.HTTPException):
            #! HTTP error
            await ctx.send(embed=self.make_error_embed(user.name,5))
        elif isinstance(error, commands.CheckFailure):
            #! check fail
            await ctx.send(embed=self.make_error_embed(user.name,6))
        elif isinstance(error, discord.Forbidden):
            #! HTTP code 403 (forbidden)
            await ctx.send(embed=self.make_error_embed(user.name,5))
        elif isinstance(error, commands.CommandRegistrationError):
            #! command registration failed
            await ctx.send(embed=self.make_error_embed(user.name,7))
        elif isinstance(error, discord.PrivilegedIntentsRequired):
            #! intents not properly enabled
            await ctx.send(embed=self.make_error_embed(user.name,8))
        elif isinstance(error, discord.ConnectionClosed):
            #! connection with discord closed
            await ctx.send(embed=self.make_error_embed(user.name,9))
        elif isinstance(error, discord.GatewayNotFound):
            #! connection with discord gateaway failed
            await ctx.send(embed=self.make_error_embed(user.name,11))
        elif isinstance(error, discord.NotFound):
            #! HTTP code 404 (not found)
            await ctx.send(embed=self.make_error_embed(user.name,5))
        else:
            #! what happen?? (python error or smth)
            rprint(f"[[bright_red]ERROR[/bright_red]] Python error: {error}\n{time_format}")
            await ctx.send(embed=self.make_error_embed(user.name,error_msg=error))
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
        maxBytes=32 * 1024 * 1024,  #! 32mb
        backupCount=5,  #! Rotate through 5 files
    )
    dt_fmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter('[{asctime}] {name}: {message}', dt_fmt, style='{')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    rprint(f'[grey]{time_format}[/grey] [[light_green]SUCCESSFUL[/light_green]] Logger has been set up.')

    #* 2. The database
    tables = ["ration", "social_credit"]
    for table in tables:
        await check_table(SAVE, table)
    rprint(f'[grey]{time_format}[/grey] [[light_green]SUCCESSFUL[/light_green]] Database (asqlite version [bright_yellow]{asqlite.__version__}[/bright_yellow]) has been set up.')

    #* 3. The startup
    intents = discord.Intents.default()
    intents.members = True #! can see members
    intents.message_content = True #! can see message content
    async with Bot(
        command_prefix="$",
        intents=intents,
        allowed_mentions=discord.AllowedMentions(roles=True, users=True, replied_user=True, everyone=True),
        description="Check out the code at: https://github.com/Catafrancia123/cosub",
        ext=EXT_LIST, #! <-- The number here represents how much modules is unloaded.
    ) as bot:
        load_dotenv()
        data = os.getenv("bot_token")
        for server in bot.guilds:
            print(server)
        if data is None:
            with open("config.toml", "rb") as config:
                data = tomllib.load(config)["bot-settings"]["bot_token"]

        try:
            await bot.start(data, reconnect=True)
        except ClientConnectorDNSError:
            print("Your device has no internet, please connect your device to the internet and try again")
            
if __name__ == "__main__":
    clear()
    asyncio.run(main())