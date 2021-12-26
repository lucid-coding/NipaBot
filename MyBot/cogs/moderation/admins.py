import disnake
from disnake.ext import commands
from disnake.ext import tasks
from disnake.ext.commands.core import command

import disnake.errors

import aiosqlite
import asyncio
from datetime import datetime, timedelta
import typing
import re
from typing import Optional

from MyBot.utils.constants import DATABASE
from MyBot.utils.constants import Constants #import owner_check, check_author, default_role, mute, modlog
from MyBot.utils.constants import SPECIAL, NAMES
from MyBot.utils.converters import _has_invites
from MyBot.utils.decorators.deco import respect_role_hierarchy, has_no_roles
import logging

log = logging.getLogger(__name__)

class Moderation(commands.Cog):
    """The servers moderation command, containing most of import ones."""
    def __init__(self, bot):
        self.bot = bot
        self.owner_id = Constants.owner_check()
        self.mod_id = Constants.check_author()[0]
        self.admin_id = Constants.check_author()[1]
        self.default = Constants.default_role()
        self.cooldown = commands.CooldownMapping.from_cooldown(4.0, 10.0, commands.BucketType.member)
        self.tempm.start()
        self.mod_log = Constants.modlog()
        
    @commands.command()
    async def kick(self, ctx, member: disnake.Member, *, reason: str):
        '''Kicks member from guild with given reason'''
        owner = ctx.guild.get_role(self.owner_id)
        mod = ctx.guild.get_role(self.mod_id)
        admin = ctx.guild.get_role(self.admin_id)
        if owner in member.roles:
            return await ctx.send("Sorry, I can't do that")
        elif mod in member.roles or admin in member.roles:
            return await ctx.send("You can't do that, member is part of moderation team")
        else:
            try:
                await ctx.send(f"📨👌 {ctx.author.mention} kicked {member.mention}\n reason:{reason}")
            except disnake.Forbidden:
                log.info(f"{ctx.author} kicked {member} but their DMs are disabled")
            await member.kick(reason=reason)
            
    @commands.command()
    @respect_role_hierarchy(member_arg=2)
    async def ban(self, ctx, member: typing.Union[disnake.Member, disnake.User], * , reason: str):
        '''Bans member from guild with given reason'''
        role = ctx.guild.get_role(self.owner_id)
        mod = ctx.guild.get_role(self.mod_id)
        admin = ctx.guild.get_role(self.admin_id)
        if not member:
            return await ctx.send_help
        if role in member.roles:
            await ctx.send("Ban hammer reguires user.")
        elif mod in member.roles or admin in member.roles:
            return await ctx.send("You can't do that, member is part of moderation team")
        else:
            guild = ctx.guild
            await guild.ban(member, reason=reason)
            await ctx.send(f"📨👌 applied ban to {member.mention}\n reason:{reason}")

    @commands.command()
    async def unban(self, ctx, member: typing.Union[disnake.Member, disnake.User] = None):
        """Unbans user from the current guild"""
        if isinstance(member, disnake.Member):
            #return await ctx.send("That seems to be a guild member, we can't unban them")
            log.info("Command: unban param `member` is type of `disnake.Member`")
        elif isinstance(member, disnake.User):
            log.info("Command: unban param `member` is type of `disnake.User`")

        ctx.guild.unban(member)
        await ctx.send("Succesfully unbanned member")
        log.info(f"{ctx.author} has unbanned {member}")
        
    @commands.command()
    @respect_role_hierarchy(member_arg=2)
    async def to(self, ctx, member: disnake.Member, duration: int, reason: typing.Optional[str] = None):
        """
        Timeouts member from guild for duration of seconds given. 
        To remove timeout the duration must be 0. Reason can be None
        """ 
        if reason is None:
            reason = "You have been timed out from guild due to moderation actions."
        await member.timeout(duration=duration, reason=reason)  
        await ctx.send(f"{ctx.author.mention} succesfully timed out {member.mention} from guild.")

    @commands.command()
    async def mute(self, ctx, member: disnake.Member, *,message: str=None):
        '''Mutes from chatting, has no time setting. Will be more likely chat ban. NOTE: recommended to use tempmute'''
        role = ctx.guild.get_role(self.owner_id)
        if role in member.roles:
            return await ctx.send("You can't do that to owner")
        if message is None:
            message = 'No time specified'
        muted_role = disnake.utils.get(ctx.guild.roles, id=Constants.mute())
        if not muted_role:
            return
        if muted_role in member.roles:
            return await ctx.send("Member is already muted")
            print("Role not found")
            perms = disnake.PermissionOverwrite(send_messages=False, read_message_history=True, manage_channels=False, manage_permissions=False, manage_webhooks=False, create_instant_invite=False, embed_links=False, attach_files=False, add_reactions=False, manage_messages=False, use_slash_commands=False, send_tts_messages=False, mention_everyone=False, use_external_emojis=False, view_channel=True)
            muted = await ctx.guild.create_role(name="Muted", permissions=perms)
            for channels in ctx.guild.text_channels:
                await channels.set_permissions(muted, overwrite=perms)
        await member.add_roles(muted_role)
        await ctx.send(f"{ctx.author.mention} applied mute to {member.mention} {message}")            

    @commands.command()
    async def tempmute(self, ctx, member: disnake.Member, time: str = None):
        """Temporary mute members from chatting"""
        command = self.bot.get_command("mute")
        new_time = time
        user_name = member.name
        user_id = member.id
        apply_time = datetime.now()
        guild = member.guild.id
        role = Constants.mute()
        if time is None:
            time = apply_time + timedelta(hours=1)
        else:
            if 'm' in new_time:
                convert = int(new_time[:-1])
                time = apply_time + timedelta(minutes=convert)
            elif 'h' in new_time:
                convert = int(time[:-1])
                time = apply_time + timedelta(hours=convert)
            elif 'd' in new_time:
                convert = int(time[:-1])
                time = apply_time + timedelta(days=convert)
            else:
                time = apply_time + timedelta(hours=1)
        time_conv = time.strftime("%Y-%m-%d, %H:%M:%S")
        async with aiosqlite.connect(DATABASE) as db:
            await db.execute("INSERT INTO infractions VALUES(?, ?, ?, ?, ?, ?)", (guild, role, user_name, user_id, apply_time, time))
            await db.commit()
        await ctx.invoke(command, member = member, message=f"Muted till ({time_conv})")
            
    @commands.command()
    async def unmute(self, ctx, member: disnake.Member):
        '''Unmutes member'''
        muted_role = disnake.utils.get(ctx.guild.roles, id=Constants.mute())
        if not muted_role in member.roles:
            return await ctx.send("User is not muted")
            #await ctx.message.add_reaction("❌")
        else:
            await member.remove_roles(muted_role)
            await ctx.send(f"pardoned mute for {member.mention}")

    @commands.command()
    async def mutevc(self, ctx, member: disnake.Member):
        '''Will mute only from voice chat'''
        role = ctx.guild.get_role(self.owner_id)
        role2 = ctx.guild.get_role(self.admin_id)
        role3 = ctx.guild.get_role(self.mod_id)
        if role in member.roles or role2 in member.roles or role3 in member.roles:
            await ctx.send("You can't do that, member is part of moderation team")
            await ctx.message.add_reaction("❌")
        else:
            await member.edit(mute=True)
            await ctx.send(f"📨👌 applied Voice chat mute to {member.mention}")

    @commands.command()
    async def deafen(self, ctx, member: disnake.Member):
        '''Will deafen member'''
        role = ctx.guild.get_role(self.owner_id)
        role2 = ctx.guild.get_role(self.admin_id)
        role3 = ctx.guild.get_role(self.mod_id)
        if role in member.roles or role2 in member.roles or role3 in member.roles:
            await ctx.send("You can't do that, member is part of moderation team")
            await ctx.message.add_reaction("❌")
        else:
            await member.edit(deafen=True)
            await ctx.send(f"📨👌 deafened {member.mention}")

    @commands.command()
    async def unmutevc(self, ctx, member: disnake.Member):
        '''Unmutes from voice chat'''
        try:
            await member.edit(mute=False)
            await ctx.send(f"{member.mention} you may now speak again")
        except:
            mutevcEm = disnake.Embed()
            mutevcEm.add_field(name="Error", value="Try again")
            await ctx.send(embed=mutevcEm)
    
    @commands.command()
    async def undeafen(self, ctx, member: disnake.Member):
        '''Undeafens member'''
        try:
            await member.edit(deafen=False)
            await ctx.send(f"{member.mention} you may now hear again")
        except:
            undeafEm = disnake.Embed()
            undeafEm.add_field(name="Command failed", value="Try again")
            await ctx.send(embed=undeafEm)
    
    @commands.command(aliases=["hush", "shh", "shhh"])
    async def silence(self, ctx, time: int = None, channel: typing.Optional[disnake.TextChannel] = None):
        '''Silences the channel for default role, time is given in minutes.'''
        #print(self.default)
        role = ctx.guild.get_role(self.default)
        if time is None:
            time = 60 * 10
        else:
            time = time * 60
        perms = ctx.channel.overwrites_for(role)
        
        perms.send_messages = False
        await ctx.send(f"{ctx.author.mention} has silenced the channel for {time / 60} minutes.")
        await ctx.channel.set_permissions(role, overwrite=perms)
        await asyncio.sleep(time)
        #Launch unsilence
        perms = ctx.channel.overwrites_for(role)
        perms.send_messages = True
        await ctx.channel.set_permissions(role, overwrite=perms)

    @commands.command(aliases=["unhush", "unshh", "unshhh"])
    async def unsilence(self, ctx, channel: typing.Optional[disnake.TextChannel] = None):
        '''Unsilences the channel'''
        if channel is None:
            channel = ctx.channel
        role = disnake.utils.get(ctx.guild.roles, id=self.default)
        perms = channel.overwrites_for(role)
        perms.send_messages = True
        await channel.set_permissions(role, overwrite=perms)
        await channel.send(f"{ctx.author.mention} has unsilenced the channel")
    
    @commands.command()
    async def role(self, ctx, member: disnake.Member, *, role: disnake.Role):
        '''Adds role to member'''
        role1 = ctx.guild.get_role(self.owner_id)
        role2 = ctx.guild.get_role(self.admin_id)
        role3 = ctx.guild.get_role(self.mod_id)
        if role1 in ctx.author.roles:
            await member.add_roles(role)
            return
        elif role1 in member.roles:
            return await ctx.send("You can't control roles of owner")
        elif role2 in member.roles or role3 in member.roles:
            return await ctx.send("You can't do that, member is part of moderation team")
        elif role > ctx.author.top_role:
            return await ctx.send("You can't add roles higher than your")
        else:
            await member.add_roles(role)
            return await ctx.send(f"Succesfully added role '{role}' to {member.mention}")

    @commands.command(aliases=["remove", "roleg"])
    async def remove_role(self, ctx, member: disnake.Member, *, role: disnake.Role):
        '''Removes role from member'''
        role1 = ctx.guild.get_role(self.owner_id)
        role2 = ctx.guild.get_role(self.admin_id)
        role3 = ctx.guild.get_role(self.mod_id)
        if role1 in ctx.author.roles:
            await member.remove_roles(role)
        elif role1 in member.roles:
            await ctx.send("You can't control roles of owner")
        elif role2 in member.roles or role3 in member.roles:
            return await ctx.send("You can't do that, member is part of moderation team")
        else:
            await member.remove_roles(role)
            return await ctx.send(f"Deleted role '{role}' from {member.mention}")

    @commands.command()
    @commands.cooldown(1, 10)
    async def say(self, ctx, channel: Optional[disnake.TextChannel] = None, *, message: str):
        content = message
        '''Will be sending message to specific channel NOTE: should only be used in moderation channels'''
        #REGEX_SEARCH = re.compile(r"<(?P<animated>a?):(?P<name>[a-zA-Z0-9_]{2,32}):(?P<id>[0-9]{18,22})>")
        #REGEX_SEARCH.findall(content)
        #try:
        #    print(REGEX_SEARCH)
        #    emoji = self.bot.get_emoji(REGEX_SEARCH[1])
        #except Exception as e:
        #    print(e) #just ffor testing what error will be raised
        #    return
        await ctx.message.delete()
        if channel is None:
            channel = ctx.channel
        await channel.send(f"{message}")
    
    @commands.command()
    @commands.is_owner()
    async def setupper(self, ctx):
        botrole = ctx.guild.get_role(811331779138682930)
        perms = disnake.PermissionOverwrite(
            send_messages=True, 
            read_message_history=True, 
            manage_channels=True, 
            manage_permissions=True, 
            manage_webhooks=True, 
            create_instant_invite=True, 
            embed_links=True, 
            attach_files=False, 
            add_reactions=True, 
            manage_messages=True, 
            mention_everyone=False, 
            use_external_emojis=False, 
            view_channel=True)
        for channels in ctx.guild.text_channels:
            await channels.set_permissions(botrole, overwrite=perms)
        log.info("Setup complete")
        await ctx.message.add_reaction("✅")

    @commands.Cog.listener()
    async def on_message(self, message):
        modembed = disnake.Embed(title="Alert", color = disnake.Color.red())
        modembed.add_field(name="Action", value=f"{message.author} | ({message.author.id}) has triggered antispam in {message.channel}")

        #mod log channel
        mod_chat = self.bot.get_channel(self.mod_log)
        reason = f"You have triggered anti-spam which results to infraction.\nAlso your message was deleted, if you think it was mistake contact to moderation team."
        x = message.content
        nlines = x.count('\n')
        ctx = await self.bot.get_context(message)
        command = self.bot.get_command('tempmute')
        embed = disnake.Embed(title="Moderation")
        embed.add_field(name="Infraction", value=f"{reason}")
        embed.add_field(name="Infractions", value="Receiving this infraction multiple times will result to ban.")
        if message.author.bot:
            return
        if nlines > 35:
            await message.delete()
            log.info(f"{message.author}: {message.author.id}, sent a message with more than 30 lines. Which triggered anti-spam")
            await ctx.invoke(command, member=message.author, time="10m")
            await message.author.send(embed=embed)
            await mod_chat.send("normally a mention")
            await mod_chat.send(embed=modembed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if await _has_invites(self, message.content):
            return await message.delete()
        
        #invite_is_https = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message.content.lower())
        #invite_is_disnake_gg = re.findall('disnake.gg/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message.content.lower())
        #if message.author.bot:
        #    return
        #if invite_is_https or invite_is_disnake_gg:
        #    log.warning(f"Invite sent in {message.channel} by {message.author}")
        #    await message.delete()
        #    await message.channel.send("Please don't send random invites")

    """
    @commands.Cog.listener("on_message")
    async def antispam(self, message):
        '''Mutes member and deleted latest messages if member sends 4 duplicated messages'''
        if not message.guild:
            return
        embed = disnake.Embed(title="Alert")
        embed.add_field(name="Action", value=f"{message.author} | ({message.author.id}) has triggered antispam in {message.channel}")

        #mod log channel
        mod_chat = self.bot.get_channel(self.mod_log)
        async with aiosqlite.connect(DATABASE) as db:
            if message.author.id == self.bot.user.id:
                return
            #embed stuff
            reason = f"You have triggered anti-spam which results to infraction.\nAlso your message was deleted, if you think it was mistake contact to moderation team."
            embed = disnake.Embed(title="Moderation")
            embed.add_field(name="Infraction", value=f"{reason}")
            embed.add_field(name="Infractions", value="Receiving this infraction multiple times will result to ban.")

            command = self.bot.get_command("tempmute")
            user = message.author.name        
            user_id = message.author.id
            guild_id = message.guild.id
            current_time = datetime.utcnow()
            content = message.content
            check_time = datetime.utcnow() - timedelta(seconds=10)
            ctx = await self.bot.get_context(message)
            await db.execute("INSERT INTO log VALUES (?, ?, ?, ?, ?)", (guild_id, user, user_id, current_time, content))
            await db.commit()
            cursor = await db.execute("SELECT guild_id, user_id, content, COUNT(*) FROM log WHERE time >= ? and user_id = ? GROUP BY guild_id, user_id, content LIMIT 4", (check_time, user_id,))
            rows = await cursor.fetchmany(4)
            if len(rows) <= 4:
                for row in rows:
                    if rows[0][3] == 4:
                        user = rows[0][1]
                    else:
                        return
                ucheck = ctx.guild.get_member(user)
                await ctx.invoke(command, member = ucheck, time="10m")
                await ucheck.send(embed=embed)
                await mod_chat.send(embed=modembed)
                await mod_chat.send(embed=modembed)

        def check(message):
            if message.author.id == self.bot.user.id:
                return
            else:
                return message.author == message.author
        await message.channel.purge(limit=6, check=check)
    """

    @commands.Cog.listener("on_message")
    async def antispam2(self, message):

        modembed = disnake.Embed(title="Alert", color = disnake.Color.red())
        modembed.add_field(name="Action", value=f"{message.author} | ({message.author.id}) has triggered antispam in {message.channel}")

        #mod log channel
        mod_chat = self.bot.get_channel(self.mod_log)

        bucket = self.cooldown.get_bucket(message)
        retry_after = bucket.update_rate_limit()
        ctx = await self.bot.get_context(message)
        command = self.bot.get_command("tempmute")
        if message.author.id == self.bot.user.id:
            return

        if retry_after:
            log.warning(f"Tempmute triggered by {message.author}")
            await ctx.invoke(command, member = message.author, time="10m")
            
            def check1(message):
                if message.author.id == self.bot.user.id:
                    return
                else:
                    return message.author == message.author
            await message.channel.purge(limit=6, check=check1)
            await mod_chat.send("normally mention")
            await mod_chat.send(embed=modembed)

    @tasks.loop(seconds=30.0)
    async def tempm(self):
        async with aiosqlite.connect(DATABASE) as db:
            current_time = datetime.now()
            rows = await db.execute("SELECT guild_id, mute_id, user_id, expire FROM infractions WHERE ? > expire", (current_time,))
            data = await rows.fetchall()
            if data is None:
                return
            else:
                userinfo = []
                for x in data:
                    userinfo.append(x)
                try: 
                    guild_id = userinfo[0][0]
                    mute_role = userinfo[0][1]
                    print(f"Hi\n\n{mute_role}\n\n")
                    user = userinfo[0][2]
                except IndexError:
                    return
                user_guild = self.bot.get_guild(guild_id)
                mute = user_guild.get_role(mute_role)
                the_member = user_guild.get_member(user)
                if not user_guild or not the_member or not mute:
                    return
                else:
                    await the_member.remove_roles(mute)
                    print("REMOVING ROLES")
                    await db.execute("DELETE FROM infractions WHERE user_id = ?", (user,))
                    await db.commit()
    
    @tempm.before_loop
    async def before_muted_check(self):
        await self.bot.wait_until_ready()
                
    async def cog_check(self, ctx):
        '''Allow only moderators to invoke these commands'''
        user_role_ids = [role.id for role in ctx.author.roles]
        return ctx.author.id == SPECIAL or any(role in user_role_ids for role in Constants.check_author())

def setup(bot):
    bot.add_cog(Moderation(bot))