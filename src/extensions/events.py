import discord, toml, difflib
from utils.logs import write_traceback
from datetime import datetime
import discord.app_commands as app_commands
from discord.ext import commands
import discord.ui as UI

with open("config.toml", "r") as config:
    config_data = toml.load(config)
    admin_roles = config_data["guild-settings"]["admin_roles"]
    
def is_faction_check(inter: discord.Interaction):
    is_faction = config_data["guild-settings"][f"{inter.guild.id}"]["faction"]
    return is_faction

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.check(is_faction_check)
    @app_commands.checks.has_any_role(*admin_roles)
    @app_commands.command(description="Hosts an event of a specific type")
    async def event(self, inter: discord.Interaction, event_type: str, time_unix: int, location: str, text: str, host: discord.Member = None):
        member_role = config_data["guild-settings"][f"{inter.guild.id}"]["member_role"]
        if member_role == 0:
            member_role = "@here"
        else:
            member_role = f"<@&{member_role}>"

        if host: user = host
        else: user = inter.user
        ui_buttons = ButtonInteractions(
                bot=self.bot, 
                timeout_duration=time_unix+600, 
                event_type=event_type,
                location=location,
        )
        embedvar = discord.Embed(
            title=f"A {event_type} is being hosted!",
            description=f"## Description\nTime: <t:{time_unix}:t>, <t:{time_unix}:R>\nLocation: {location}\n\n{text}",
            color=discord.Color.blue(),
            timestamp=datetime.now(),
        )
        embedvar.set_footer(text=f"ID: {self.bot.interaction_id}")
        embedvar.set_author(name=f"Host: {user.name}", icon_url=user.avatar.url)
        try:
            icon = inter.guild.icon.url
        except AttributeError:
            icon = self.bot.discord_icon.uri # default discord logo
        embedvar.set_thumbnail(url=icon)
        await inter.response.send_message(f"Sent event message. Adjust your deployment settings below.", ephemeral=True) # after this use followup!
        await inter.followup.send(f"{member_role}", embed=embedvar, view=ui_buttons)

        # Reactions
        message_id = inter.channel.last_message_id
        message = await inter.followup.fetch_message(message_id)
        await message.add_reaction("✅")
    
    ## AUTOCOMPLETES ##    
    @event.autocomplete("event_type")
    async def event_type_autocomplete(self, inter: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        selections = ["Deployment", "Training", "Tryout"]
        choices = [app_commands.Choice(name=i, value=i) for i in selections]
        if not current: return choices
        match = difflib.get_close_matches(current, selections, n=25)
        choices = [app_commands.Choice(name=j, value=j) for j in match]

        return choices
    
    @event.autocomplete("time_unix")
    async def time_unix_autocomplete(self, inter: discord.Interaction, current: str):
        selections = ["Now", "In 5 minutes", "In 10 minutes", "In 15 minutes", "In 20 minutes", "In 30 minutes", "In an hour"]
        base_datetime = round(datetime.now().timestamp())
        values = [base_datetime, base_datetime+300, base_datetime+600, base_datetime+900, base_datetime+1200, base_datetime+1800, base_datetime+3600]
        choices = [app_commands.Choice(name=v, value=values[i]) for i, v in enumerate(selections)]
        if not current: return choices

        match = difflib.get_close_matches(current, selections, n=25)
        choices = [app_commands.Choice(name=j, value=selections.index(j)) for j in match]
        return choices


class ButtonInteractions(UI.View):
    def __init__(self, *args, **kwargs):
        self.bot = kwargs["bot"]
        self.event_type = kwargs["event_type"]
        self.location = kwargs["location"]
        super().__init__(timeout=kwargs["timeout_duration"])

    @discord.ui.button(label=f"Cancel Event", style=discord.ButtonStyle.red)
    async def test_1(self, inter: discord.Interaction, button: discord.ui.Button):
        await inter.response.send_message('Running test_button 1...')
        self.stop()

    @discord.ui.button(label=f"Start Event", style=discord.ButtonStyle.green) # start/end
    async def test_2(self, inter: discord.Interaction, button: discord.ui.Button):
        await inter.response.send_message('Running test_button 2', ephemeral=True)
        self.stop()
        
    @discord.ui.button(label="Send Event Log", style=discord.ButtonStyle.primary)
    async def test_3(self, inter: discord.Interaction, button: discord.ui.Button):
        event_log_channel_id = config_data["guild-settings"][f"{inter.guild.id}"]["event_log_channel"]
        event_log_channel = self.bot.fetch_channel(event_log_channel_id)
        
        embedvar = discord.Embed(
            title=f"{self.event_type} Log",
            description=f"## Description\nDuration: BLANK\nLocation: {self.location}\nAttendees: {self.attendees}\n\nNotes:\nBLANK",
            color=discord.Color.blue(),
            timestamp=datetime.now(),
        )

        await inter.response.send_message(f"Sent event log to: {event_log_channel.name}", ephemeral=true)
        self.stop()

class ShiftSystem():
    def __init__(self, inter):
        self.start_time = self.total_time = self.time_elapsed = 0
        self.time_between_breaks = []
        self.inter = inter
        self.guild = self.inter.guild

    async def start(self):
        self.start_time = datetime.datetime.now().timestamp()
        await edit(SAVE, self.guild.id, "shift_status", "id", self.inter.user.id, 1) # no true/false in sql, use 1/0

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

        shift_time = await load(SAVE, self.guild.id, "shift_duration_seconds", "id", self.inter.user.id)
        shift_amount = await load(SAVE, self.guild.id, "shift_amount", "id", self.inter.user.id)

        await edit(SAVE, self.guild.id, "shift_duration_seconds", "id", self.inter.user.id, shift_time+self.total_time)
        await edit(SAVE, self.guild.id, "shift_amount", "id", self.inter.user.id, shift_amount+1)
        await edit(SAVE, self.guild.id, "shift_status", "id", self.inter.user.id, 0)


async def setup(bot):
    ext = Events(bot=bot)
    ext.description = "A sub-section of the bot consisting of events that are useful for a certain faction."
    await bot.add_cog(ext)
