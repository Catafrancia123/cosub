import discord, toml, time
from datetime import datetime
from discord.ext import commands
from schemas.saveloader import check_table, add, edit, load, check_data
from schemas.functions import Functions
import discord.ui as UI
import discord.app_commands as app_commands

with open("config.toml", "r") as config:
    config_data = toml.load(config)
    in_testing = config_data["bot_settings"]["in_testing"]
SAVE = "save.db"
    
async def is_faction_check(inter: discord.Interaction):
    check = await load(SAVE, "server_info", "is_faction", "server_id", inter.guild.id)
    match check:
        case 1: return True
        case 0 | None: return False

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.check(is_faction_check)
    @app_commands.command(description="Hosts an event of a specific type")
    async def event(self, inter: discord.Interaction):
        await inter.response.send_modal(MakeEventForm(self.bot))

class EventReactionButtons(UI.View):
    def __init__(self, *args, **kwargs):
        super().__init__(timeout=None)
        self.bot = kwargs["bot"]
        self.data = kwargs["data"]

    @UI.select(placeholder="Select attendance options:", row=1, options=[discord.SelectOption(label="Attend", value=1), discord.SelectOption(label="Un-attend", value=0)])
    async def selection(self, inter: discord.Interaction, select: UI.Select):
        value = int(select.values[0])
        if value == 1:
            self.data["attendees"].append(inter.user.id)           
            await inter.response.send_message("You have been logged to willingly attend the event, please do not forget and remember:\n`You react, you attend.`\nIf you can't attend for any reason in the future, before the event happens, press the button again, and select `Un-attend`.", ephemeral=True)
        elif value == 0:
            self.data["attendees"].remove(inter.user.id)
            await inter.response.send_message("You have un-attended from the event, you are now free from the obligation to join it.", ephemeral=True)

        attendees = ""
        if self.data["attendees"]:
            for user_id in self.data["attendees"]:
                attendees += f"<@{user_id}>, "
        else:
            attendees = "N/A"
        embedvar = discord.Embed(
            description=f"## {self.data['event_type']}\nTime: <t:{self.data['time']}:f>, <t:{self.data['time']}:R>\nLocation: {self.data['location']}\nAttendees: {attendees}\n\n{self.data['notes']}",
            color=discord.Color.blue(),
            timestamp=datetime.now(),
        )
        embedvar.set_footer(text=f"ID: {self.bot.interaction_id}")
        embedvar.set_author(name=f"Host: {inter.user.name}\nCo-host(s): {','.join(self.data['co_host'])}", icon_url=inter.user.avatar.url)
        try:
            icon = inter.guild.icon.url
        except AttributeError:
            icon = self.bot.user.avatar.url
        embedvar.set_thumbnail(url=icon)
        ui_buttons = EventReactionButtons(bot=self.bot,data=self.data)
        await inter.message.edit(embed=embedvar, view=ui_buttons)
        await self.wait()

