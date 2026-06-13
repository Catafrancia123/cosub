import random, discord, toml
from math import floor
from datetime import datetime
from discord.ext import commands
from schemas.saveloader import edit, check_data
import discord.ui as UI
import discord.app_commands as app_commands

with open("config.toml", "r") as config:
    config_data = toml.load(config)

class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(with_app_command = True, brief = "Gets a user's information", aliases=["user", "u", "member", "member_info"])
    async def user_info(self, ctx, target = commands.Author):
        is_member = True
        if isinstance(target, int): 
            try:
                user = await ctx.guild.fetch_member(target_id)
            except Exception:
                user = await self.bot.fetch_user(target_id)
                is_member = False
        else: 
            user = target

        # check for roles
        roles = getattr(user, "roles", None)
        roles_text = ""
        if roles:
            for user_role in roles[::-1]:
                if user_role.name == "@everyone": continue
                roles_text += f"<@&{user_role.id}>, "
        else: roles_text = "N/A"

        timestamps = [round(user.created_at.timestamp())]
        tmp = getattr(user, "joined_at", "N/A")
        if tmp != "N/A": timestamps.append(round(tmp.timestamp()))
        else: timestamps.append("N/A")

        for i, timestamp in enumerate(timestamps):
            if not isinstance(timestamp, int): continue
            temp = f"<t:{timestamp}:R>"
            timestamps[i] = temp

        user_dict = {
            # user info
            "profile": f"<@{user.id}>",
            "created": timestamps[0],
            "id": user.id,

            # member info
            "break_line_1": 0,
            "joined": timestamps[1],
            "roles": roles_text,
            # add activity and infractions later
        }

        # embed variables
        embed_desc = "**User Information**\n"
        for key, value in user_dict.items():
            if value == 0 and is_member:
                embed_desc += "\n**Member Information**\n"
                continue
            if key == "id": 
                embed_desc += f"ID: {value}\n"
                continue
            embed_desc += f"{key.title()}: {value}\n"

        if is_member: 
            title = f"{user.display_name} ({user.name})"
        else:
            title = f"{user.name}"
        embedvar = discord.Embed(
            title = title,
            description = embed_desc,
            color = discord.Color.blue(),
            timestamp = datetime.now(),
        )
        embedvar.set_thumbnail(url=user.avatar.url)
        embedvar.set_footer(text=f"ID: {self.bot.interaction_id}")

        await ctx.reply(embed=embedvar)

async def setup(bot):
    await bot.add_cog(Information(bot=bot))   
