import discord, toml, pathlib
from discord.ext import commands
from sqlite3 import DatabaseError
# sys.path.append(os.path.abspath(os.path.join('..', 'schemas')))
pathlib.Path(__file__).parent / "utils/logs.py", "schemas/saveloader.py"
from utils.logs import write_traceback
from schemas.saveloader import load, add, edit

SAVE = "save.db"
with open("config.toml", "r") as config:
    data = toml.load(config)
    admin_roles = data["guild-settings"]["admin_roles"]

class Points(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_any_role(*admin_roles)
    @commands.hybrid_command(with_app_command = True, brief = "Increases a user's points.")
    async def points_increase(self, ctx, target: discord.User, amount: int):
        guild_name = ctx.guild.name.replace(" ", "_")
        cur_amount = await load(SAVE, guild_name, target.name)
        if cur_amount is None:
            await add(SAVE, guild_name, target.name, 0)
            cur_amount = 0
        await edit(SAVE, guild_name, target.name, cur_amount+amount)
        await ctx.reply(f"Increased {amount} point(s) to: {target.name}.")

    @commands.has_any_role(*admin_roles)
    @commands.hybrid_command(with_app_command = True, brief = "Decreases a user's points.")
    async def points_decrease(self, ctx, target: discord.User, amount: int):
        guild_name = ctx.guild.name.replace(" ", "_")
        cur_amount = await load(SAVE, guild_name, target.name)
        if cur_amount is None:
            await add(SAVE, guild_name, target.name, 0)
            cur_amount = 0
        await edit(SAVE, guild_name, target.name, cur_amount-amount)
        await ctx.reply(f"Decreased {amount} point(s) to: {target.name}.")

    @commands.has_any_role(*admin_roles)
    @commands.hybrid_command(with_app_command = True, brief = "Sets a user's points to a set amount")
    async def points_set(self, ctx, target: discord.User, amount: int):
        guild_name = ctx.guild.name.replace(" ", "_")
        cur_amount = await load(SAVE, guild_name, target.name)
        if cur_amount is None:
            await add(SAVE, guild_name, target.name, amount)
        else:
            await edit(SAVE, guild_name, target.name, amount)
        await ctx.reply(f"Set to {amount} point(s) to: {target.name}.")

    @commands.has_any_role(*admin_roles)
    @commands.hybrid_command(with_app_command = True, brief = "Returns the mentioned user's points")
    async def points_amount(self, ctx, target: discord.User = commands.Author):
        guild_name = ctx.guild.name.replace(" ", "_")
        cur_amount = await load(SAVE, guild_name, target.name)
        if cur_amount is None:
            await add(SAVE, guild_name, target.name, 0)
            cur_amount = 0
        await ctx.reply(f"{target.name} has {cur_amount} point(s)")

    async def cog_command_error(self, ctx, error):
        #! Refer to the error dict in main file for the error codes.
        user = ctx.author
        if isinstance(error, DatabaseError):
            await ctx.reply(embed=self.make_error_embed(user.name, 10))
        else:
            await self.bot.on_command_error(ctx, error)
        
        
async def setup(bot):
    await bot.add_cog(Points(bot=bot))   