import datetime, discord, tomllib, sys, os
import discord.ui as UI
from extensions import EXT_LIST
from discord.ext import commands
from rich import print as rprint

with open("config.toml", "rb") as config:
    data = tomllib.load(config)
    admin_roles = data["guild-settings"]["admin_roles"]
    
def clear():
    if sys.platform.startswith(('win32')):
        os.system('cls')
    elif sys.platform.startswith(('linux', 'cygwin', 'darwin', 'freebsd')):
        os.system('clear')             

class Maintenance(commands.Cog):    
    def __init__(self, bot):
        self.bot = bot
        self.time_format = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    @commands.has_any_role(*admin_roles)
    @commands.command(brief = "Shuts down the bot manually.")
    async def shutdown(self, ctx):
        user = ctx.author
        await ctx.reply(f"Bot shutdown initated by {user.name}.")
        rprint(f'[grey]{self.time_format}[/grey] [[light_blue]EVN 01[/light_blue]] Bot shutdown initiated by {user.name}')
        await self.bot.close()

    @commands.hybrid_command(with_app_command = True, brief = "Shows the average ping of the bot.")
    async def ping(self, ctx):
        await ctx.reply(f"Discord Bot => {round(self.bot.latency*1000)}ms\n")

    @commands.command(brief = "Used to sync commands.")
    @commands.is_owner()
    async def sync(self, ctx):
        user = ctx.author
        clear()
        rprint(f'[grey]{self.time_format}[/grey] [[light_blue]EVN 02[/light_blue]] Bot extension sync initiated by {user.name}')
        for ext in EXT_LIST: #! <-- The number here represents how much modules is unloaded.
            try:   
                await self.bot.reload_extension(ext.name)
                rprint(f'[grey]{self.time_format}[/grey] [[light_green]SUCCESSFUL[/light_green]] Module \"{ext.name}\" has been reloaded.')
            except Exception as e:
                rprint(f'[grey]{self.time_format}[/grey] [[bright_red]ERROR[/bright_red]] Module \"{ext.name}\" failed to reload.')
                print(e)
        await self.bot.tree.sync()
        await ctx.reply("All commands have been synced.")

    @commands.command(brief="This is a test command.")
    @commands.is_owner()
    async def test(self, ctx):
        ui_buttons = ButtonInteractions(timeout_duration_seconds=120)
        embedvar = discord.Embed(
            title="Test command!!!",
            description="Button test and a timestamp test below!",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now(),
        )
        await ctx.reply(f"{self.bot.guilds}", embed=embedvar, view=ui_buttons)

    async def cog_command_error(self, ctx, error):
        user = ctx.author
        if isinstance(error, commands.MissingAnyRole):
            await ctx.reply(self.bot.make_error_embed(user.name, 4))
        if isinstance(error, commands.NotOwner):
            await ctx.reply(self.bot.make_error_embed(user.name, 12))

class ButtonInteractions(UI.View):
    def __init__(self, timeout_duration_seconds: int = 180):
        self.timeout_duration_seconds = timeout_duration_seconds
        super().__init__(timeout=self.timeout_duration_seconds)

    @discord.ui.button(label='Test button 1', style=discord.ButtonStyle.green)
    async def test_1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Running test_button 1...')
        self.stop()

    @discord.ui.button(label='Test button 2', style=discord.ButtonStyle.red)
    async def test_2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Running test_button 2', ephemeral=True)
        self.stop()


async def setup(bot):
    await bot.add_cog(Maintenance(bot=bot))