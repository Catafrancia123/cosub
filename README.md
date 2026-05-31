![Version](https://img.shields.io/badge/version-0.2.2--dev2-blue?style=plastic)
![Python Versions](https://img.shields.io/badge/python-3.12%20%7C%203.13%20%7C%203.14%20-blue?style=plastic)
[![Discord](https://img.shields.io/discord/990326151987724378?logo=discord&logoColor=white&color=5865F2)](https://discord.gg/BHUxXKwTfA) 

# cosub
cosub (short for Catamapp's Open Source Utilities Bot) is a open source discord utilities bot for servers that have a sort of work enviroment and wanted a easy to configure bot.

This is a open source, discord general utilities bot for factions and more. The bot can be used to manage shifts, host trainings and even add points while topped off with a bit of humor. This bot is open to contributions, just fork the repo and once the changes are done, make a pull request and i will check it.
> [!NOTE]
> The bot isn't fully completed yet, there are many commands to add or even debug.
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
# local_username is your local alias for the bot, defaults to admin.
local_username = "admin"
# self explanatory
bot_token = "insert_discord_bot_token"
# loaded_modules is a development config if you want to specify the modules loaded. (FOR ALL SERVERS)
loaded_modules = ["maintenance", "humor", "settings"]
# send_startup_message is a bot config whether or not to send a bot status messaage to the respective server's log channels. (FOR ALL SERVERS)
send_startup_message = true
```

## Server Setup
In order to run the bot normally, you must fill out a form of server information. The form can be accessed by running the command `/setup`. In which it should show like this:

<img width="583" height="147" alt="image" src="https://github.com/user-attachments/assets/e589bfa2-799a-4217-a6cb-6b14e8030251" />

To get the emoji id: [here](https://support.discord.com/hc/en-us/community/posts/360069335891-Get-Emoji-ID)
To enable the special faction-based commands, tick the "Is a faction?" checkbox and proceed by pressing another button:

<img width="409" height="140" alt="image" src="https://github.com/user-attachments/assets/f6e9994d-1e9e-4d05-bd87-48dc8a3cf7ba" />

## Integrations
The responsibility of the usage of commands is relied on the server itself. So, once you have done `/setup`, follow these steps to enable integrations:
### Step 1: Go to Server Settings
<img width="960" height="540" alt="setup_1" src="https://github.com/user-attachments/assets/4b160718-52e0-4b23-b0d7-10bfd432c780" />

### Step 2: Go to the Integrations Tab
<img width="960" height="540" alt="setup_2" src="https://github.com/user-attachments/assets/047119ba-235f-48dd-9a91-a49cd10267ee" />

### Step 3: Go find the bot (mine is COSUB here)
<img width="960" height="540" alt="setup_3" src="https://github.com/user-attachments/assets/de220f8f-4959-4c25-8e4b-3639999896e1" />

### Step 4: Edit the usage of commands to be only used by a certain role, user or channel. 
The top part means the entire bot can only be used in a certain channel or user or role, while the bottom part with commands is used for certain commands to be used in a certain channel or user or role.
<img width="960" height="540" alt="setup_4" src="https://github.com/user-attachments/assets/f7a01327-b2a7-4a5c-a15d-de63a1c42191" />

## Running it
Run the `main.py` file and wait for the setup process to complete. Once you hear a *beep* sound, it's ready to use.
You can monitor the bot via the command line for errors and events.
Also, check the two log files (`bot.log`, `error.log`) to monitor the bot's information and errors.
