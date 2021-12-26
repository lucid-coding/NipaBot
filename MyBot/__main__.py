import aiosqlite
from random import randint, choice
import os
from disnake.colour import Colour
from disnake.ext.commands.help import HelpCommand
from dotenv import load_dotenv

from MyBot.utils import banner
from MyBot.log import setup
from MyBot.utils.constants import DATABASE
from MyBot.utils.paginator import EmbedPaginator

from disnake.ext.commands.errors import ExtensionAlreadyLoaded
from disnake.ext import commands, tasks
import disnake



intents = disnake.Intents.default()
intents.members = True
intents.voice_states = True
bot = commands.Bot(
    command_prefix=commands.when_mentioned_or('!'), 
    activity=disnake.Game(name="Command !help"), 
    case_insensitive=True,
    intents=intents,
    sync_commands_debug=True)


from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())
TOKEN = os.getenv('DISCORD_TOKEN')

import disnake
from disnake import ui
from disnake.ext import menus
from itertools import starmap

class MyMenuPages(ui.View, menus.MenuPages):
    def __init__(self, source, *, delete_message_after=False):
        super().__init__(timeout=60)
        self._source = source
        self.current_page = 0
        self.ctx = None
        self.message = None
        self.delete_message_after = delete_message_after

    async def start(self, ctx, *, channel=None, wait=False):
        # We wont be using wait/channel, you can implement them yourself. This is to match the MenuPages signature.
        await self._source._prepare_once()
        self.ctx = ctx
        self.message = await self.send_initial_message(ctx, ctx.channel)

    async def _get_kwargs_from_page(self, page):
        """This method calls ListPageSource.format_page class"""
        value = await super()._get_kwargs_from_page(page)
        if 'view' not in value:
            value.update({'view': self})
        return value

    async def interaction_check(self, interaction):
        """Only allow the author that invoke the command to be able to use the interaction"""
        return interaction.user == self.ctx.author

    @ui.button(label='≪', style=disnake.ButtonStyle.grey)
    async def first_page(self, button, interaction):
        await self.show_page(0)

    @ui.button(label='Back', style=disnake.ButtonStyle.blurple)
    async def before_page(self, button, interaction):
        await self.show_checked_page(self.current_page - 1)

    @ui.button(label='Quit', style=disnake.ButtonStyle.red)
    async def stop_page(self, button, interaction):
        self.stop()
        if self.delete_message_after:
            await self.message.delete(delay=0)

    @ui.button(label='Next', style=disnake.ButtonStyle.blurple)
    async def next_page(self, button, interaction):
        await self.show_checked_page(self.current_page + 1)

    @ui.button(label='≫', style=disnake.ButtonStyle.grey)
    async def last_page(self, button, interaction):
        await self.show_page(self._source.get_max_pages() - 1)

class HelpPageSource(menus.ListPageSource):
    def __init__(self, data, helpcommand):
        super().__init__(data, per_page=6)
        self.helpcommand = helpcommand

    def format_command_help(self, no, command):
        signature = self.helpcommand.get_command_signature(command)
        docs = self.helpcommand.get_command_brief(command)
        return f"{no}. {signature}\n{docs}"
    
    async def format_page(self, menu, entries):
        page = menu.current_page
        max_page = self.get_max_pages()
        starting_number = page * self.per_page + 1
        iterator = starmap(self.format_command_help, enumerate(entries, start=starting_number))
        page_content = "\n".join(iterator)
        embed = disnake.Embed(
            title=f"Help Command[{page + 1}/{max_page}]", 
            description=page_content,
            color=disnake.Colour.red()
        )
        author = menu.ctx.author
        embed.set_footer(text=f"Requested by {author}", icon_url=author.avatar.url)  # author.avatar in 2.0
        return embed

from itertools import chain

class MyHelp(commands.MinimalHelpCommand):
    def get_command_brief(self, command):
        return command.short_doc or "Command is not documented."
    
    async def send_bot_help(self, mapping):
        all_commands = list(chain.from_iterable(mapping.values()))
        formatter = HelpPageSource(all_commands, self)
        menu = MyMenuPages(formatter, delete_message_after=True)
        await menu.start(self.context)

bot.help_command = MyHelp()




@bot.event 
async def on_ready():
    """Creating additional database stuff if needed"""
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("CREATE TABLE IF NOT EXISTS reminders (guild_id INTEGER, user_id INTEGER, channel_id INTEGER, message_id INTEGER, expire INTEGER)")
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
    if folder.endswith('.py') and not folder.startswith("__"):
        #bot.load_extension(f"MyBot.cogs.moderation.{folder[:-3]}")
        ext.append(f"MyBot.cogs.moderation.{folder[:-3]}")
    else:
        continue
 
    for subfolder in os.listdir('MyBot/cogs/other'):
        if subfolder.endswith('.py') and not subfolder.startswith("__"):
            #bot.load_extension(f"MyBot.cogs.other.{subfolder[:-3]}")
            ext.append(f"MyBot.cogs.other.{subfolder[:-3]}")
        else:
            continue
        #for filename in os.listdir('MyBot/cogs/other/music'):
        #    if filename.endswith('.py') and not filename.startswith("__"):
        #        bot.load_extension(f"MyBot.cogs.other.music.{filename[:-3]}")
        #        ext.append(f"MyBot.cogs.other.music.{filename[:-3]}")
if __name__ == '__main__':
    setup()
    #extensions = ['MyBot.cogs.moderation.admins', 'MyBot.cogs.moderation.general', 'MyBot.cogs.other.default', 'MyBot.cogs.moderation.warnings', 'MyBot.cogs.other.event', 'MyBot.cogs.moderation.dm', 'MyBot.cogs.moderation.config', 'MyBot.cogs.moderation.defcon', 'MyBot.cogs.other.bonker', 'MyBot.cogs.other.logs']
    try:
        bot.load_extension("MyBot.cogs.other.slashes")
        bot.load_extension("MyBot.cogs.moderation.general")
        for extension in ext:
            bot.load_extension(extension)
    except ExtensionAlreadyLoaded as e:
        print(e)
        #bot.unload_extension(extension)
    bot.run(TOKEN)
    
