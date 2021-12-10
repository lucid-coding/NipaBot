import disnake
from disnake.ext import commands
import aiosqlite
from MyBot.utils.constants import DATABASE
from MyBot.utils.constants import owner_check, check_author
from MyBot.utils.errors import InvalidInfractedUserError
from MyBot.utils.constants import SPECIAL
import logging
from logging import getLogger

log = getLogger(__name__)

class Warning(commands.Cog):
    '''Cog for handling the warning system'''
    def __init__(self, bot):
        self.bot = bot
        self.owner_id = owner_check()
        self.mod_id = check_author()[0]
        self.admin_id = check_author()[1]

    @commands.command()
    async def warns(self, ctx, member: disnake.Member):
        '''Shows the amount of warnings user has'''
        user = member.id
        role = ctx.guild.get_role(self.owner_id)
        if role in member.roles:
            await ctx.send("Owners doesn't have warnings")
            await ctx.message.add_reaction("🚫")
        else:
            async with aiosqlite.connect(DATABASE) as db:
                cursor = await db.execute("SELECT Userid FROM warnings WHERE Userid = ?", (user,))
                rows = await cursor.fetchall()
                a = []
                for row in rows:
                    a.append(row)
                warnAmount = len(a)
                await ctx.send(f"user <@!{user}> has {warnAmount} warnings")

    @commands.command()
    async def warn(self, ctx, member: disnake.Member, *, reason: str = None):
        '''Warns user for their action. Reason must be provided in order to warn that user.'''
        if reason is None:
            return await ctx.send("Reason for warning must be provided.")

        DmEm = disnake.Embed(title="You received Infraction", color=disnake.Color.red())
        DmEm.add_field(name="Type", value="Warning")
        DmEm.add_field(name="Reason", value=f"{reason}")
        DmEm.add_field(name="Action", value=f"Action done by {ctx.author.mention}")
        
        role = ctx.guild.get_role(self.owner_id)
        role2 = ctx.guild.get_role(self.admin_id)
        role3 = ctx.guild.get_role(self.mod_id)

        if role in member.roles:
            await ctx.send("Owners can't be warned")
        elif role2 in member.roles or role3 in member.roles:
            await ctx.send("You can't do that, member is part of moderation team")
        elif member.id == self.bot.user.id:
            await ctx.message.add_reaction("🚫")
            log.info(f"{ctx.author} attemped to warn the bot which is highly forbidden")
            #raise InvalidInfractedUserError(member.id)
        else:
            async with aiosqlite.connect(DATABASE) as db:
                user_name = member.name
                user_id = member.id
                auth = str(ctx.author)
                authId = ctx.author.id
                reas = reason
                await db.execute("INSERT INTO warnings VALUES(?, ?, ?, ?, ?)", (user_name, user_id, auth,  authId, reas))
                await db.commit()
                try:
                    await member.send(embed=DmEm)
                    log.info(f"{ctx.author} warned {member}. Reason: {reason}")
                except disnake.Forbidden:
                    await ctx.message.add_reaction("🚫")
            await ctx.send(f"Applied warning to {member} || {member.id} reason: {reason}")
 
    async def cog_check(self, ctx):
        '''Allow only moderators to invoke these commands'''
        user_role_ids = [role.id for role in ctx.author.roles]
        return ctx.author.id == SPECIAL or any(role in user_role_ids for role in check_author())

def setup(bot):
    bot.add_cog(Warning(bot))
