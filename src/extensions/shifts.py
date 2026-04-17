#! This extension is in development, do not load it yet.

import discord, time, datetime
import discord.ui as UI
from schemas.saveloader import check_data, edit, load, add
from discord.ext import commands

SAVE = "save.db"

async def check_shifts(ctx):
    check = await check_data(SAVE, ctx.guild.id, "shift_amount", "id", ctx.author.id)
    if not check:
        await add(SAVE, ctx.guild.id, "id", ctx.author.id)
        await edit(SAVE, ctx.guild.id, "shift_amount", "id", ctx.author.id, 0)
    return True

class Shift(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.check(check_shifts)
    @commands.hybrid_command(brief="Manage and view your shifts.", aliases=["shift"])
    async def shift_info(self, ctx):
        user = ctx.author
        check = await check_data(SAVE, ctx.guild.id, "shift_status", "id", user.id)
        if not check:
            await add(SAVE, ctx.guild.id, "id", user.id)

        shift_status = await load(SAVE, ctx.guild.id, "shift_status", "id", user.id) == 1
       
        # EMBED DESC VARS
        shift_amount = await load(SAVE, ctx.guild.id, "shift_amount", "id", user.id)
        total_time = await load(SAVE, ctx.guild.id, "shift_duration_seconds", "id", user.id)

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

        if shift_status:
            embedvar = discord.Embed(
                title=f"{user.avatar.url} {user.name}'s Shift Management",
                description=embed_desc,
                color=discord.Color.green(),
                timestamp=datetime.datetime.now(),
            )
        elif not shift_status:
            embedvar = discord.Embed(
                title="Shift Management ",
                description=embed_desc,
                color=discord.Color.red(),
                timestamp=datetime.datetime.now(),
            )

        ui_buttons = ButtonInteractions(bot=self.bot, timeout_seconds=180)
        embedvar.set_footer(text=f"ID: {self.bot.interaction_id} | Shift Type: default") # change shift type to align if the settings change
        await ctx.reply(embed=embedvar, view=ui_buttons)
        ButtonInteractions(bot=self.bot, shift_id=ctx.channel.last_message_id) # pass the message id

class ShiftSystem():
    def __init__(self, interaction):
        self.start_time = self.total_time = self.time_elapsed = 0
        self.time_between_breaks = []
        self.interaction = interaction
        self.guild = self.interaction.guild

    async def start(self):
        self.start_time = datetime.datetime.now().timestamp()
        await edit(SAVE, self.guild.id, "shift_status", "id", self.interaction.user.id, 1) # no true/false in sql, use 1/0

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

        shift_time = await load(SAVE, self.guild.id, "shift_duration_seconds", "id", self.interaction.user.id)
        shift_amount = await load(SAVE, self.guild.id, "shift_amount", "id", self.interaction.user.id)

        await edit(SAVE, self.guild.id, "shift_duration_seconds", "id", self.interaction.user.id, shift_time+self.total_time)
        await edit(SAVE, self.guild.id, "shift_amount", "id", self.interaction.user.id, shift_amount+1)
        await edit(SAVE, self.guild.id, "shift_status", "id", self.interaction.user.id, 0)

        return self.time_elapsed


class ButtonInteractions(UI.View):
    def __init__(self, **kwargs):
        self.bot = kwargs["bot"]
        try:
            self.shift_message_id = kwargs["shift_id"]
        except Exception: pass

        try:
            super().__init__(timeout=kwargs["timeout_seconds"])
        except Exception:
            super().__init__(timeout=180) # default is 180 seconds
        self.is_break = False

    async def check_status(interaction: discord.Interaction):
        pass

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

async def setup(bot):
    await bot.add_cog(Shift(bot=bot))
