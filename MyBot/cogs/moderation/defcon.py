import disnake
from disnake.errors import InvalidArgument
from disnake.ext import commands
from disnake.ext import tasks
from disnake.ext.commands import clean_content

from MyBot.utils.constants import DATABASE
from MyBot.utils.constants import owner_check, check_author, default_role
from MyBot.utils.constants import SPECIAL, NAMES, modlog
from MyBot.utils.time.times import relativedelta_to_timedelta, _stringify_relativedelta
from MyBot.utils.converters import format_user

import arrow
import logging
from dateutil.relativedelta import relativedelta
import humanize

REJECTION_MESSAGE = """
Hi, {user} - Thanks for your interest in our server!
Due to a current (or detected) cyberattack on our community, we've limited access to the server for new accounts. Since
your account is relatively new, we're unable to provide access to the server at this time.
Even so, thanks for joining! We're very excited at the possibility of having you here, and we hope that this situation
will be resolved soon.
"""

BASE_CHANNEL_TOPIC = "Defense Mechanism"

SECONDS_IN_DAY = 86400


log = logging.getLogger(__name__)

class Defcon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.default = default_role()
        self.mod_log = modlog()
        self.threshold = relativedelta(days=0)
        self.expiry = None

    @commands.Cog.listener()
    async def on_member_join(self, member: disnake.Member) -> None:
        """Check newly joining users to see if they meet the account age threshold."""
        print("RUNNING DEFCON CHECK")
        if self.threshold:
            print("running")
            log.warning("first if statement ran")
            now = arrow.utcnow()

            if now - member.created_at < relativedelta_to_timedelta(self.threshold):
                log.info(f"Rejecting user {member}: Account is too new")


                message_sent = False

                try:
                    await member.send(REJECTION_MESSAGE.format(user=member.mention))
                    message_sent = True
                except disnake.Forbidden:
                    log.debug(f"Cannot send DEFCON rejection DM to {member}: DMs disabled")
                except Exception:
                    # Broadly catch exceptions because DM isn't critical, but it's imperative to kick them.
                    log.exception(f"Error sending DEFCON rejection message to {member}")

                await member.kick(reason="DEFCON active, user is too new")

                message = (
                    f"{format_user(member)} was denied entry because their account is too new."
                )

                if not message_sent:
                    message = f"{message}\n\nUnable to send rejection message via DM; they probably have DMs disabled."
                
                mod_chat = self.bot.get_channel(self.mod_log)
                embed = disnake.Embed(title="Entry denied", description=message)
                await mod_chat.send(embed=embed)
        else:
            # for debugging because it does not work yet
            a = "b" if self.threshold else "c"
            print(a)

    @commands.group()
    async def defcon(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command.name)

    @defcon.command(name="threshold", aliases=('t', 'd'))
    async def threshold_command(self, ctx, threshold: int):
        if isinstance(threshold, int):
            threshold = relativedelta(days=threshold) 
            self.threshold = threshold

    @defcon.command(aliases=["lockdown", "activate", "lock"])
    async def shutdown(self, ctx):
        role = ctx.guild.get_role(self.default)
        permissions = role.permissions

        permissions.update(
            send_messages=False,
            add_reactions=False,
            send_messages_in_threads=False,
            connect=False
        )
        await role.edit(reason="DEFCON shutdown", permissions=permissions)
        await ctx.send(f"Server shut down.")

    @defcon.command()
    async def unshutdown(self, ctx):
        role = ctx.guild.get_role(self.default)#ctx.guild.default_role
        permissions = role.permissions

        permissions.update(
            send_messages=True,
            add_reactions=True,
            send_messages_in_threads=True,
            connect=True
        )
        await role.edit(reason="DEFCON unshutdown", permissions=permissions)
        await ctx.send(f"Server reopened.")
        
    @defcon.command()
    async def status(self, ctx):
        embed = disnake.Embed(
            colour=disnake.Colour.red(), title="DEFCON Status",
            description=f"""
                **Threshold:** {humanize.naturaldelta(self.threshold) if self.threshold else "-"}
                **Expires:** does not exist yet
                **Verification level:** {ctx.guild.verification_level.name}
                """
        )
        await ctx.send(embed=embed)

    async def cog_check(self, ctx):
        '''Allow only moderators to invoke these commands'''
        user_role_ids = [role.id for role in ctx.author.roles]
        return ctx.author.id == SPECIAL or any(role in user_role_ids for role in check_author())

def setup(bot):
    bot.add_cog(Defcon(bot))