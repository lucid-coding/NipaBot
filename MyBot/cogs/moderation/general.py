import disnake
from disnake.ext import commands
from disnake.ext import tasks

import aiosqlite
import os.path
import typing
from datetime import datetime, timedelta

from MyBot.utils.constants import DATABASE
from MyBot.utils.constants import Constants # import owner import owner_check, check_author
from MyBot.utils.errors import InvalidInfractedUserError
from MyBot.utils.constants import SPECIAL, NAMES

import logging
import random

log = logging.getLogger(__name__)

class Mods(commands.Cog):
    """Commands for general modearation of server"""
    def __init__(self, bot):
        self.bot = bot
        self.streamloop.start()

    @commands.command(aliases=["sm", "smode", "slow"])
    async def slowmode(self, ctx, duration: int, channel: typing.Optional[disnake.TextChannel] = None):
        """Sets slowmode to current channel the commands is invoked, arguments taked as in seconds"""
        if channel is None:
            channel = ctx.channel
        await channel.edit(slowmode_delay=duration)
        await ctx.send(f"{channel} slowmode set to {duration} second(s)")

    @commands.command(aliases=["clear", "cls"])
    @commands.cooldown(2, 10)
    async def purge(self, ctx, amount: int) -> None:
        """Deletes specific amount of messages in channel.
        Be aware of rate limits Suggested amount ~10-20 max per use case."""
        await ctx.channel.purge(limit=amount)
        log.warning(f"{ctx.author.display_name} purged {amount} messages in {ctx.channel.name}")

    @commands.command()
    async def starify(self, ctx, member: disnake.Member) -> None:
        """Changes user name to something else if needed."""
        if member.id == self.bot.user.id:
            log.warning(f"{ctx.author} tried to starify the bot")
            return
        if member is None:
            await ctx.send_help()
        await member.edit(nick=random.choice(NAMES))

        embed = disnake.Embed()
        embed.add_field(name="Infraction", value="Your username has been changed as it may be breaking the server rules or breaking disnake Terms of Services", inline=False)
        embed.add_field(name="Expires", value="Never", inline=False)
        embed.set_footer(text="If you would like to discuss this infraction, contact to bot or Moderation team.")
        await ctx.message.add_reaction("✅")
        try:
            await member.send(embed=embed)
        except disnake.errors.Forbidden:
            log.warning("User has disabled DMs.")

    @commands.command(name="ustream", aliases=["video", "videoshare"])
    async def stream_role(self, ctx, member: disnake.Member, duration: str = None) -> None:
        """
        Allows any user to be able to stream in voice chats, except muted users.
        Default value is 30 minutes if no duration is specified. 
        """
        video_role = int(882677702237241384) #video role: ctx.guild.get_role
        role = ctx.guild.get_role(882677702237241384)
        apply_time = datetime.now()
        guild = member.guild.id
        user = member.id
        if duration is None:
            duration = apply_time + timedelta(minutes=30)
        if "m" in duration:
            convert = int(duration[:-1])
            duration = apply_time + timedelta(minutes=convert)
        elif "h" in duration:
            convert = int(duration[:-1])
            duration = apply_time + timedelta(hours=convert)
        else: 
            await ctx.send("Use format of either [10m] to give video permission for 10 minutes. Use format [1h] to give video permission for 1 hour")
        async with aiosqlite.connect(DATABASE) as db:
            await db.execute("INSERT INTO rolecontrol VALUES (?, ?, ? ,?)", (guild, user, video_role, duration,))
            await db.commit()

        await member.add_roles(role)
        log.info(f"{ctx.author} gave streaming permission for {member}:({member.id}). Duration '{duration}'")
        await ctx.send(f"{member.mention} has permission to stream on voice chat")

    @tasks.loop(seconds=30.0)
    async def streamloop(self):
        current_time = datetime.now()
        async with aiosqlite.connect(DATABASE) as db:
            rows = await db.execute("SELECT guild_id, user_id, role, expire FROM rolecontrol WHERE ? > expire", (current_time,))
            data = await rows.fetchall()
            if data is None:
                return
            else:
                userinfo = []
                for x in data:
                    userinfo.append(x)
                try: 
                    guild_id = userinfo[0][0]
                    user = userinfo[0][1]
                    video = userinfo[0][2]
                except IndexError:
                    return
                user_guild = self.bot.get_guild(guild_id)
                role = user_guild.get_role(video)
                the_member = user_guild.get_member(user)
                if not user_guild or not the_member or not role:
                    return
                else:
                    await the_member.remove_roles(role)
                    await db.execute("DELETE FROM rolecontrol WHERE role = ?", (video,))
                    await db.commit()

    @streamloop.before_loop
    async def before_muted_check(self):
        await self.bot.wait_until_ready()
        
    async def cog_check(self, ctx):
        '''Allow only moderators to invoke these commands'''
        user_role_ids = [role.id for role in ctx.author.roles]
        return ctx.author.id == SPECIAL or any(role in user_role_ids for role in Constants.check_author())

def setup(bot):
    bot.add_cog(Mods(bot))
