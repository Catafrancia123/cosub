#! This cog is in development, do not load it yet.

import discord, datetime, pathlib
import discord.ui as UI
from discord.ext import commands
pathlib.Path(__file__).parent / "schemas/shift_system.py"
from schemas.shift_system import ShiftSystem

class Shift(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Manage and view your shifts.")
    async def shift_info(self, ctx):
        user = ctx.author

        ui_buttons = ButtonInteractions()
        embedvar = discord.Embed(
            title=ctx.guild.name,
            description="Shift not activated.",
            color=discord.Color.red(),
            timestamp=datetime.datetime.now(),
        )            
        embedvar.set_footer(text=f"ID: {self.bot.interaction_id}")
        await ctx.reply(embed=embedvar, view=ui_buttons)

class ButtonInteractions(UI.View):
    def __init__(self, timeout_duration_seconds: int = 180):
        self.timeout_duration_seconds = timeout_duration_seconds
        super().__init__(timeout=self.timeout_duration_seconds)

    @discord.ui.button(label='Start shift', style=discord.ButtonStyle.green)
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        shift_system = ShiftSystem(interaction)
        await shift_system.start()

    @discord.ui.button(label='Toggle break', style=discord.ButtonStyle.yellow)
    async def sbreak(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Running test_button 2', ephemeral=True)
        self.stop()

    @discord.ui.button(label='End shift', style=discord.ButtonStyle.red)
    async def end(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Running test_button 2', ephemeral=True)
        self.stop()

async def setup(bot):
    await bot.add_cog(Shift(bot=bot))