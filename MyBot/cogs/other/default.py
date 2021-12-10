import disnake
from disnake.ext import commands
from disnake.errors import InvalidArgument
from disnake.ext.commands import clean_content
from disnake.utils import get
from disnake import AllowedMentions, Colour, Embed, Guild, Message, Role
from disnake.utils import escape_markdown

from MyBot.utils.constants import meme
from MyBot.utils.converters import DurationDelta, Duration
from MyBot.utils.factory import ModLog
from MyBot.utils.decorators.deco import restrict_to_user
from MyBot.utils. paginator import EmbedPaginator
import rapidfuzz
import colorsys
import pprint
import textwrap
from collections import defaultdict
from typing import Any, DefaultDict, Mapping, Optional, Tuple, Union

import requests
import os
import random
import inspect
from inspect import getsource
from pathlib import PurePath
import asyncpraw
import time
import asyncio
import logging
from datetime import datetime, timedelta

#statuses 

'''
# Setting `Playing` status
await bot.change_presence(activity=disnake.Game(name="a game"))

# Setting `Streaming` status
await bot.change_presence(activity=disnake.Streaming(name="My Stream", url=my_twitch_url))

# Setting `Listening` status
await bot.change_presence(activity=disnake.Activity(type=disnake.ActivityType.listening, name="a song"))

# Setting `Watching` status
await bot.change_presence(activity=disnake.Activity(type=disnake.ActivityType.watching, name="a movie"))
'''

log = logging.getLogger(__name__)

from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
WEBHOOK_ID = os.getenv('WEBHOOK_ID')

