import discord, sys, os, tomllib
from sqlite3 import DatabaseError
from discord.ext import commands
sys.path.append(os.path.abspath(os.path.join('..', 'schemas')))
from utils.logs import write_traceback
from schemas.saveloader import load, add, edit

SAVE = "save.db"
with open("config.toml", "rb") as config:
    data = tomllib.load(config)
    admin_roles = data["guild-settings"]["admin_roles"] 

class Points(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_any_role(*admin_roles)
    @commands.hybrid_command(with_app_command = True, brief = "Increases a user's points.")
    async def points_increase(self, ctx, is_social_credit: bool, target: discord.User, amount: int):
        if is_social_credit:
            point_type = "social_credit"
        elif not is_social_credit:
            point_type = "ration"

        cur_amount = await load(SAVE, point_type, target.name)
        if cur_amount is None:
            await add(SAVE, point_type, target.name, 0)
            cur_amount = 0
        await edit(SAVE, point_type, target.name, cur_amount+amount)
        await ctx.reply(f"Increased {amount} {point_type}(s) to: <@{target.id}>.")

    @commands.has_any_role(*admin_roles)
    @commands.hybrid_command(with_app_command = True, brief = "Decreases a user's points.")
    async def points_decrease(self, ctx, is_social_credit: bool, target: discord.User, amount: int):
        if is_social_credit:
            point_type = "social_credit"
        elif not is_social_credit:
            point_type = "ration"

        cur_amount = await load(SAVE, point_type, target.name)
        if cur_amount is None:
            await add(SAVE, point_type, target.name, 0)
            cur_amount = 0
        await edit(SAVE, point_type, target.name, cur_amount-amount)
        await ctx.reply(f"Decreased {amount} {point_type}(s) to: <@{target.id}>.")

    @commands.has_any_role(*admin_roles)
    @commands.hybrid_command(with_app_command = True, brief = "Sets a user's points to a set amount")
    async def points_set(self, ctx, is_social_credit: bool, target: discord.User, amount: int):
        if is_social_credit:
            point_type = "social_credit"
        elif not is_social_credit:
            point_type = "ration"

        cur_amount = await load(SAVE, point_type, target.name)
        if cur_amount is None:
            await add(SAVE, point_type, target.name, amount)
        else:
            await edit(SAVE, point_type, target.name, amount)
        await ctx.reply(f"Set to {amount} {point_type}(s) to: <@{target.id}>.")

    @commands.has_any_role(*admin_roles)
    @commands.hybrid_command(with_app_command = True, brief = "Returns the mentioned user's points")
    async def points_amount(self, ctx, is_social_credit: bool, target: discord.User = commands.Author):
        if is_social_credit:
            point_type = "social_credit"
        elif not is_social_credit:
            point_type = "ration"
        
        cur_amount = await load(SAVE, point_type, target.name)
        if cur_amount is None:
            await add(SAVE, point_type, target.name, 0)
            cur_amount = 0
        await ctx.reply(f"<@{target.id}> has {cur_amount} {point_type}(s)")

    async def cog_command_error(self, ctx, error):
        user = ctx.author
        if isinstance(error, commands.MissingAnyRole):
            await ctx.reply(self.bot.make_error_embed(user.name, 4))
        if isinstance(error, DatabaseError):
            await ctx.reply(self.bot.make_error_embed(user.name, 10))
            write_traceback(error)

async def setup(bot):
    await bot.add_cog(Points(bot=bot))   