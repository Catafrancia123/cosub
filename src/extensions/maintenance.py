import datetime, discord, tomllib
from extensions import EXT_LIST
from discord.ext import commands
from rich import print as rprint

with open("config.toml", "rb") as config:
    data = tomllib.load(config)
    admin_roles = data["guild-settings"]["admin_roles"]               

class Maintenance(commands.Cog):    
    def __init__(self, bot):
        self.bot = bot
        self.time_format = datetime.datetime.strftime(datetime.datetime.now(datetime.timezone.utc), "Today at %I:%M %p UTC.")

    @commands.has_any_role(*admin_roles)
    @commands.command(brief = "Shuts down the bot manually.")
    async def shutdown(self, ctx):
        user = ctx.author
        await ctx.reply(f"Bot shutdown initated by {user.name}.")
        rprint(f'[grey]{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/grey] [[light_blue]EVN 01[/light_blue]] Bot shutdown initiated by {user.name}')
        await self.bot.close()

    @commands.hybrid_command(with_app_command = True, brief = "Shows the average ping of the bot.")
    async def ping(self, ctx):
        embedvar = discord.Embed(
            title="Pong!",
            description=f"Average bot ping: {round(self.bot.latency*1000)}ms",
            color=discord.Color.blue(),
        )
        embedvar.set_footer(text=self.time_format)

        await ctx.reply(embed=embedvar)

    @commands.command(brief = "Used to sync commands.")
    @commands.is_owner()
    async def sync(self, ctx):
        user = ctx.author
        rprint(f'[grey]{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/grey] [[light_blue]EVN 02[/light_blue]] Bot extension sync initiated by {user.name}')
        for ext in EXT_LIST: #! <-- The number here represents how much modules is unloaded.
            try:   
                await self.bot.reload_extension(ext.name)
                rprint(f'[grey]{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/grey] [[light_green]SUCCESSFUL[/light_green]] Module \"{ext.name}\" has been reloaded.')
            except Exception as e:
                rprint(f'[grey]{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/grey] [[bright_red]ERROR[/bright_red]] Module \"{ext.name}\" failed to reload.')
                print(e)
        await self.bot.tree.sync()
        await ctx.reply("All commands have been synced.")

async def setup(bot):
    await bot.add_cog(Maintenance(bot=bot))