import random, discord, toml
from math import floor
from datetime import datetime
from discord.ext import commands

with open("config.toml", "r") as config:
    config_data = toml.load(config)
    admin_roles = config_data["guild-settings"]["admin_roles"]

class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(with_app_command = True, brief = "Gets a user's information", aliases=["user", "u", "member", "member_info"])
    async def user_info(self, ctx, target: discord.Member = commands.Author, target_id: int = 0): 
        if target: user = target
        elif target_id: user = await ctx.guild.fetch_member(target_id) 
        is_member = type(user) == discord.Member

        # check for roles
        if is_member:
            roles_text = ""
            for user_role in user.roles:
                roles_text += f"{user_role.name}, "

        timestamps = [user.created_at.timestamp()]
        if is_member: timestamps.append(user.joined_at.timestamp())
        for i, timestamp in enumerate(timestamps):
            temp = round(timestamps[i])
            temp = f"<t:{temp}:R>"
            timestamps[i] = temp

        user_dict = {
            # user info
            "username": user.name,
            "created": timestamps[0],
            "id": user.id,

            # member info
            "break_line_1": 0,
            "joined": timestamps[1] or "N/A",
            "roles": roles_text or "N/A",
            # add activity and infractions later
        }

        # embed variables
        embed_desc = "**User Information**\n"
        for key, value in user_dict.items():
            if value == 0 and is_member:
                embed_desc += "\n**Member Information**\n"
                continue
            embed_desc += f"{key.title()}: {value}\n"

        embedvar = discord.Embed(
            title = f"{user.display_name} ({user.name})",
            description = embed_desc,
            color = discord.Color.blue(),
            timestamp = datetime.now(),
        )
        embedvar.set_thumbnail(url=user.avatar.url)
        embedvar.set_footer(text=f"ID: {self.bot.interaction_id}")

        await ctx.reply(embed=embedvar)

async def setup(bot):
    await bot.add_cog(Information(bot=bot))   