class EventManagementButtons(UI.View):
    def __init__(self, *args, **kwargs):
        super().__init__(timeout=None)
        self.bot = kwargs["bot"]
        self.data = kwargs["data"]
    
    @UI.button(label=f"Start Event", style=discord.ButtonStyle.green) # start
    async def event_status(self, inter: discord.Interaction, button: UI.Button):
        message = await inter.channel.fetch_message(inter.channel.last_message_id)
        system = ShiftSystem()
        time = round(datetime.now().timestamp())
       
        self.bot.logger.info(f"BOT LOG: reactions = {message.reactions}")
        attendees = len(self.data["attendees"])
        if attendees <= 2 and not in_testing: 
            await inter.response.send_message("The event hasn't reached its minimal reaction count.\nAtleast 2 people including the host are required to react to start the event.", ephemeral=True)
            return 

        self.data["status"] = True
        ui_buttons = EventEndButtons(
            bot=self.bot,
            data=self.data,
            timeout_duration=14400,
            shift_system=system,
        )
        
        attendees = ""
        if self.data["attendees"]:
            for i, user_id in enumerate(self.data["attendees"]):
                if i == len(self.data["attendees"]):
                    attendees += f"<@{user_id}>"
                else:
                    attendees += f"<@{user_id}>, "
                self.bot.logger.info(f"BOT LOG: {i} {len(self.data['attendees'])}")
        else:
            attendees = "N/A"
        embedvar = discord.Embed(
            description=f"## {self.data['event_type']} Started\nStarted at: <t:{time}:f>\nLocation: {self.data['location']}\nAttendees: {attendees}\n\n{self.data['notes']}",
            color=discord.Color.green(),
            timestamp=datetime.now(),
        )
        embedvar.set_footer(text=f"ID: {self.bot.interaction_id}")
        embedvar.set_author(name=f"Host: {inter.user.name}\nCo-host(s): {','.join(self.data['co_host'])}", icon_url=inter.user.avatar.url)
        try:
            icon = inter.guild.icon.url
        except AttributeError:
            icon = self.bot.user.avatar.url
        embedvar.set_thumbnail(url=icon)

        system.start()
        await inter.response.send_message("Event started.", ephemeral=True)
        await message.edit(embed=embedvar, view=ui_buttons)
        await self.wait()

    @UI.button(label=f"Cancel Event", style=discord.ButtonStyle.red)
    async def event_cancel(self, inter: discord.Interaction, button: UI.Button):
        #event_log_channel_id = config_data["guild-settings"][f"{inter.guild.id}"]["event_log_channel"]
        #event_log_channel = await self.bot.fetch_channel(event_log_channel_id)
        time = round(datetime.now().timestamp())
        embedvar = discord.Embed(
            description=f"## {self.data['event_type']} Canceled\nCanceled at: <t:{time}:f>\n\nThis {self.data['event_type']} has been canceled.",
            color=discord.Color.red(),
            timestamp=datetime.now(),
        )
        embedvar.set_footer(text=f"ID: {self.bot.interaction_id}")
        embedvar.set_author(name=f"Host: {inter.user.name}\nCo-host(s): {','.join(self.data['co_host'])}", icon_url=inter.user.avatar.url)
        try:
            icon = inter.guild.icon.url
        except AttributeError:
            icon = self.bot.user.avatar.url
        embedvar.set_thumbnail(url=icon)

        await inter.response.send_message('Event canceled.', ephemeral=True)
        await inter.message.edit(embed=embedvar)
        self.stop()
        
    @UI.button(label="Edit Event", style=discord.ButtonStyle.primary)
    async def edit_event(self, inter: discord.Interaction, button: UI.Button):
        await inter.response.send_modal(EditEventForm(bot=self.bot, data=self.data))
        await self.wait()

class EventEndButtons(UI.View):
    def __init__(self, *args, **kwargs):
        super().__init__(timeout=None)
        self.bot = kwargs["bot"]
        self.data = kwargs["data"]
        self.system = kwargs["shift_system"]
        self.duration = 0

    @UI.button(label=f"End Event", style=discord.ButtonStyle.red) # end
    async def event_status(self, inter: discord.Interaction, button: UI.Button):
        time = round(datetime.now().timestamp())
        
        attendees = ""
        if self.data["attendees"]:
            for i, user_id in enumerate(self.data["attendees"]):
                if i == len(self.data["attendees"]):
                    attendees += f"<@{user_id}>"
                else:
                    attendees += f"<@{user_id}>, "
                self.bot.logger.info(f"BOT LOG: {i} {len(self.data['attendees'])}")
        embedvar = discord.Embed(
            description=f"## {self.data['event_type']} Ended\nEnded at: <t:{time}:f>\nLocation: {self.data['location']}\nAttendees: {attendees}\n\nThis {self.data['event_type']} has ended.",
            color=discord.Color.red(),
            timestamp=datetime.now(),
        )
        embedvar.set_footer(text=f"ID: {self.bot.interaction_id}")
        embedvar.set_author(name=f"Host: {inter.user.name}\nCo-host(s): {','.join(self.data['co_host'])}", icon_url=inter.user.avatar.url)
        try:
            icon = inter.guild.icon.url
        except AttributeError:
            icon = self.bot.user.avatar.url
        embedvar.set_thumbnail(url=icon)

        self.data["duration"] = self.system.end()
        await inter.response.send_message("Event Ended.", ephemeral=True)
        await inter.message.edit(embed=embedvar)
        self.data["status"] = False
        await self.wait()
    
    @UI.button(label="Send Event Log", style=discord.ButtonStyle.primary)
    async def event_log(self, inter: discord.Interaction, button: UI.Button):
        if self.data["status"]: await inter.response.send_message("Event is still ongoing, please press the `End Event` button first to end the event and then press this button again.", ephemeral=True)
        await inter.response.send_modal(EventLogForm(bot=self.bot, data=self.data)) 

