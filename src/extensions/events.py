import discord, datetime, sys, os, tomllib
from discord.ext import commands
sys.path.append(os.path.abspath(os.path.join('..', 'utils')))

with open("config.toml", "rb") as config:
    data = tomllib.load(config)
    admin_roles = data["guild-settings"]["admin_roles"]

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logo = discord.File("images/logo.png", filename="logo.png")
        self.time_format = datetime.datetime.strftime(datetime.datetime.now(datetime.timezone.utc), "Today at %I:%M %p UTC.")

    @commands.has_any_role(*admin_roles)
    @commands.hybrid_command(with_app_command = True, brief = "Hosts a deployment.")
    async def deployment(self, ctx, time_unix: int, location: str, text: str, host: discord.Member = commands.Author):
        user = host
        embedvar = discord.Embed(
            title="Deployment",
            description=f"## Host: <@{user.id}>\nTime: <t:{time_unix}:t>, <t:{time_unix}:R>\nPlace: {location}\n\n{text}",
            color=discord.Color.red(),
        )
        embedvar.set_footer(text=self.time_format)

        await ctx.send(f"<@&1326784766812360725>", embed=embedvar)

    @commands.has_any_role(*admin_roles)
    @commands.hybrid_command(with_app_command = True, brief = "Hosts a training.")
    async def training(self, ctx, type: str, time_unix: int, text: str, host: discord.Member = commands.Author):
        user = host
        embedvar = discord.Embed(
            title=f"{type} Training",
            description=f"### Host: <@{user.id}>\nTime: <t:{time_unix}:t>, <t:{time_unix}:R>\n\n{text}",
            color=discord.Color.red(),
        )
        embedvar.set_footer(text=self.time_format)
        
        await ctx.send(f"<@&1326784766812360725>", embed=embedvar)

    @commands.has_any_role(*admin_roles)
    @commands.hybrid_command(with_app_command = True, brief = "Hosts a tryout.")
    async def tryout(self, ctx, time_unix: int, location: str, text: str, host: discord.Member = commands.Author):
        user = host
        embedvar = discord.Embed(
            title="A tryout is being hosted!",
            description=f"### Host: <@{user.id}>\nTime: <t:{time_unix}:t>, <t:{time_unix}:R>\nPlace: {location}\n\n{text}",
            color=discord.Color.red(),
        )
        embedvar.set_footer(text=self.time_format)
        
        await ctx.send(f"<@&1375757830199443506>", embed=embedvar)

async def setup(bot):
    await bot.add_cog(Events(bot=bot))