#! This schema is under development, do not use it yet.

import time, datetime
from schemas.saveloader import edit, load

SAVE = "save.db"

class ShiftSystem():
    def __init__(self, interaction):
        self.start_time = self.total_time = self.time_elapsed = 0
        self.interaction = interaction
        self.guild_name = self.interaction.guild.name.replace(" ", "_")

    async def start(self):
        self.start_time = time.time()

        cur_amount = await load(SAVE, self.guild_name, "shifts") 
        await edit(SAVE, self.guild_name, "shifts", cur_amount+1)

    async def end(self):
        self.total_time = time.time() - self.start_time
        self.time_elapsed = datetime.timedelta(seconds=int(self.total_time)) 

        cur_amount = await load(SAVE, self.guild_name, "shift_duration_seconds") 
        await edit(SAVE, self.guild_name, "shift_duration_seconds", cur_amount+self.total_time)
