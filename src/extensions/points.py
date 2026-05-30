import discord, toml, pathlib
from discord.ext import commands
from sqlite3 import DatabaseError
pathlib.Path(__file__).parent / "schemas/saveloader.py"
from schemas.saveloader import check_data, load, add, edit

# PERMISSIONS HANDLED BY INTEGRATIONS TAB!!!

SAVE = "save.db"
async def check_points(ctx):
    check = await check_data(SAVE, ctx.guild.id, "points", "id", ctx.author.id)
    if not check:
        await add(SAVE, ctx.guild.id, "id", ctx.author.id)
        await edit(SAVE, ctx.guild.id, "points", "id", ctx.author.id, 0)
    return True

class Points(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.check(check_points)
    @commands.hybrid_command(with_app_command = True, brief = "Increases a user's points.")
    async def points_increase(self, ctx, target: discord.User, amount: int):
        guild_id = ctx.guild.id
        cur_amount = await load(SAVE, guild_id, "points", "id", target.id)
        new_amount = cur_amount+amount
        if cur_amount is None:
            await add(SAVE, guild_id, "points", 0)
            await add(SAVE, guild_id, "id", target.id)
            cur_amount = 0
        await edit(SAVE, guild_id, "points", "id", target.id, new_amount)
        await ctx.reply(f"Increased {amount} point(s) to: {target.name}.\n{target.name} now has {new_amount} point(s)")

    @commands.check(check_points)
    @commands.hybrid_command(with_app_command = True, brief = "Decreases a user's points.")
    async def points_decrease(self, ctx, target: discord.User, amount: int):
        guild_id = ctx.guild.id
        cur_amount = await load(SAVE, guild_id, "points", "id", target.id)
        new_amount = cur_amount-amount
        if cur_amount is None:
            await add(SAVE, guild_id, "points", 0)
            await add(SAVE, guild_id, "id", target.id)
            cur_amount = 0
        await edit(SAVE, guild_id, "points", "id", target.id, new_amount)
        await ctx.reply(f"Decreased {amount} point(s) to: {target.name}.\n{target.name} now has {new_amount} point(s)")

    @commands.check(check_points)
    @commands.hybrid_command(with_app_command = True, brief = "Sets a user's points to a set amount")
    async def points_set(self, ctx, target: discord.User, amount: int):
        guild_id = ctx.guild.id
        cur_amount = await load(SAVE, guild_id, "points", "id", target.id)
        if cur_amount is None:
            await add(SAVE, guild_id, "points", amount)
            await add(SAVE, guild_id, "id", target.id)
        else:
            await edit(SAVE, guild_id, "points", "id", target.id, amount)
        await ctx.reply(f"Set {amount} point(s) to: {target.name}.")

    @commands.check(check_points)
    @commands.hybrid_command(with_app_command = True, brief = "Returns the mentioned user's points")
    async def points_amount(self, ctx, target: discord.User = commands.Author):
        guild_id = ctx.guild.id
        check = await check_data(SAVE, guild_id, "points", "id", target.id)
        if not check: cur_amount = None
        elif check:
            cur_amount = await load(SAVE, guild_id, "points", "id", target.id)

        if cur_amount is None: # yeah you gotta add it
            await add(SAVE, guild_id, "points", 0)
            await add(SAVE, guild_id, "id", target.id)
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
