#! This extension is in development, do not load it yet.

import discord, time, datetime
import discord.ui as UI
from schemas.saveloader import check_data, edit, load, add
from discord.ext import commands

SAVE = "save.db"

async def check_shifts(ctx):
    check = await check_data(SAVE, "server_data", "shift_amount", "user_id", ctx.author.id)
    if not check:
        await add(SAVE, "server_data", "user_id", ctx.author.id)
        await edit(SAVE, "server_data", "shift_amount", "user_id", ctx.author.id, 0)
    return True

class Shift(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.check(check_shifts)
    @commands.hybrid_command(brief="Manage and view your shifts.", aliases=["shift"])
    async def shift_info(self, ctx):
        user = ctx.author
        check = await check_data(SAVE, "server_data", "shift_status", "user_id", user.id)
        if not check:
            await add(SAVE, "server_data", "user_id", user.id)

        shift_status = await load(SAVE, "server_data", "shift_status", "user_id", user.id) == 1
       
        # EMBED DESC VARS
        shift_amount = await load(SAVE, "server_data", "shift_amount", "user_id", user.id)
        total_time = await load(SAVE, "server_data", "shift_duration_seconds", "user_id", user.id)

        if shift_amount <= 0:
            avg_time = 0
        else:
            avg_time = seconds = total_time // shift_amount

        embed_desc = f"""
            **{"Shift Not Activated" if not shift_status else "Shift Activated"}**

            Shift Count: {shift_amount}
            Total Duration: {time.strftime('%H Hours, %M Minutes, %S Seconds', time.gmtime(total_time))}
            Average Duration: {time.strftime('%H Hours, %M Minutes, %S Seconds', time.gmtime(avg_time))}
        """

        embedvar = discord.Embed(
            description=embed_desc,
            color=discord.Color.blue(), # default is blue
            timestamp=datetime.datetime.now(),
        )
        if shift_status:
            embedvar.color = discord.Color.green()

        ui_buttons = ButtonInteractions(bot=self.bot)
        embedvar.set_footer(text=f"ID: {self.bot.interaction_id} | Shift Type: default") # change shift type to align if the settings change
        embedvar.set_author(name="Shift Management", icon_url=user.avatar.url)

        await ctx.reply(embed=embedvar, view=ui_buttons)
        ButtonInteractions(bot=self.bot, shift_id=ctx.channel.last_message_id) # pass the message id



class ButtonInteractions(UI.View):
    def __init__(self, **kwargs):
        self.bot = kwargs["bot"]
        try:
            self.shift_message_id = kwargs["shift_id"]
        except Exception: pass

        self.is_break = False

    @discord.ui.button(label='Start shift', style=discord.ButtonStyle.green)
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        shift_message = self.bot.fetch_message(self.shift_message_id)
        embedvar = discord.Embed(
            title="Shift Information",
            description="Shift activated",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now(),
        )
        embedvar.set_footer(text=f"ID: {self.bot.interaction_id}")
        await shift_message.edit(embed=embedvar)

        await interaction.response.send_message('Shift Started.', ephemeral=True)
        shift_system = ShiftSystem(interaction)
        await shift_system.start()

    @discord.ui.button(label='Toggle break', style=discord.ButtonStyle.grey)
    async def sbreak(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.is_break:
            self.is_break = True
            await interaction.response.send_message('Break toggled.', ephemeral=True)
        elif self.is_break:
            self.is_break = False
            await interaction.response.send_message('Resuming Shift.', ephemeral=True)

        shift_system = ShiftSystem(interaction)
        await shift_system.shift_break(self.is_break)
        self.stop()

    @discord.ui.button(label='End shift', style=discord.ButtonStyle.red)
    async def end(self, interaction: discord.Interaction, button: discord.ui.Button):
        shift_message = self.bot.fetch_message(self.shift_message_id)
        embedvar = discord.Embed(
            title="Shift Information",
            description="Shift not activated",
            color=discord.Color.red(),
            timestamp=datetime.datetime.now(),
        )
        embedvar.set_footer(text=f"ID: {self.bot.interaction_id}")
        await shift_message.edit(embed=embedvar)

        await interaction.response.send_message('Shift Ended.', ephemeral=True)
        shift_system = ShiftSystem(interaction)
        total_time = await shift_system.end()
        await interaction.response.send_message('Total time: {total_time} seconds', ephemeral=True)
        
        self.stop()

class ShiftSystem():
    def __init__(self, interaction):
        self.start_time = self.total_time = self.time_elapsed = 0
        self.time_between_breaks = []
        self.interaction = interaction
        self.guild = self.interaction.guild

    async def start(self):
        self.start_time = datetime.datetime.now().timestamp()
        await edit(SAVE, "server_data", "shift_status", "user_id", self.interaction.user.id, 1) # no true/false in sql, use 1/0

    async def shift_break(self, status: bool): # status is whether you are doing a break/continuing 
        if status == True:
             self.time_between_breaks.append(datetime.datetime.now().timestamp() - self.start_time)
        elif status == False:
            self.start_time = datetime.datetime.now().timestamp()

    async def end(self) -> int:
        self.total_time = datetime.datetime.now().timestamp() - self.start_time
        for time in self.time_between_breaks:
            self.total_time += time
        self.time_elapsed = datetime.timedelta(seconds=int(self.total_time)) # final time in readable way

        shift_time = await load(SAVE, "server_data", "shift_duration_seconds", "user_id", self.interaction.user.id)
        shift_amount = await load(SAVE, "server_data", "shift_amount", "user_id", self.interaction.user.id)

        await edit(SAVE, "server_data", "shift_duration_seconds", "user_id", self.interaction.user.id, shift_time+self.total_time)
        await edit(SAVE, "server_data", "shift_amount", "user_id", self.interaction.user.id, shift_amount+1)
        await edit(SAVE, "server_data", "shift_status", "user_id", self.interaction.user.id, 0)

        return self.time_elapsed

async def setup(bot):
    await bot.add_cog(Shift(bot=bot))
