#! This cog is in development, do not load it yet.

import discord
import discord.ui as UI
import discord.app_commands as app_commands
from datetime import datetime
from discord.ext import commands
from schemas.saveloader import edit, check_data, load

SAVE = "./save.db"
class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(description="Adjusts settings for the bot.")
    async def settings(self, inter: discord.Interaction):
        settings = {
            "server": {
                "name": "Server Settings",
                "is_faction": {
                    "description": "**Faction Extensions**\n\nEnables/Disables Faction extensions such as (events, points, shifts, etc)", 
                    "value": await load(SAVE, "server_info", "is_faction", "server_id", inter.guild.id),
                },
            },
        }
        ui_buttons = SettingButtonsRight(bot=self.bot, settings=settings, category="server", current="is_faction")
        embedvar = discord.Embed(
            title=settings["server"]["name"],
            description=settings["server"]["is_faction"]["description"],
            color=discord.Color.blue(),
            timestamp=datetime.now(),
        )            
        embedvar.set_footer(text=f"ID: {self.bot.interaction_id}")
        await inter.response.send_message("Use the arrows below to change between settings, and the Enable/Disable buttons to adjust settings.", ephemeral=True)
        await inter.followup.send(embed=embedvar, view=ui_buttons)
    
    @app_commands.command(description="Bot Server Setup.")
    async def setup(self, inter: discord.Interaction):
        check = await check_data("./save.db", "server_info", "log_channel", "server_id", inter.guild.id)
        custom_emoji_text = "Before you start, please read on how to get your custom emoji id: [here](https://support.discord.com/hc/en-us/community/posts/360069335891-Get-Emoji-ID)" 
        if not check:
            await inter.response.send_message(custom_emoji_text, view=ModalButton(bot=self.bot), ephemeral=True)
        else:
            await inter.response.send_message(f"You have done setup, pressing the button below will overwrite **ALL** your previous settings, use the `/settings` command if you want to change settings seperately.\n{custom_emoji_text}", view=ModalButton(bot=self.bot), ephemeral=True)
        
