#! This schema is under development, do not use it yet.

import time, datetime
from schemas.saveloader import edit, add, load

SAVE = "save.db"

class ShiftSystem():
    def __init__(self, interaction):
        global start, end, paused, paused_dur, time_elapsed
        self.interaction = interaction

    async def start(self):
        guild_name = self.interaction.guild.name.replace(" ", "_")
        start = time.time()

        cur_amount = await load(SAVE, guild_name, "shifts") 
        await edit(SAVE, guild_name, "shifts", cur_amount+1)

    async def end(self):
        guild_name = self.interaction.guild.name.replace(" ", "_")
        total_time = time.time() - start
        time_elapsed = datetime.timedelta(seconds=int(total_time)) 

        cur_amount = await load(SAVE, guild_name, "shift_duration_seconds") 
        await edit(SAVE, guild_name, "shift_duration_seconds", cur_amount+total_time)
