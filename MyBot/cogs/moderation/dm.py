from logging import getLogger
from typing import Optional
import asyncio
import disnake
from disnake.ext import commands
import aiosqlite
from datetime import datetime, timedelta
from pytz import timezone
from MyBot.utils.constants import Constants
from MyBot.utils.constants import DATABASE
from MyBot.utils.constants import SPECIAL


#When bot receives message, it will every time send the same message.
#This system is under development, the ModMail feature is NOT done.

log = getLogger(__name__)

class DmSender(commands.Cog):
    """Handles direct messages from user(s). Currently under development"""
    def __init__(self, bot):
        self.bot = bot
        self.webhook = None
        self.forward = Constants.channel_forward()
        self.modmail_channel = 884145344605224970 #this channel for modmail
        
    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        """gets the main forward channel"""
        channel = self.bot.get_channel(self.forward)
        if message.guild or message.author.bot:
            return


        if message.content is not None:    
            embed = disnake.Embed(title="Confirm thread creation", description="This system is for reporting concerns to the moderators, and is not intended for other purposes.")
            embed.set_footer(text="React to contact Moderation team.")
            msg = await message.author.send(embed=embed)
            await msg.add_reaction("✅")
            await msg.add_reaction("❌")
            #check function for reactions
            def check(reaction, user):
                return user == message.author and str(reaction.emoji) == "✅" and (str(reaction.emoji) == "✅" or str(reaction.emoji) == "❌")

            try:
               reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout = 60)

            except asyncio.TimeoutError:
                embed = disnake.Embed(title="Cancelled", description="Timed out")
                return await message.author.send(embed=embed)
                
            if str(reaction.emoji) == "✅":
                async with aiosqlite.connect(DATABASE) as db: #don't mind this yet
                    await db.execute("INSERT INTO modmail VALUES (?, ?, ?, ?)", ("guild, userid, channelid, isopen=True/False"))
                    await db.commit()
                embed = disnake.Embed(title="Thread Created", description="Thank you for your report! The moderation team will get back to you as soon as possible.", timestamp=datetime.utcnow())
                embed.set_footer(text="Your message has been sent")
                channel = self.bot.get_channel(self.modmail_channel)                
                await message.author.send(embed=embed)
                return await channel.send(f"@here new thread!")

            elif str(reaction.emoji) == "❌":
                embed = disnake.Embed(title="Cancelled", description="Cancelled by you.")
                return await message.author.send(embed=embed)
            else:
                log.fatal("Failed to create thread.")

            #working with system of ModMail above

        #embed/variables to forward
        content=message.content
        username=f"{message.author.display_name} ({message.author.id})"
        avatar_url=message.author.avatar.url
        time = datetime.utcnow()

        embed = disnake.Embed(description=f"{content}", timestamp = time)
        embed.set_author(name=f"{username}", url=embed.Empty, icon_url=f"{avatar_url}")
        embed.set_footer(text="Message created")
        await channel.send(embed=embed)
        await self.bot.process_commands(message)

    @commands.command(aliases=("reply",))
    async def send_dm(self, ctx: commands.Context, member: Optional[disnake.Member], *, message: str) -> None:        
        """
        Allow you to send DM to user(s):
        If member is not provided, bot will automatically send message to last user.
        NOTE:Overusing this feature will lead to disabling this feature.
        """
        if not member: #connects to database to check for members
            async with aiosqlite.connect(DATABASE) as db:
                cursor = await db.execute("SELECT userid FROM messages ORDER BY time DESC")
                row = (await cursor.fetchone())[0]
                member = ctx.guild.get_member(row) if row else None
            await ctx.message.add_reaction("✅")
            log.info("Message sended")

        # If we still don't have a Member at this point, give up
        if not member:
            log.info("This bot has never gotten a DM, or the database has been cleared.")
            await ctx.message.add_reaction("❌")
            return

        if member.id == self.bot.user.id:
            log.info("Not sending message to bot user")
            return await ctx.send("🚫 I can't send messages to myself!")
        try:
            embed = disnake.Embed(description=f"{message}", timestamp = datetime.utcnow())
            embed.set_author(name=f"{ctx.author}", url=embed.Empty, icon_url=ctx.author.avatar.url)
            embed.set_footer(text=f"{ctx.author.top_role}")
            await member.send(embed=embed)
        except disnake.errors.Forbidden:
            log.info("User has disabled DMs.")
            await ctx.message.add_reaction("❌")
        else:
            await ctx.message.add_reaction("✅")

    async def cog_check(self, ctx):
        '''Allow only moderators to invoke these commands'''
        user_role_ids = [role.id for role in ctx.author.roles]
        return ctx.author.id == SPECIAL or any(role in user_role_ids for role in Constants.check_author())

def setup(bot):
    bot.add_cog(DmSender(bot))
