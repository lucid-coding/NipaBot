import disnake
import asyncio
import difflib
import itertools
import typing as t
from datetime import datetime, timezone
from itertools import zip_longest
import aiohttp

import disnake
from dateutil.relativedelta import relativedelta
from disnake.abc import GuildChannel
from disnake.ext.commands import Cog, Context
from disnake.utils import escape_markdown
from disnake import Webhook

from MyBot.utils.constants import modlog, SPECIAL

from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
WEBHOOK_ID = os.getenv('WEBHOOK_ID')

class ModLog:
    """Embed generator class"""
    def __init__(self, bot):
        self.bot = bot
        self.webhook = WEBHOOK_URL
        self.webhook_id = WEBHOOK_ID
        
    async def send_log_message(
        self,
        icon_url: t.Optional[str],
        colour: t.Union[disnake.Colour, int],
        title: t.Optional[str],
        text: str,
        thumbnail: t.Optional[t.Union[str, disnake.Asset]] = None,
        channel_id: int = modlog(),
        ping_everyone: bool = False,
        files: t.Optional[t.List[disnake.File]] = None,
        content: t.Optional[str] = None,
        additional_embeds: t.Optional[t.List[disnake.Embed]] = None,
        timestamp_override: t.Optional[datetime] = None,
        footer: t.Optional[str] = None,
    ) -> Context:
        """Generate log embed and send to logging channel."""
        # Truncate string directly here to avoid removing newlines
        embed = disnake.Embed(
            description=text[:4093] + "..." if len(text) > 4096 else text
        )

        if title and icon_url:
            embed.set_author(name=title, icon_url=icon_url)

        embed.colour = colour
        embed.timestamp = timestamp_override or datetime.utcnow()

        if footer:
            embed.set_footer(text=footer)

        if thumbnail:
            embed.set_thumbnail(url=thumbnail)

        if ping_everyone:
            if content:
                content = f"<@!{SPECIAL}>\n{content}"
            else:
                content = f"<@!{SPECIAL}>"

        # Truncate content to 2000 characters and append an ellipsis.
        if content and len(content) > 2000:
            content = content[:2000 - 3] + "..."

        channel = self.bot.get_channel(channel_id)
        #log_message = await channel.send(
            #content=content,
        embed=embed#,
            #files=files
        #)
        return embed
        #if additional_embeds:
        #    for additional_embed in additional_embeds:
        #        await channel.send(embed=additional_embed)

        #return await self.bot.get_context(log_message)  # Optionally return for use with antispam

    async def send_webhook(self, embed: disnake.Embed):
        """Webhook sender function for sending 1 embed"""
        async with aiohttp.ClientSession() as session:
            webhook = disnake.Webhook.from_url(url=self.webhook, session=session)
            return await webhook.send(embed=embed)