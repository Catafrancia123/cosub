#! This cog is in development, do not load it yet.

import discord
import discord.ui as UI
from datetime import datetime
from discord.ext import commands

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(brief="Adjusts settings for the bot.")
    @commands.is_owner()
    async def settings(self, ctx):
        ui_buttons = ButtonInteractions(timeout_duration_seconds=300)
        embedvar = discord.Embed(
            title="Bot Settings",
            description="Use the arrows below to change between settings, and the Enable/Disable buttons to adjust settings.",
            color=discord.Color.blue(),
            timestamp=datetime.now(),
        )            
        embedvar.set_footer(text=f"ID: {self.bot.interaction_id}")
        await ctx.reply(embed=embedvar, view=ui_buttons)
        
class ButtonInteractions(UI.View):
    def __init__(self, timeout_duration_seconds: int = 180):
        self.timeout_duration_seconds = timeout_duration_seconds
        super().__init__(timeout=self.timeout_duration_seconds)

    @discord.ui.button(label=" :arrow_backward: ", style=discord.ButtonStyle.gray)
    async def test_1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Running test_button 1...')
        self.stop()

    @discord.ui.button(label="Enable", style=discord.ButtonStyle.green)
    async def test_2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Running test_button 2', ephemeral=True)
        self.stop()
        
    @discord.ui.button(label=" :arrow_forward: ", style=discord.ButtonStyle.gray)
    async def test_3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Running test_button 3')
        self.stop()

async def setup(bot):
    await bot.add_cog(Settings(bot=bot))