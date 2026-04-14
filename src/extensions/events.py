import discord, toml
from datetime import datetime
from discord.ext import commands

with open("config.toml", "r") as config:
    config_data = toml.load(config)
    admin_roles = config_data["guild-settings"]["admin_roles"]
    
def is_faction_check(ctx):
    is_faction = config_data["guild-settings"][f"{ctx.guild.id}"]["faction"]
    return is_faction

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.check(is_faction_check)
    @commands.has_any_role(*admin_roles)
    @commands.hybrid_command(with_app_command = True, brief = "Hosts a deployment.")
    async def deployment(self, ctx, time_unix: int, location: str, text: str, host: discord.Member = commands.Author):
        member_role = f"<@&{config_data["guild-settings"][f"{ctx.guild.id}"]["member_role"]}>"
        if member_role == 0:
            member_role = "@everyone"
        user = host
        embedvar = discord.Embed(
            title="Deployment",
            description=f"## Host: <@{user.id}>\nTime: <t:{time_unix}:t>, <t:{time_unix}:R>\nPlace: {location}\n\n{text}",
            color=discord.Color.red(),
            timestamp=datetime.now(),
        )
        embedvar.set_footer(text=f"ID: {self.bot.interaction_id}")

        if member_role == 0:
            member_role = "@everyone"
        await ctx.send(member_role, embed=embedvar)

    @commands.check(is_faction_check)
    @commands.has_any_role(*admin_roles)
    @commands.hybrid_command(with_app_command = True, brief = "Hosts a training.")
    async def training(self, ctx, type: str, time_unix: int, text: str, host: discord.Member = commands.Author):
        user = host
        member_role = f"<@&{config_data["guild-settings"][f"{ctx.guild.id}"]["member_role"]}>"
        if member_role == 0:
            member_role = "@everyone"
        embedvar = discord.Embed(
            title=f"{type} Training",
            description=f"### Host: <@{user.id}>\nTime: <t:{time_unix}:t>, <t:{time_unix}:R>\n\n{text}",
            color=discord.Color.red(),
            timestamp=datetime.now(),
        )
        embedvar.set_footer(text=f"ID: {self.bot.interaction_id}")
        
        await ctx.send(f"{member_role}", embed=embedvar)

    @commands.check(is_faction_check)
    @commands.has_any_role(*admin_roles)
    @commands.hybrid_command(with_app_command = True, brief = "Hosts a tryout.")
    async def tryout(self, ctx, time_unix: int, location: str, text: str, host: discord.Member = commands.Author):
        user = host
        member_role = f"<@&{config_data["guild-settings"][f"{ctx.guild.id}"]["member_role"]}>"
        if member_role == 0:
            member_role = "@everyone"
        embedvar = discord.Embed(
            title="A tryout is being hosted!",
            description=f"### Host: <@{user.id}>\nTime: <t:{time_unix}:t>, <t:{time_unix}:R>\nPlace: {location}\n\n{text}",
            color=discord.Color.red(),
            timestamp=datetime.now(),
        )
        embedvar.set_footer(text=f"ID: {self.bot.interaction_id}")
        
        await ctx.send(f"{member_role}", embed=embedvar)

async def setup(bot):
    await bot.add_cog(Events(bot=bot))
