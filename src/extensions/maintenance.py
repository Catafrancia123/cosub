import discord, toml, sys, os
import discord.ui as UI
from schemas.saveloader import load
from datetime import datetime
from extensions import EXT_LIST
from discord.ext import commands
from rich import print as rprint

with open("config.toml", "r") as config:
    config_data = toml.load(config)
    in_testing = config_data["bot_settings"]["in_testing"]

def trusted_bot_admins_check(ctx):
    trusted_admins = config_data["bot_settings"]["trusted_bot_admins"]
    if ctx.author.id in trusted_admins: 
        print("yes")
        return True
    return False

def clear():
    if sys.platform.startswith(('win32')):
        os.system('cls')
    elif sys.platform.startswith(('linux', 'cygwin', 'darwin', 'freebsd')):
        os.system('clear')

class Maintenance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.time_format = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    @commands.check(trusted_bot_admins_check)
    @commands.command(brief = "Shuts down the bot manually.", aliases=["kill"])
    async def shutdown(self, ctx):
        is_activated = config_data["bot_settings"]["send_startup_message"]
        user = ctx.author
        await ctx.reply("Affirmative, self-destructing current instance...")
        rprint(f'[grey]{self.time_format}[/grey] [[cyan1]EVN 01[/cyan1]] Bot shutdown initiated by {user.name}')
       
        if is_activated and not in_testing:
            startup_embed = discord.Embed(
                title="Bot Status",
                description=f"Bot has been shutdown.\nPlease wait for the next startup.",
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            startup_embed.set_thumbnail(url=self.bot.user.avatar.url)
            startup_embed.set_footer(text=f"ID: {self.bot.interaction_id}")
            startup_embed.set_author(name=f"Shutdown initiated by {user.name}", icon_url=user.avatar.url)
            for server in self.bot.guilds:
                try:
                    channel_id = await load("./save.db", "server_info", "log_channel", "server_id", server.id) 
                    if channel_id == 0: continue
                    log_channel = self.bot.get_channel(channel_id)
                    message_id = await load("./save.db", "server_info", "startup_message_id", "server_id", server.id)

                    status_message = await log_channel.fetch_message(message_id)
                except Exception as e:
                    self.bot.logger.exception(e)
                    continue

                # check message author
                if not status_message.author.id == 1020720588353974272:
                    await log_channel.send(embed=startup_embed)
                else:
                    await status_message.edit(embed=startup_embed)
                rprint(f"[grey]{self.time_format}[/grey] [[light_green]SUCCESSFUL[/light_green]] Sent shutdown message to guild: {server.name}")
        await self.bot.close()

    @commands.hybrid_command(with_app_command = True, brief = "Shows the average ping of the bot.")
    async def ping(self, ctx):
        msg_process_time = (datetime.now().timestamp() - ctx.message.created_at.timestamp()) * 1000
        await ctx.reply(f"Bot Latency => {round(self.bot.latency*1000)}ms\nMessage Processing => {round(msg_process_time)}ms")

    @commands.command(brief = "Used to sync commands.", hidden=True, aliases=["s"])
    @commands.is_owner()
    async def sync(self, ctx):
        user = ctx.author
        rprint(f'\n[grey]{self.time_format}[/grey] [[cyan1]EVN 02[/cyan1]] Bot extension sync initiated by {user.name}')
        for ext in self.bot.ext:
            try:   
                await self.bot.reload_extension(ext.name)
                rprint(f'[grey]{self.time_format}[/grey] [[light_green]SUCCESSFUL[/light_green]] Module \"{ext.name}\" has been re-loaded.')
            except Exception as e:
                rprint(f'[grey]{self.time_format}[/grey] [[bright_red]ERROR[/bright_red]] Module \"{ext.name}\" failed to re-load.\n[cyan1]INSTRUCTIONS:[/cyan1] Fix the problem by checking the error type in [code]error.log[/code] or [code]bot.log[/code], then re-sync.')
                self.bot.logger.exception(e)
    
        # Unloaded Extensions failsafe (shit's redundant, deactivated)
        #if self.bot.unloaded_ext:
        #    for ext in self.bot.unloaded_ext:
        #        try:
        #            await self.bot.load_extension(ext.name)
        #        except commands.ExtensionAlreadyLoaded: pass
        #        rprint(f'[grey]{self.time_format}[/grey] [[light_green]SUCCESSFUL[/light_green]] Module \"{ext.name}\" has been loaded.')
        await self.bot.tree.sync()
        rprint(f'[grey]{self.time_format}[/grey] [[light_green]COMPLETE[/light_green]] Bot has completed syncing.')
        await ctx.reply("All commands have been synced.")

    @commands.command(brief="This is a test command.", hidden=True)
    @commands.is_owner()
    async def test(self, ctx):
        await ctx.reply("nothing for now.")

    @commands.command(brief="Clear's the bot status log", hidden=True, aliases=["cls", "clear"])
    @commands.is_owner()
    async def clear_log(self, ctx):
        user = ctx.author
        clear()
        rprint(f'\n[grey]{self.time_format}[/grey] [[cyan1]EVN 03[/cyan1]] Bot log clear initiated by {user.name}')
        await ctx.reply("Cleared bot log.")

    """@commands.hybrid_command(brief="Runs SQL code for DB adjustments.")
    @commands.is_owner()
    async def run_sql(self, ctx, *args):
        code = " ".join(args)
        async with asqlite.connect("save.db") as conn, conn.cursor() as db:
            await db.execute(code)

        await ctx.reply(f"Ran SQL Code:\n```{code}```", ephemeral=True)"""
        
    async def cog_command_error(self, ctx, error):
        user = ctx.author
        #! Refer to the error dict in main file for the error codes.
        if isinstance(error, commands.NotOwner):
            await ctx.reply(embed=self.make_error_embed(user.name, 12))
        else:
            await self.bot.on_command_error(ctx, error)

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
