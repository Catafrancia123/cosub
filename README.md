![Version](https://img.shields.io/badge/version-0.2.1--dev2-blue?style=plastic)
![Python Versions](https://img.shields.io/badge/python-3.12%20%7C%203.13%20%7C%203.14%20-blue?style=plastic)
[![Discord](https://img.shields.io/discord/990326151987724378?logo=discord&logoColor=white&color=5865F2)](https://discord.gg/BHUxXKwTfA) 

# cosub
cosub (short for Catamapp's Open Source Utilities Bot) is a open source discord utilities bot for servers that have a sort of work enviroment and wanted a easy to configure bot.

This is a open source, discord general utilities bot for factions and more. The bot can be used to manage shifts, host trainings and even add points while topped off with a bit of humor. This bot is open to contributions, just fork the repo and once the changes are done, make a pull request and i will check it.
> [!NOTE]
> The bot isn't fully completed yet, there are many commands to add or even debug. Also, this is the dev branch, expect lots of errors.
# Download
## Prerequesites/Dependencies
What you need to run the bot is the newest Python version (3.12+), find [here](https://python.org "Official Python Website"). And some third party packages listed below:

> [!NOTE]
> Why 3.12+? Because we had some features that require Python version 3.12 above: [f-string rework](https://peps.python.org/pep-0701/ "PEP 701")

- `discord.py` - This is what discord package the bot runs on.
- `rich` (local) - This adds colors and many other stuff you cant do in basic python.
- `playsound3` (local) - This plays a sound to alert you that the bot is ready.
- `asqlite` (database) - This is the database the bot is going to be using.
- `toml` (config) - This is for writing and reading the `toml` config file and used in guild settings. 
- `jishaku` (misc) - Bot extension for bot statistics, etc.

> [!NOTE]
> The packages with `(local)` tag have to be installed to prevent any errors (i just used them to make your command line look better lol - catamapp).

If you want to install these packages fast, run `pip install -r requirements.txt`

# Running The Bot
## Setup
Before running the bot, you need a `config.toml` file as the config for the bot with the code below:

> [!NOTE]
> Please copy the whole file entirely without deleting/ignoring a single thing.
```toml
title = "Config file"

[bot-settings]
# local_username is your username, defaults to admin.
local_username = "admin"
# self explanatory
bot_token = "insert_discord_bot_token"
# loaded_modules is a development config if you want to specify the modules loaded. (FOR ALL SERVERS)
loaded_modules = ["maintenance", "humor", "settings"]

[guild-settings]
# admin roles are the roles that have administrator/moderator permissions (FOR ALL SERVERS)
admin_roles = [128880188670686008, 1378763072357011566]

# server-name is your server name, with a few adjustments:
# 1. Make sure every letter is in lowercase.
# 2. Names with spaces will be changed by dashes (-): bot test -> bot-test
# 3. Names with colons (:), change to a dash (-): TNO: Discord Server -> tno--discord-server
[guild-settings.server-name]
# member_role is the role id of a "member" role. Defaults to 0
member_role = 0
# startup_channel is an optional channel id for bot status. Defaults to 0
startup_channel = 0
# faction is the activation of certain extensions (deployments, training, points, etc.) if your discord server is a faction. Defaults to false.
faction = false
```

## Running it
Run the `main.py` file and wait for the setup process to complete. Once you hear a *beep* sound, it's ready to use.
You can monitor the bot via the command line for errors and events.
Also, check the two log files (`bot.log`, `error.log`) to monitor the bot's information and errors.
