import discord
from rich import print as rprint
from schemas.saveloader import load
from datetime import datetime

class Functions():
    async def make_error_embed(self, *args, **kwargs) -> discord.Embed:
        ctx = kwargs["ctx"]
        try: error_msg = kwargs['error_msg']
        except Exception: error_msg = "N/A"
        if not ctx: ctx = discord.Context.from_interaction(inter)
        """Returns a embed with an informative error message.
        
        Args:
            user (discord.User or discord.Member): The user who did the error.
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
                13:"BLANK",
                14:"BLANK",
                15:"BLANK",
            }

        error_code = kwargs["error_code"]
        embedvar = discord.Embed(
            title=f"Error {error_code:02d}",
            description=errors[error_code],
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        embedvar.set_author(name=f"User: {ctx.author.name}", icon_url=ctx.author.avatar.url)
        if error_code != 99:
            rprint(f'[grey]{time_format}[/grey] [[bright_red]ERR {error_code:02d}[/bright_red]] by {ctx.author.name}')
        else:
            rprint(f"{time_format} [[bright_red]ERROR[/bright_red]] Python error: {error_msg}")

        log_text = f"Error happened in: https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/{ctx.channel.last_message_id}"
        server_log_channel_id = await load("./save.db", "server_info", "log_channel", "server_id", ctx.guild.id)
        server_log_channel = await ctx.bot.fetch_channel(server_log_channel_id)
        developer_log_channel = await ctx.bot.fetch_channel(1397584273967681697)

        if server_log_channel_id != 1397584273967681697:
            await server_log_channel.send(log_text, embed=embedvar)
        await developer_log_channel.send(log_text, embed=embedvar)
        return embedvar

class VersionError(Exception):
    def __init__(self, python_version, config_version):
        self.message = f"\nOutdated COSUB version!\n\nmain.py: {python_version}\nconfig.toml: {config_version}\n\nPlease confirm your version of COSUB is the newest by going to the GitHub repository:\nhttps://github.com/Catafrancia123/cosub"
        super().__init__(self.message)

    def __str__(self):
        return self.message

class ChecksumMismatchError(Exception):
    def __init__(self, expected, got):
        self.message = f"\nChecksum mismatch!\n\nExpected: {expected}\nGot: {got}\n\nPlease confirm your installation of COSUB is true by installing from the GitHub repository:\nhttps://github.com/Catafrancia123/cosub"
        super().__init__(self.message)

    def __str__(self):
        return self.message
