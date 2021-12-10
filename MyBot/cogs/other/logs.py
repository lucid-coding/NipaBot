import disnake
from disnake.ext import commands
from disnake.utils import escape_markdown

from MyBot.utils.constants import SPECIAL
from MyBot.utils.converters import DurationDelta, Duration
from MyBot.utils.factory import ModLog
from MyBot.utils.decorators.deco import restrict_to_user

import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
WEBHOOK = os.getenv('WEBHOOK_URL')
WEBHOOK_ID = os.getenv('WEBHOOK_ID')

class Log(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.modlog = ModLog
        self.webhook = WEBHOOK
        self.webhook_id = WEBHOOK_ID

    @commands.Cog.listener("on_member_join")
    async def member_join(self, member):
        """When ever user join the guild, modlog will receive logs"""
        content = await self.modlog.send_log_message(
            self, colour=disnake.Color.red(), title=f"{member} | {member.id} has joined", 
            text="User has left the guild, attempting to log information", icon_url=member.avatar.url, 
            content="Sample content", footer="Logger webhook", ping_everyone=True
                #thumbnail="Sample thumbnail"
            )

        await ModLog.send_webhook(self, content)

    @commands.Cog.listener("on_member_remove")
    async def member_leave(self, member):
        """When ever user leaves a guild, modlog will receive logs"""
        content = await self.modlog.send_log_message(
            self, colour=disnake.Color.red(), title=f"{member} | {member.id}", 
            text="User has left the guild, attempting to log information", icon_url=member.avatar.url, 
            footer="Logger webhook"
            )

        await ModLog.send_webhook(self, content)

    @commands.Cog.listener("on_raw_bulk_message_delete")
    async def bulk_alert(self, messages):
        """Checking if messages are purged and alerting that to modlog channel"""
        if self.bot.id in messages or SPECIAL in messages:
            return
        content = await self.modlog.send_log_message(
            self, colour=disnake.Color.red(), title=f"Alert", 
            text=f"({len(messages)}) messages have been bulked in {messages[0].channel}", icon_url=disnake.Embed.Empty, 
            footer="Logger webhook"
            )

        await ModLog.send_webhook(self, content)

    @commands.Cog.listener("on_message_delete")
    async def message_deleted_alert(self, message):
        a = message.content if len(message.content) < 100 else message.content[:100]
        content = await self.modlog.send_log_message(
            self, colour=disnake.Color.red(), title=f"{message.author} | {message.author.id}", 
            text=f"{message.author} Has deleted a message, CONTENT: \n{a}", icon_url=message.author.avatar.url, 
            footer="Logger webhook"
            )

        await ModLog.send_webhook(self, content)

    @commands.Cog.listener("on_guild_channel_delete")
    async def channel_delete(self, channel):
        ...

    @commands.Cog.listener("on_guild_channel_create")
    async def channel_create(self, channel):
        ...

    @commands.Cog.listener("on_guild_update")
    async def guild_update(self, before, after):
        ...
    
    @commands.Cog.listener("on_guild_role_create")
    async def new_role(self, role):
        ...

    @commands.Cog.listener("on_guild_role_delete")
    async def role_delete(self, role):
        ...

    @commands.Cog.listener("on_member_ban")
    async def member_ban(self, guild, user):
        ...

    @commands.Cog.listener("on_member_unban")
    async def member_unban(self, guild, user):
        ...
    

def setup(bot):
    bot.add_cog(Log(bot))