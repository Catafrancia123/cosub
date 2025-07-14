![Version](https://img.shields.io/badge/version-0.1.0-blue?style=plastic) [![Discord](https://img.shields.io/discord/990326151987724378?logo=discord&logoColor=white&color=5865F2)](https://discord.gg/BHUxXKwTfA) 
# cosub
cosub (short for Catamapp's Open Source Utilities Bot) is a open source discord utilities bot for servers that have a sort of work enviroment and wanted a easy to configure bot.

This is a open source, discord general utilities bot for factions and more. The bot can be used to manage shifts, host trainings and even add points while topped off with a bit of humor. This bot is open to contributions, just fork the repo and once the changes are done, make a pull request and i will check it.
> [!NOTE]
> The bot isn't fully completed yet, there are many commands to add or even debug. Also, this is the dev branch, expect lots of errors.
# Download
## Prerequesites/Dependencies
What you need to run the bot is the newest Python version, find [here](https://python.org "Official Python Website"). And some third party packages listed below:

- `discord.py` - This is what discord package the bot runs on.
- `rich` (local) - This adds colors and many other stuff you cant do in basic python.
- `playsound3` (local) - This plays a sound to alert you that the bot is ready.
- `python-dotenv` (local) - This is for loading a enviroment file for the discord token.
- `asqlite` (database) - This is the database the bot is going to be using.
- `jishaku` (misc) - Library for bot statistics, etc.

> [!NOTE]
> The packages with `(local)` tag have to be installed to prevent any errors in the file (i just used them to make your command line look better lol - catamapp).

If you want to install these packages fast, run the `requirements.txt` file.
`pip install -r requirements.txt`

# Running The Bot
## Setup
Before running the bot, you need a `config.toml` file as the config for the bot, with the code below:
```toml
title = "Config file"

[bot-settings]
bot_token="insert_bot_token"

[guild-settings]
admin_roles = [128880188670686008, 1378763072357011566, ...]
```

## Running it
Run the `main.py` file and wait for the setup process to complete. Once you hear a *beep* sound, it's ready to use.
You can monitor the bot via the command line for errors and events.
Also, check the two log files (`bot.log`, `error.log`) to monitor the bot's information and errors.
