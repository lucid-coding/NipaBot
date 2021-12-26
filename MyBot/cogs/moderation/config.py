import disnake
from disnake.errors import InvalidArgument
from disnake.ext import commands
from disnake.ext import tasks
from disnake.ext.commands import clean_content
import typing
from MyBot.utils.constants import DATABASE
from MyBot.utils.constants import Constants #import owner import owner_check, check_author, default_role
from MyBot.utils.constants import SPECIAL, NAMES
import datetime

import logging

log = logging.getLogger(__name__)

class configuration(commands.Cog):
    """Configuration cog for the bot."""
    def __init__(self, bot):
        self.bot = bot
        self.default = Constants.default_role()


    @commands.group()
    async def edit(self, ctx):
        """Group commands for editing and configuration of server"""
        if not ctx.invoked_subcommand:
            await ctx.send_help(ctx.command.name)

    @edit.command()
    async def msg(self, ctx, message: int, channel: typing.Optional[disnake.TextChannel] = None, *, content: str = None):
        """Edits a message sent by bot. Does not work for editing Embed content"""
        if not content:
            await ctx.send("Message content is not provided")
        if not channel :
            channel = ctx.channel
        msgs = await channel.fetch_message(message)
        await msgs.edit(content=content)

    @edit.command()
    async def role(self, ctx, role: disnake.Role):
        """Sets overwrites for current channel to None"""
        #perms = ctx.channel.overwrites_for(role)
        #67437633 for proper mute perms
        try:
            await ctx.channel.set_permissions(role, overwrite=None)
            #if that errored it would still send Success
            await ctx.send("Success")
        except Exception as error:
            raise error
    @commands.command()
    async def logs(self, ctx, amount: int = 20):
        if amount > 100:
            amount = 100
        async for entry in ctx.guild.audit_logs(limit=amount):
            print(f'{entry.user} did {entry.action} to {entry.target}')

    @commands.command()
    async def uinfo(self, ctx, member: disnake.Member):
        await ctx.send(member.created_at)

    @commands.command()
    async def get_permissions(self, ctx, role: disnake.Role):
        a = ctx.channel.permissions_for(role)
        print(a)

    async def cog_check(self, ctx):
        '''Allow only moderators to invoke these commands'''
        user_role_ids = [role.id for role in ctx.author.roles]
        return ctx.author.id == SPECIAL or any(role in user_role_ids for role in Constants.check_author())


def setup(bot):
    bot.add_cog(configuration(bot))