class General(commands.Cog):
    """General commands"""
    def __init__(self, bot):
        self.bot = bot
        self.last_msg = None
        self.modlog = ModLog
        self.webhook = WEBHOOK_URL
        self.webhook_id = WEBHOOK_ID

    @commands.command()
    @restrict_to_user(534738044004335626)
    async def test(self, ctx, member: disnake.Member):    
        content = await self.modlog.send_log_message(
                self, colour=disnake.Color.red(), title=f"{member} | {member.id}", 
                text="Sample text", icon_url=member.display_avatar, 
                footer="Sample footer"
                #thumbnail="Sample thumbnail"
                )

        await ModLog.send_webhook(self, content)

    @commands.command()
    async def test_embed(self, ctx):
        embed1 = disnake.Embed(title="Test embed 1", description="Test description 1")
        embed1.add_field(name="test field 1", value="Test value 1")

        embed2 = disnake.Embed(title="Test embed 2", description="Test description 2")
        embed2.add_field(name="test field 2", value="Test value 2")

        embed3 = disnake.Embed(title="Test embed 3", description="Test description 3")
        embed3.add_field(name="test field 3", value="Test value 3")

        embed4 = disnake.Embed(title="Test embed 4", description="Test description 4")
        embed4.add_field(name="test field 4", value="Test value 4")

        embedss = [embed1, embed2, embed3, embed4]
        a = EmbedPaginator(ctx, embeds=embedss, timeout=180)
        await a.start()


    @commands.command()
    @restrict_to_user(534738044004335626)
    async def create_webhook(self, ctx, name: str):
        """Creates a webhook for a current channel with given name"""
        await ctx.channel.create_webhook(name=name, reason="I don't have permission to create webhook so bot made it")

    @commands.command()
    @restrict_to_user(534738044004335626)
    async def get_webhook(self, ctx):
        """Gets a list of webhooks in current channel"""
        a = await ctx.channel.webhooks()
        await ctx.send(a)

    @commands.command()
    @restrict_to_user(534738044004335626)
    async def webhook_urls(self, ctx):
        """Returns a list of webhook URLs in server"""
        content = "\n".join([f"{w.name} - {w.url}" for w in await ctx.guild.webhooks()])
        await ctx.send(content)

    @commands.command()
    @restrict_to_user(534738044004335626)
    async def send_webhook(self, ctx):
        content = await self.modlog.send_log_message(
            self, colour=disnake.Color.red(), title="Access denied", 
            text="Sample text", icon_url=ctx.author.avtar.url, 
            content="Sample content", footer="Sample footer", ping_everyone=True
            #thumbnail="Sample thumbnail"
            )

    #@commands.command()
    #@commands.cooldown(1, 3)
    #async def join(self, ctx):
    #    '''Will make bot join the current voice channel'''
    #    await ctx.author.voice.channel.connect()
    #    chann = ctx.author.voice.channel
    #    await ctx.guild.change_voice_state(channel=chann, self_deaf=True)

    @commands.command()
    @commands.cooldown(1, 3)
    async def dc(self, ctx):
        '''Will disconnect bot from current voice channel'''
        await ctx.voice_client.disconnect()
    
    @commands.command()
    @commands.cooldown(1, 20)
    async def nitro(self, ctx):
        '''Bot sends nitro gift to current channel'''
        await ctx.message.delete()
        await ctx.send('https://i.redd.it/xedy9ugkqo621.png')

    @commands.command()
    @commands.cooldown(1, 3)
    async def code(self,ctx):
        '''Shows how to format python code'''
        codeM = disnake.Embed()
        codeM.add_field(name="This is how to format Python code", value="\`\`\`py \nThe code\n\`\`\`\n**These are backticks, not quotes.**")
        await ctx.send(embed=codeM)

    #unknow error in the meme commands. The error have not been traceked down.
    @commands.group()
    @commands.cooldown(1, 3)
    async def meme(self, ctx):
        '''Meme command'''
        await ctx.message.delete()
        if ctx.invoked_subcommand is None:
            await ctx.send("No meme source provided, type '!help meme' to see choices")
    
    @meme.command()
    async def dankmemes(self, ctx):
        reddit = asyncpraw.Reddit(client_id=f'{meme()[0]}',
                     client_secret=f'{meme()[1]}',
                     user_agent=f'{meme()[2]}')
        memes_submissions = await reddit.subreddit('dankmemes').hot()
        post_to_pick = random.randint(1, 20)
        for i in range(0, post_to_pick):
            submission = next(x for x in memes_submissions if not x.stickied)
        await ctx.send(submission.url)

    @meme.command()
    async def memes(self, ctx):
        reddit = asyncpraw.Reddit(client_id=f'{meme()[0]}',
                     client_secret=f'{meme()[1]}',
                     user_agent=f'{meme()[2]}')
        memes_submissions = await reddit.subreddit('memes').hot()
        post_to_pick = random.randint(1, 20)
        for i in range(0, post_to_pick):
            submission = next(x for x in memes_submissions if not x.stickied)
        await ctx.send(submission.url)

    @commands.command()
    @commands.cooldown(1, 5)
    async def server(self, ctx):
        '''Shows some status of server'''
        member_count = len(ctx.guild.members)
        role_count = len(ctx.guild.roles)
        d = ctx.guild.created_at
        embed = disnake.Embed(title=f"Server information", description=f"Information of {ctx.guild.name}", color=ctx.author.color) #Server created: {year_difference}, {month_difference} and {day_difference} ago")
        embed.add_field(name="General", value=f"Members: {member_count}\nRoles: {role_count}\n")
        embed.set_thumbnail(url=f"{ctx.guild.icon_url}")
        embed.set_author(name="NipaDev")
        await ctx.send(embed=embed)

    @commands.command(aliases=["nick", "newname"])
    @commands.cooldown(1, 60)
    async def setnick(self, ctx: commands.Context, *, nick: str):
        '''Changes your nickname'''
        await ctx.author.edit(nick=nick)
        await ctx.send(f'Nickname was changed for {ctx.author.mention} ')

    @commands.command(aliases=["src"])
    @commands.cooldown(1, 30)
    async def source(self, ctx: commands.Context, command: str=None):
        '''Shows source of commands, and links it to github'''
        my_command = self.bot.get_command(command)
        if command is None:
            return await ctx.send("Please provide the command name")
            
        if not my_command:
            return await ctx.send("Command not found")
        else:
            command_call = my_command.callback
            command_lines = inspect.getsourcelines(command_call)
            code = inspect.getsource(command_call)
            first_line = command_lines[1]
            end_line = len(command_lines[0]) + first_line - 1
            file_path = inspect.getfile(command_call)
            filename = PurePath(file_path).name

            if len(code) > 1900:
                file = open(f'{command}.py', "w", encoding='utf-8')
                file.write(code)
                file.close()
                await ctx.send(file = disnake.File(f'{command}.py'))
                os.remove(f'./{command}.py')
            else:
                embed = disnake.Embed(title="Bot's GitHub Repository", color=ctx.author.color)
                embed.add_field(name=f"Source of command '{my_command}'", value=f"[Github link](https://github.com/Nipa-Code/Nipa-bot/tree/master/MyBot/cogs/{filename}#L{first_line}-L{end_line})")
                await ctx.send(embed=embed)

    @commands.command(aliases=("poll",))
    @commands.has_any_role(833841708805652481)
    async def vote(self, ctx: commands.Context, title: clean_content(fix_channel_mentions=True), *options: str) -> None:
        """
        Allow max 20 options to be passed. A simple poll command that generates a poll embed with x amount of reactions

        """
        if len(title) > 256:
            raise InvalidArgument("The title cannot be longer than 256 characters.")
        if len(options) < 2:
            raise InvalidArgument("Please provide at least 2 options.")
        if len(options) > 20:
            raise InvalidArgument("I can only handle 20 options!")

        codepoint_start = 127462  # represents "regional_indicator_a" unicode value
        options = {chr(i): f"{chr(i)} - {v}" for i, v in enumerate(options, start=codepoint_start)}
        embed = disnake.Embed(title=title, description="\n".join(options.values()), color=ctx.author.color)
        message = await ctx.send(embed=embed)
        for reaction in options:
            await message.add_reaction(reaction)

    @commands.command()
    async def create_emoji(self, ctx, name, emote):
        """Creates a emoji with given name"""
        await ctx.guild.create_custom_emoji(name = (name),image = bytes(requests.get(emote).content))
        await ctx.send(f'{ctx.author.mention} Added the emote with name {name}')

    @commands.command(name="ping")
    @commands.cooldown(1, 10)
    async def ping(self, ctx: commands.Context):
        """Get the bot's current websocket and API latency."""
        start_time = time.time()
        message = await ctx.send("Testing Ping...")
        end_time = time.time()

        await message.edit(content=f"Pong! {round(self.bot.latency * 1000)}ms\nAPI: {round((end_time - start_time) * 1000)}ms")
    
    @commands.command(aliases=["bm", "bookmark"])
    async def book_mark(self, ctx, msg: disnake.Message = None, *, title: str = None):
        """
        Bot sends a embed bookmark for you. Creates a new embed with reacton that people can react to
        and receive a bookmark that way.
        :param: msg, a disnake message object that is required
        :param: title, optional embed title
        """
        if msg is None:
            return await ctx.send("No message to bookmark")
        
        url = msg.jump_url
        await msg.channel.fetch_message(msg.id)

        if len(msg.content) > 40:
            content_of_description = msg.content[:40]
        else:
            content_of_description = msg.content

        embed = disnake.Embed(title="Bookmark" if title is None else title, description=f"{content_of_description}...", color=ctx.author.color)
        embed.add_field(name="Visit the Bookmarked message", value=f"[visit original message]({url})")
        embed.set_author(name=msg.author, icon_url=ctx.author.avtar.url)
        embed.set_thumbnail(url="https://images-ext-2.disnakeapp.net/external/zl4oDwcmxUILY7sD9ZWE2fU5R7n6QcxEmPYSE5eddbg/%3Fv%3D1/https/cdn.disnakeapp.com/emojis/654080405988966419.png?width=20&height=20")
        await ctx.author.send(embed=embed)
        
        e_embed = disnake.Embed(title="Bookmark.", description="React to this message to receive you own bookmark", color=ctx.author.color)
        new_msg = await ctx.send(embed=e_embed)

        def event_check(reaction: disnake.Reaction, user: disnake.Member) -> bool:
            """Make sure that this reaction is what we want to operate on."""
            return (
                # Conditions for a successful pagination:
                all((
                    # Reaction is on this message
                    reaction.message.id == new_msg.id,
                    # User has not already bookmarked this message
                    user.id not in bookmarked_users,
                    # Reaction is the `BOOKMARK_EMOJI` emoji
                    str(reaction.emoji) == "📌",
                    # Reaction was not made by the Bot
                    user.id != self.bot.user.id
                ))
            )

        bookmarked_users = [ctx.author.id]
        reaction_message = await new_msg.add_reaction("📌")

        while True:
            try:
                _, user = await self.bot.wait_for("reaction_add", timeout=30, check=event_check)
            except asyncio.TimeoutError:
                log.debug("Timed out waiting for a reaction")
                break
            log.info(f"{user} has successfully bookmarked from a reaction, attempting to DM them.")
            await user.send(embed=embed)
            bookmarked_users.append(user.id)
            
        await reaction_message.delete()

    @commands.command(aliases=["convert"])
    async def convert_to_utc(self, ctx, time: str):
        """
        A unit of time should be appended to the duration.
        Units (∗case-sensitive):
        \u2003`y` - years
        \u2003`m` - months∗
        \u2003`w` - weeks
        \u2003`d` - days
        \u2003`h` - hours
        \u2003`M` - minutes∗
        \u2003`s` - seconds
        Alternatively, an ISO 8601 timestamp can be provided for the duration.
        """
        b = await Duration().convert(ctx, time)
        return await ctx.send(b)

    @commands.command(aliases=["timestamp", "ts"])
    async def generate_timestamp(self, ctx, time: str):
        """
        A unit of time should be appended to the duration.
        Units (∗case-sensitive):
        \u2003`y` - years
        \u2003`m` - months∗
        \u2003`w` - weeks
        \u2003`d` - days
        \u2003`h` - hours
        \u2003`M` - minutes∗
        \u2003`s` - seconds
        Alternatively, an ISO 8601 timestamp can be provided for the duration.
        """
        b = await Duration().convert(ctx, time)
        ts = b.timestamp()
        await ctx.send(f"Timestamp number: {int(ts)} \nConverted to: `<t:{int(ts)}:F>` in format F\nTimestamp: <t:{int(ts)}:F>")

    @commands.command()
    async def remind(self, ctx, time: str, *, message: str):
        b = await Duration().convert(ctx, time)
        ts = b.timestamp()
        #timestamp = 
        embed = disnake.Embed(
            title="Reminder set", 
            description=f"""
            Your reminder will arrive on <t:{int(ts)}:F>
            But I won't ping you nor will I do anything because I'm bored
            """, color=ctx.author.color
            )
        await ctx.send(embed=embed)

    @commands.command()
    async def roleinfo(self, ctx, *roles: Union[Role, str]) -> None:
        """
        Return information on a role or list of roles.
        To specify multiple roles just add to the arguments, delimit roles with spaces in them using quotation marks.
        """
        parsed_roles = set()
        failed_roles = set()

        all_roles = {role.id: role.name for role in ctx.guild.roles}
        for role_name in roles:
            if isinstance(role_name, Role):
                # Role conversion has already succeeded
                parsed_roles.add(role_name)
                continue

            match = rapidfuzz.process.extractOne(
                role_name, all_roles, score_cutoff=80,
                scorer=rapidfuzz.fuzz.ratio
            )

            if not match:
                failed_roles.add(role_name)
                continue

            # `match` is a (role name, score, role id) tuple
            role = ctx.guild.get_role(match[2])
            parsed_roles.add(role)

        if failed_roles:
            await ctx.send(f":x: Could not retrieve the following roles: {', '.join(failed_roles)}")

        for role in parsed_roles:
            h, s, v = colorsys.rgb_to_hsv(*role.colour.to_rgb())

            embed = Embed(
                title=f"{role.name} info",
                colour=role.colour,
            )
            embed.add_field(name="ID", value=role.id, inline=True)
            embed.add_field(name="Colour (RGB)", value=f"#{role.colour.value:0>6x}", inline=True)
            embed.add_field(name="Colour (HSV)", value=f"{h:.2f} {s:.2f} {v}", inline=True)
            embed.add_field(name="Member count", value=len(role.members), inline=True)
            embed.add_field(name="Position", value=role.position)
            embed.add_field(name="Permission code", value=role.permissions.value, inline=True)

            await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message: disnake.Message):
        self.last_msg = message
    
    """
    @commands.command(name="snipe")
    @commands.cooldown(1, 30)
    async def snipe(self, ctx: commands.Context):
        '''A command to snipe delete messages.'''
        if not self.last_msg:  # on_message_delete hasn't been triggered since the bot started
            await ctx.send("There is no message to snipe!")
            return

        author = self.last_msg.author
        content = self.last_msg.content

        embed = disnake.Embed(title=f"Message from {author}", description=content, color=ctx.author.color)
        await ctx.send(embed=embed)
    """

def setup(bot):
    bot.add_cog(General(bot))