class EventLogForm(UI.Modal, title="Event Log Form"):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.bot = kwargs["bot"]
        self.data = kwargs["data"]
        self.proof = UI.Label(text="Proof of event (in image form)", component=UI.FileUpload(required=True))
        self.notes = UI.Label(text="Event Remarks/Notes", component=UI.TextInput(style=discord.TextStyle.paragraph, placeholder=f"The {self.data['event_type']} went smoothly.", required=False)) # notes

        self.all = [self.notes, self.proof]
        for i in self.all: self.add_item(i)

    async def on_submit(self, inter: discord.Interaction):
        event_log_channel_id = await load(SAVE, "server_info", f"{self.data['event_type'].lower()}_log_channel", "server_id", inter.guild.id)
        event_log_channel = await self.bot.fetch_channel(event_log_channel_id)

        # Count stuff
        attendees = ""
        if self.data["attendees"]:
            for i, user_id in enumerate(self.data["attendees"]):
                if i == len(self.data["attendees"]):
                    attendees += f"<@{user_id}>"
                else:
                    attendees += f"<@{user_id}>, "
                self.bot.logger.info(f"BOT LOG: {i} {len(self.data['attendees'])}")
        else:
            attendees = "N/A"

        remarks = self.notes.component.value
        embedvar = discord.Embed(
            description=f"## {self.data['event_type']} Log\nDuration: {self.data['duration']}\nLocation: {self.data['location']}\nAttendees: {attendees}\n\nNotes:\n{remarks}",
            color=discord.Color.blue(),
            timestamp=datetime.now(),
        )
        embedvar.set_footer(text=f"ID: {self.bot.interaction_id}")
        embedvar.set_author(name=f"Host: {inter.user.name}\nCo-host(s): {','.join(self.data['co_host'])}", icon_url=inter.user.avatar.url)
        try:
            icon = inter.guild.icon.url
        except AttributeError:
            icon = self.bot.user.avatar.url
        embedvar.set_thumbnail(url=icon)
    
        files = self.proof.component.values
        for i, att in enumerate(files):
            files[i] = await att.to_file()
        message = await event_log_channel.send(embed=embedvar)
        message_id = message.id
        await event_log_channel.send("Proof:", files=files)
        
        log_text = f"https://discord.com/channels/{inter.guild.id}/{event_log_channel.id}/{message_id}"
        await inter.response.send_message(f"Sent event log to: {log_text}", ephemeral=True)

class EditEventForm(UI.Modal, title="Edit Event"):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.bot = kwargs["bot"]
        self.data = kwargs["data"]
        self.time = UI.Label(text="Time (in unix time, eg. 1778760000)", component=UI.TextInput(required=False)) # time
        self.co_host = UI.Label(text="Co-host", component=UI.UserSelect(placeholder="N/A", max_values=3, row=4)) # channel (optional)

        self.all = [self.co_host, self.time]
        for i in self.all: self.add_item(i)

    async def on_submit(self, inter: discord.Interaction):
        try: co_host = [i.name for i in self.co_host.component.values]
        except Exception: co_host = ["N/A"]
        if not self.time.component.value:
            time = data['time']
        else:
            time = int(self.time.component.value)
        embedvar = discord.Embed(
            description=f"## {self.data['event_type']}\nTime: <t:{time}:f>, <t:{time}:R>\nLocation: {self.data['location']}\n\n{self.data['notes']}",
            color=discord.Color.blue(),
            timestamp=datetime.now(),
        )
        embedvar.set_footer(text=f"ID: {self.bot.interaction_id}")
        embedvar.set_author(name=f"Host: {inter.user.name}\nCo-host(s): {', '.join(co_host)}", icon_url=inter.user.avatar.url)
        try:
            icon = inter.guild.icon.url
        except AttributeError:
            icon = self.bot.user.avatar.url
        embedvar.set_thumbnail(url=icon)

        await inter.response.send_message("Sucessfully edited event.", ephemeral=True)
        await inter.message.edit(embed=embedvar)