class SettingButtons(UI.View):
    def __init__(self, *args, **kwargs):
        self.bot = kwargs["bot"]
        self.settings = kwargs["settings"]
        self.current_selection = kwargs["current"]
        self.current_category = kwargs["category"]

        self.value = self.settings[self.current_category][self.current_selection]["value"]
        super().__init__(timeout=300)

    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.gray)
    async def left(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Running test_button 1...')
        await self.wait()

    @discord.ui.button(label="Enable", style=discord.ButtonStyle.green)
    async def enable(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Running test_button 2', ephemeral=True)
        await self.wait()

    @discord.ui.button(label="Disable", style=discord.ButtonStyle.red)
    async def disable(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Running test_button 2', ephemeral=True)
        await self.wait()
        
    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.gray)
    async def right(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Running test_button 3')
        await self.wait()

class SettingButtonsRight(UI.View):
    def __init__(self, *args, **kwargs):
        self.bot = kwargs["bot"]
        self.settings = kwargs["settings"]
        self.current_selection = kwargs["current"]
        self.current_category = kwargs["category"]
        self.value = self.settings[self.current_category][self.current_selection]["value"]
        super().__init__(timeout=300)

    @discord.ui.button(label="Enable", style=discord.ButtonStyle.green)
    async def enable(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Running test_button 2', ephemeral=True)
        await self.wait()
    
    @discord.ui.button(label="Disable", style=discord.ButtonStyle.red)
    async def disable(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Running test_button 2', ephemeral=True)
        await self.wait()
        
    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.gray)
    async def right(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Running test_button 3')
        await self.wait()

class SettingButtonsLeft(UI.View):
    def __init__(self, *args, **kwargs):
        self.bot = kwargs["bot"]
        self.settings = kwargs["settings"]
        self.current_selection = kwargs["current"]
        self.current_category = kwargs["category"]
        self.value = self.settings[self.current_category][self.current_selection]["value"]
        super().__init__(timeout=300)

    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.gray)
    async def left(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Running test_button 3')
        await self.wait()

    @discord.ui.button(label="Enable", style=discord.ButtonStyle.green)
    async def enable(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Running test_button 2', ephemeral=True)
        await self.wait()
    
    @discord.ui.button(label="Disable", style=discord.ButtonStyle.red)
    async def disable(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Running test_button 2', ephemeral=True)
        await self.wait()
        

class ModalButton(UI.View):
    def __init__(self, *args, **kwargs):
        self.bot = kwargs["bot"]
        super().__init__(timeout=300)
    
    @UI.button(label="Start", style=discord.ButtonStyle.green) # start
    async def proceed(self, inter: discord.Interaction, button: UI.Button):
        await inter.response.send_modal(SetupForm(bot=self.bot))

class ModalButton(UI.View):
    def __init__(self, *args, **kwargs):
        self.bot = kwargs["bot"]
        super().__init__(timeout=300)
    
    @UI.button(label="Start", style=discord.ButtonStyle.green) # start
    async def proceed(self, inter: discord.Interaction, button: UI.Button):
        await inter.response.send_modal(SetupForm(bot=self.bot))

class ModalButton(UI.View):
    def __init__(self, *args, **kwargs):
        self.bot = kwargs["bot"]
        super().__init__(timeout=300)
    
    @UI.button(label="Start", style=discord.ButtonStyle.green) # start
    async def proceed(self, inter: discord.Interaction, button: UI.Button):
        await inter.response.send_modal(SetupForm(bot=self.bot))

class FactionModalButton(UI.View):
    def __init__(self, *args, **kwargs):
        self.bot = kwargs["bot"]
        self.data = kwargs["data"]
        super().__init__(timeout=300)
    
    @UI.button(label="Proceed", style=discord.ButtonStyle.green) # start
    async def proceed(self, inter: discord.Interaction, button: UI.Button):
        await inter.response.send_modal(SetupFactionForm(bot=self.bot, data=self.data))    

class SetupForm(UI.Modal, title="Bot Server Setup"):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.bot = kwargs["bot"]
        self.member_role = UI.Label(text=f"Member role", component=UI.RoleSelect(placeholder="@everyone", required=True)) # member role 
        self.reaction = UI.Label(text="Reaction emoji (INSERT EMOJI ID)", component=UI.TextInput(style=discord.TextStyle.short, placeholder="Insert the emoji ID here (ignore if don't have)", required=False)) # faction check
        self.log_channel = UI.Label(text="Bot log channel", component=UI.ChannelSelect(channel_types=[discord.ChannelType.text, discord.ChannelType.news, discord.ChannelType.private, discord.ChannelType.public_thread, discord.ChannelType.private_thread, discord.ChannelType.forum, discord.ChannelType.media], required=True)) # log channel
        self.faction = UI.Label(text="Is a faction?", component=UI.Checkbox()) # faction check

        self.all = [self.member_role, self.reaction, self.log_channel, self.faction]
        for i in self.all: self.add_item(i)

    async def on_submit(self, inter: discord.Interaction):
        data = {
            "member_role": self.member_role.component.values[0].id,
            "reaction_emoji": self.reaction.component.value,
            "log_channel": self.log_channel.component.values[0].id,
            "is_faction": self.faction.component.value,
        }
        if not data["reaction_emoji"]: data["reaction_emoji"] = 0
        button = FactionModalButton(bot=self.bot, data=data)
        if data["is_faction"]:
            await inter.response.send_message("Proceed with the second stage of bot setup:", view=button, ephemeral=True)
        else:
            for v in data.items():
                await edit("./save.db", "server_info", v[0], "server_id", inter.guild.id, v[1])
            await inter.response.send_message("Bot successfully set up, you can run more commands now.", ephemeral=True)

class SetupFactionForm(UI.Modal, title="Bot Server Setup (Faction Section)"):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.bot = kwargs["bot"]
        self.data = kwargs["data"]
        self.deployment_log = UI.Label(text="Event log channel (Deployments)", component=UI.ChannelSelect(channel_types=[discord.ChannelType.text, discord.ChannelType.news, discord.ChannelType.private, discord.ChannelType.public_thread, discord.ChannelType.private_thread, discord.ChannelType.forum, discord.ChannelType.media], required=True)) # log channel (deployment)
        self.training_log = UI.Label(text="Event log channel (Trainings)", component=UI.ChannelSelect(channel_types=[discord.ChannelType.text, discord.ChannelType.news, discord.ChannelType.private, discord.ChannelType.public_thread, discord.ChannelType.private_thread, discord.ChannelType.forum, discord.ChannelType.media], required=True)) # log channel (training)
        self.tryout_log = UI.Label(text="Event log channel (Tryout)", component=UI.ChannelSelect(channel_types=[discord.ChannelType.text, discord.ChannelType.news, discord.ChannelType.private, discord.ChannelType.public_thread, discord.ChannelType.private_thread, discord.ChannelType.forum, discord.ChannelType.media], required=True)) # log channel (tryout)

        self.all = [self.deployment_log, self.training_log, self.tryout_log]
        for i in self.all: self.add_item(i)

    async def on_submit(self, inter: discord.Interaction):
        self.data["deployment_log_channel"] = self.deployment_log.component.values[0].id
        self.data["training_log_channel"] = self.training_log.component.values[0].id
        self.data["tryout_log_channel"] = self.tryout_log.component.values[0].id 
        for v in self.data.items():
            await edit("./save.db", "server_info", v[0], "server_id", inter.guild.id, v[1])
        await inter.response.send_message("Bot successfully set up, you can run more commands now.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Settings(bot=bot))
