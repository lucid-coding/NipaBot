import disnake
from disnake.ext import commands
import datetime
from datetime import datetime
import aiosqlite
from MyBot.utils.constants import DATABASE
from MyBot.utils.constants import default_role, welcome
from logging import getLogger

log = getLogger(__name__) 

class EventHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error,commands.MissingPermissions):
            print(type(error))
            embed = disnake.Embed(color = disnake.Color.red())
            embed.add_field(name=f"{ctx.guild.name}", value=f"Missing permissions {error.missing_permissions}")
            await ctx.send(embed=embed)

        elif isinstance(error,commands.MissingRequiredArgument):
            print(type(error))
            embed = disnake.Embed(color = disnake.Color.red())
            embed.add_field(name=f"{ctx.guild.name}", value=f"Missing argument: {error.param}")
            await ctx.send(embed=embed)

        elif isinstance(error, commands.MissingRole):
            print(type(error))
            embed = disnake.Embed()
            embed.add_field(name=f"{ctx.guild.name}", value=f"You are missing the {error.missing_role.mention} role")
            await ctx.send(embed=embed)

        elif isinstance(error,commands.CommandNotFound):
            print(type(error))
            embed = disnake.Embed(color = ctx.author.color)
            embed.add_field(name=f"{ctx.guild.name}", value="Invalid command type !help")
            await ctx.send(embed=embed)

        elif isinstance(error, commands.CommandOnCooldown):
            print(type(error))
            embed = disnake.Embed(color = ctx.author.color)
            embed.add_field(name=f"{ctx.guild.name}", value=f"This command is on cooldown. Please try again after {round(error.retry_after, 1)} seconds.")
            await ctx.send(embed=embed)

        elif isinstance(error, commands.MemberNotFound):
            print(type(error))
            embed = disnake.Embed(color = ctx.author.color)
            embed.add_field(name=f"{ctx.guild.name}", value=f"Seems like that user is not found on guild. Maybe try something else?")
            await ctx.send(embed=embed)

        elif isinstance(error, commands.MissingAnyRole):
            print(type(error))
            embed = disnake.Embed(color = ctx.author.color)
            embed.add_field(name=f"{ctx.guild.name}", value=f"Missing at least one of reguired roles {error.missing_roles}")
            await ctx.send(embed=embed)
            
        elif isinstance(error, commands.CheckFailure):
            print(type(error))
            error = getattr(error, 'original', error)
            await ctx.send(f"{error} You are not allowed to run this command")
            
        else:
            raise error
    """
    @commands.Cog.listener()
    async def on_member_join(self,  member):
        channel = self.bot.get_channel(welcome())
        embed =  disnake.Embed(title="👋 Welcome!",description=f"{member.name} has joined.")
        embed.add_field(name="Commands", value="To see list of bot commands type !help.")
        role = disnake.utils.get(member.guild.roles, id=default_role())
        await member.add_roles(role)
        await channel.send(embed=embed)
    """
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = self.bot.get_channel(welcome())
        await channel.send(f"{member.name} has left guild 👋.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild:
            return
        id = message.author.id
        name = message.author.name
        time = datetime.now()
        if message.author.id == self.bot.user.id:
            return
        else:
            async with aiosqlite.connect(DATABASE) as db:
                await db.execute("INSERT INTO messages VALUES(?, ?, ?)", (name, id, time))
                await db.commit()

def setup(bot):
    bot.add_cog(EventHandler(bot))
