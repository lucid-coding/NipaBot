from typing import List

import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction
from typing import Optional
   
class Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.langs = ["Python", "JavaScript", "TypeScript", "Java", "Rust", "Lisp", "Elixir"]

    async def autocomplete_langs(self, inter: ApplicationCommandInteraction, string: str) -> List[str]:
        return [lang for lang in self.langs if string.lower() in lang.lower()]

    @commands.slash_command(name="slashers", guild_ids=[776140379442905098])
    async def _test(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.send_message("hi")

    @commands.slash_command(name="resp", guild_ids=[776140379442905098])
    async def languages(self, inter: disnake.ApplicationCommandInteraction, language: str):
        await inter.response.send_message("return code 200")
        
    @languages.autocomplete("language")
    async def language_autocomp(self, inter: disnake.ApplicationCommandInteraction, string: str):
        string = string.lower()
        return [lang for lang in self.langs if string in lang.lower()]

def setup(bot):
    bot.add_cog(Slash(bot))