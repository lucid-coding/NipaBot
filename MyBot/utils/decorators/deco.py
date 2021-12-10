import disnake
import asyncio
from functools import wraps

from disnake.ext.commands import check, Context

def restrict_to_user(user: int):
    """Allows only specific user to run these commands. Must be edited manually from files"""
    async def predicate(ctx: Context):
        return ctx.author.id == user
    return check(predicate)

