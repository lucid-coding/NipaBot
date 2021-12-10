from MyBot.utils.constants import DATABASE
import aiosqlite
import disnake
from random import randint, choice
from disnake.ext import commands, tasks
import os
from dotenv import load_dotenv
from MyBot.utils import banner
from MyBot.log import setup
from disnake.ext.commands.errors import ExtensionAlreadyLoaded

intents = disnake.Intents.default()
intents.members = True
intents.voice_states = True
bot = commands.Bot(
    command_prefix=commands.when_mentioned_or('.'), 
    activity=disnake.Game(name="Command !help"), 
    case_insensitive=True,
    intents=intents,
    sync_commands_debug=True)


from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
TOKEN = os.getenv('DISCORD_TOKEN')

class MyNewHelp(commands.MinimalHelpCommand):
    """Bots help command class"""
    async def send_pages(self):
        
        destination = self.get_destination()
        for page in self.paginator.pages:
            emby = disnake.Embed(description=page)
            await destination.send(embed=emby)

bot.help_command = MyNewHelp()

@bot.event 
async def on_ready():
    """Creating additional database stuff if needed"""
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("CREATE TABLE IF NOT EXISTS messages (username STR, userid INTEGER, time INTEGER)")
        await db.execute("CREATE TABLE IF NOT EXISTS warnings (Username STR, Userid INTEGER, mod STR, modId INTEGER, reason STR)")
        await db.execute("CREATE TABLE IF NOT EXISTS log (guild_id INTEGER, user_name STR, user_id INTEGER, time INTEGER, content STR)")
        await db.execute("CREATE TABLE IF NOT EXISTS rolecontrol (guild_id INTEGER, user_id INTEGER, role INTEGER, expire INTEGER)")
        await db.execute("CREATE TABLE IF NOT EXISTS infractions (guild_id INTEGER, mute_id INTEGER, user_name STR, user_id INTEGER, apply_time INTEGER, expire INTEGER)")
        await db.commit()
        
    print(f"I am online!\nUsername:{bot.user.name}\n version 2.0 Development started at: '3/19/2021'") 

#loading the cogs
ext = []

for folder in os.listdir('MyBot/cogs/moderation'):
    if folder.endswith('.py'):
        ext.append(f"MyBot.cogs.moderation.{folder[:-3]}")

    for subfolder in os.listdir('MyBot/cogs/other'):
        if subfolder.endswith('.py'):
            ext.append(f"MyBot.cogs.other.{subfolder[:-3]}")
        
        for filename in os.listdir('MyBot/cogs/other/music'):
            if filename.endswith('.py'):
                ext.append(f"MyBot.cogs.other.music.{filename[:-3]}")

if __name__ == '__main__':
    setup()
    #extensions = ['MyBot.cogs.moderation.admins', 'MyBot.cogs.moderation.general', 'MyBot.cogs.other.default', 'MyBot.cogs.moderation.warnings', 'MyBot.cogs.other.event', 'MyBot.cogs.moderation.dm', 'MyBot.cogs.moderation.config', 'MyBot.cogs.moderation.defcon', 'MyBot.cogs.other.bonker', 'MyBot.cogs.other.logs']
    try:
        bot.load_extension("MyBot.cogs.other.slashes")
        for extension in ext:
            bot.load_extension(extension)
    except ExtensionAlreadyLoaded as e:
        print(e)
        #bot.unload_extension(extension)
    bot.run(TOKEN)
    
