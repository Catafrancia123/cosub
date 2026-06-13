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
            "server_info": {
                "name": "Server Settings",
                "is_faction": {
                    "index": 1,
                    "description": "**Faction Mode**\nEnables/Disables Faction extensions such as (events, points, shifts, etc)",
                    "type": "select",
                    "value": await load(SAVE, "server_info", "is_faction", "server_id", inter.guild.id),
                },
                "log_channel": {
                    "index": 2,
                    "description": "**Log Channel**\nThe bot's logging channel for errors, announcements, and such (NOT FOR EVENTS).",
                    "type": "channel",
                    "value": await load(SAVE, "server_info", "log_channel", "server_id", inter.guild.id),
                },
            },
        }
        ui_buttons = SettingSelection(bot=self.bot, settings=settings, category="server_info", current="is_faction")
        embedvar = discord.Embed(
            title=settings["server_info"]["name"],
            description=settings["server_info"]["is_faction"]["description"],
            color=discord.Color.blue(),
            timestamp=datetime.now(),
        )            
        embedvar.set_footer(text=f"ID: {self.bot.interaction_id}")
        await inter.response.send_message("Use the arrows below to change between settings, and the Selection to change the settings.", ephemeral=True)
        await inter.followup.send(embed=embedvar, view=ui_buttons)
    
    @app_commands.command(description="Bot Server Setup.")
    async def setup(self, inter: discord.Interaction):
        check = await check_data("./save.db", "server_info", "log_channel", "server_id", inter.guild.id)
        custom_emoji_text = "Before you start, please read on how to get your custom emoji id: [here](https://support.discord.com/hc/en-us/community/posts/360069335891-Get-Emoji-ID)" 
        if not check:
            await inter.response.send_message(custom_emoji_text, view=ModalButton(bot=self.bot), ephemeral=True)
        else:
            await inter.response.send_message(f"You have done setup, pressing the button below will overwrite **ALL** your previous settings, use the `/settings` command if you want to change settings seperately.\n{custom_emoji_text}", view=ModalButton(bot=self.bot), ephemeral=True)
    
class SettingFunction():
    def __init__(self, *args, **kwargs):
        self.bot = kwargs["bot"]
        self.settings = kwargs["settings"]
        self.current_selection = kwargs["current"]
        self.current_category = kwargs["category"]   

    async def change_page(self, inter: discord.Interaction, positive: bool) -> list:
        index = self.settings[self.current_category][self.current_selection]["index"]
        if index == len(self.settings[self.current_category])-1:
            await inter.response.send_message("Can't go any further.", ephemeral=True)
            await self.wait()
        else:
            if positive: index += 1
            elif not positive: index -= 1
            self.bot.logger.info(f"BOT LOG: {index}")
            names = []
            for i in self.settings[self.current_category]:
                names.append(i)
                i = self.settings[self.current_category][i]
                if type(i) != dict: continue
                if i["index"] == index: 
                    data = i 
                    break

            ui_buttons = SettingSelection(bot=self.bot, settings=self.settings, category=self.current_category, current=names[index-1])
            embedvar = discord.Embed(
                title=self.settings[self.current_category]["name"],
                description=self.settings[self.current_category][names[index-1]]["description"],
                color=discord.Color.blue(),
                timestamp=datetime.now(),
            )
            return [embedvar, ui_buttons]

class SettingSelection(UI.View):
    def __init__(self, *args, **kwargs):
        super().__init__(timeout=300)
        self.bot = kwargs["bot"]
        self.settings = kwargs["settings"]
        self.current_selection = kwargs["current"]
        self.current_category = kwargs["category"]
        self.functions = SettingFunction(bot=self.bot, settings=self.settings, current=self.current_selection, category=self.current_category)
       
        self.value = self.settings[self.current_category][self.current_selection]["value"]

    @UI.button(emoji="◀️", style=discord.ButtonStyle.gray, row=2)
    async def left(self, inter: discord.Interaction, button: discord.ui.Button):
        message = await inter.channel.fetch_message(inter.message.id)
        data = await self.functions.change_page(inter, False)
        await message.edit(embed=data[0], view=data[1])

    @UI.select(placeholder="Enable", row=1, options=[discord.SelectOption(label="Enable", value=1), discord.SelectOption(label="Disable", value=0)])
    async def selection(self, inter: discord.Interaction, select: UI.Select):
        value = select.values[0]
        match value:
            case 1: value = "Enabled"
            case 0: value = "Disabled"
        await inter.response.send_message(f"Setting {value}.", ephemeral=True)
        await self.wait()
    
    @UI.button(emoji="▶️", style=discord.ButtonStyle.gray, row=2)
    async def right(self, inter: discord.Interaction, button: discord.ui.Button):
        message = await inter.channel.fetch_message(inter.message.id)
        data = await self.functions.change_page(inter, False)
        await message.edit(embed=data[0], view=data[1])

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
