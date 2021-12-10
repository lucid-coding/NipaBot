# Nipa-bot
My simple Discord bot made in python using disnake

# Bot

To start using the bot, you need to setup it. First start by making an application at the [Discord developer portal](https://discord.com/developers/applications/). To application **remember to turn intents on**.

### Permissions
What permissions bot needs to work? To be honest I'm not 100% sure what all it needs. But atleast these are recommended: 
![Image link](https://github.com/Nipa-Code/Python-projects-list/blob/main/perms.png)

### Code setup
You may see file called config.yaml, there you need to set few role id's and channel id's. 
After that is done go to constants.py and add the location of few files, so the bot can use them.

### Running Bot
After finishing the steps above, you are ready to run bot
Run the bot by running: **python -m MyBot** , run command on terminal at directory where MyBot locates at.

# FEATURES
Mainly used for moderation, has abilities to **silence/lock** current channel temporary, **moderate users**, **keep track on bot DM's** that user(s) sent, **warn** them. Bot can also send memes!

## NOTE:

Do **NOT** change the folder (MyBot) to anything, otherwise you need to change a lot more imports and few other things.
Bot **is not** suitable for big servers.

## DATABASE

Bot uses **SQLite** as database to store infractions. Also used to some random stuff. **Bot creates the database tables automatically**, 
