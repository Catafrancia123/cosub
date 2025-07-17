import random
from discord.ext import commands

class Humor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(with_app_command = True, brief = "uhh my head hurts")
    async def wack(self, ctx): 
        await ctx.reply("uhh my head hurts\n- WPCO AI Bot")

    @commands.command(brief = "Make the bot say anything.")
    async def say(self, ctx, *, text: str):
        await ctx.message.delete()
        await ctx.send(text)

    @commands.hybrid_command(with_app_command = True, brief = "Classic RNG command.")
    async def roll(self, ctx, end_num: int):
        if end_num > 500:
            await ctx.reply("Too much numbers, try again with numbers less than 500.")
        await ctx.reply(f":game_die: Rolled Number: {random.randint(1, end_num)}")

async def setup(bot):
    await bot.add_cog(Humor(bot=bot))   