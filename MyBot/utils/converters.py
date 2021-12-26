"""

"""

from __future__ import annotations

import typing as t
from typing import Union
import datetime

import asyncio
import re
from datetime import timedelta
from typing import Any, Dict, List, Mapping, NamedTuple, Optional, Tuple, Union

import disnake.errors
import disnake
from disnake.ext import commands
from disnake.ext.commands import BadArgument, Context, Converter, IDConverter, MemberConverter, UserConverter
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

import dateutil.tz
import aiohttp
import logging

from MyBot.utils.time.times import parse_duration_string
from MyBot.utils.time.regex import INVITE_RE

T = t.TypeVar("T")

log = logging.getLogger()

class DurationDelta(Converter):
    """Convert duration strings into dateutil.relativedelta.relativedelta objects."""

    async def convert(self, ctx: Context, duration: str) -> relativedelta:
        """
        Converts a `duration` string to a relativedelta object.
        The converter supports the following symbols for each unit of time:
        - years: `Y`, `y`, `year`, `years`
        - months: `m`, `month`, `months`
        - weeks: `w`, `W`, `week`, `weeks`
        - days: `d`, `D`, `day`, `days`
        - hours: `H`, `h`, `hour`, `hours`
        - minutes: `M`, `minute`, `minutes`
        - seconds: `S`, `s`, `second`, `seconds`
        The units need to be provided in descending order of magnitude.
        """
        if not (delta := parse_duration_string(duration)):
            raise BadArgument(f"`{duration}` is not a valid duration string.")

        return delta


class Duration(DurationDelta):
    """Convert duration strings into UTC datetime.datetime objects."""

    async def convert(self, ctx: Context, duration: str) -> datetime:
        """
        Converts a `duration` string to a datetime object that's `duration` in the future.
        The converter supports the same symbols for each unit of time as its parent class.
        """
        delta = await super().convert(ctx, duration)
        now = datetime.now(timezone.utc)

        try:
            return now + delta
        except (ValueError, OverflowError):
            raise BadArgument(f"`{duration}` results in a datetime outside the supported range.")

def format_user(user: disnake.abc.User) -> str:
    """Return a string for `user` which has their mention and ID."""
    return f"{user.mention} (`{user.id}`)"

class ResponseCodeError(ValueError):
    """Raised when a non-OK HTTP response is received."""

    def __init__(
        self,
        response: aiohttp.ClientResponse,
        response_json: Optional[dict] = None,
        response_text: str = ""
    ):
        self.status = response.status
        self.response_json = response_json or {}
        self.response_text = response_text
        self.response = response

    def __str__(self):
        response = self.response_json if self.response_json else self.response_text
        return f"Status: {self.status} Response: {response}"

async def req(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            json_data = await resp.json()
            return json_data #would return a object to be used later

async def _has_invites(self, text: str) -> Union[dict, bool]:
        """
        Checks if there's any invites in the text content that aren't in the guild whitelist.
        If any are detected, a dictionary of invite data is returned, with a key per invite.
        If none are detected, False is returned.
        Attempts to catch some of common ways to try to cheat the system.
        """
        #text = self.clean_input(text)

        # Remove backslashes to prevent escape character aroundfuckery like
        # disnake\.gg/gdudes-pony-farm
        text = text.replace("\\", "")

        invites = [m.group("invite") for m in INVITE_RE.finditer(text)]
        invite_data = dict()
        for invite in invites:
            if invite in invite_data:
                continue
            
            response = await req(
                f"https://discordapp.com/api/v7//{invite}"
            )

            #response = await response.json()
            guild = response.get("guild")
            if guild is None:
                return True

            guild_id = guild.get("id")

            reason = None
           
            reason = "invite not allowed"

            guild_icon_hash = guild["icon"]
            guild_icon = (
                "https://cdn.discordapp.com/icons/"
                f"{guild_id}/{guild_icon_hash}.png?size=512"
            )
            invite_data[invite] = {
                "name": guild["name"],
                "id": guild['id'],
                "icon": guild_icon,
                "members": response["approximate_member_count"],
                "active": response["approximate_presence_count"],
                "reason": reason
            }
        return invite_data if invite_data else False