class MakeEventForm(UI.Modal, title="Create Event"):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.event_selections = ["Deployment", "Training", "Tryout"]
        self.base_datetime = round(datetime.now().timestamp())

        self.event_type = UI.Label(text="Event Type", component=UI.Select(options=[discord.SelectOption(label=i, value=i) for i in self.event_selections], placeholder="Select event type:", row=1, required=True)) # event type
        self.time = UI.Label(text="Time (in unix time, eg. 1778760000)", component=UI.TextInput(placeholder="Enter the time here in unix format!")) # time (advanced)
        self.location = UI.Label(text="Location of the Event", component=UI.TextInput(placeholder="Site-45")) # location
        self.notes = UI.Label(text="Event Notes/Instructions", component=UI.TextInput(style=discord.TextStyle.paragraph, placeholder="Join up and say !WPCO in radio!")) # notes

        self.all = [self.event_type, self.time, self.location, self.notes]
        for i in self.all: self.add_item(i)

    async def on_submit(self, inter: discord.Interaction):
        data = {
            "event_type": self.event_type.component.values[0], 
            "time": int(self.time.component.value),
            "location": self.location.component.value,
            "notes": self.notes.component.value,
            "co_host": ["N/A"],
            "attendees": [],
        }
       
        member_role = await load(SAVE, "server_info", "member_role", "server_id", inter.guild.id)
        if member_role == 0: 
            member_role = "@here"
        else: 
            member_role = f"<@&{member_role}>"
        reaction_buttons = EventReactionButtons(bot=self.bot,data=data)
        management_buttons = EventManagementButtons(bot=self.bot, data=data)
        embedvar = discord.Embed(
            description=f"## {data['event_type']}\nTime: <t:{data['time']}:f>, <t:{data['time']}:R>\nLocation: {data['location']}\nAttendees: N/A\n\n{data['notes']}",
            color=discord.Color.blue(),
            timestamp=datetime.now(),
        )
        embedvar.set_footer(text=f"ID: {self.bot.interaction_id}")
        embedvar.set_author(name=f"Host: {inter.user.name}\nCo-host(s): N/A", icon_url=inter.user.avatar.url)
        try:
            icon = inter.guild.icon.url
        except AttributeError:
            icon = self.bot.user.avatar.url
        embedvar.set_thumbnail(url=icon)
        await inter.response.send_message(f"Sent event message. Adjust your deployment settings below.", ephemeral=True, view=management_buttons) # after this use followup!
        await inter.followup.send(f"{member_role}", embed=embedvar, view=reaction_buttons)

class ShiftSystem():
    def __init__(self):
        self.start_time = self.total_time = self.time_elapsed = 0
        self.time_between_breaks = []

    def start(self):
        self.start_time = time.monotonic()

    def shift_break(self, status: bool): # status is whether you are doing a break/continuing 
        if status == True:
             self.time_between_breaks.append(time.monotonic() - self.start_time)
        elif status == False:
            self.start_time = time.monotonic()

    def end(self) -> int:
        self.total_time = round(time.monotonic() - self.start_time)
        for break_time in self.time_between_breaks:
            self.total_time += break_time

        hours, remainder = divmod(self.total_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        formatted = '{:02} hour(s), {:02} minute(s), {:02} second(s)'.format(int(hours), int(minutes), int(seconds))
        return formatted


async def setup(bot):
    ext = Events(bot=bot)
    ext.description = "A sub-section of the bot consisting of events that are useful for a certain faction."
    await bot.add_cog(ext)
