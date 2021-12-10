import disnake
from disnake import File
from disnake.ext import commands

from asyncdagpi import Client, ImageFeatures


class Context(commands.Context):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def session(self):
        return self.bot.session

    @disnake.utils.cached_property
    def replied_reference(self):
        ref = self.message.reference
        if ref and isinstance(ref.resolved, disnake.Message):
            return ref.resolved.to_reference()
        return None

    @property
    def thumb(self) -> str:
        return '<:thumb:867439449582862357>'

    @property
    def agree(self) -> str:
        return '<:agree:797537027469082627>'

    @property
    def disagree(self) -> str:
        return '<:disagree:797537030980239411>'

    @property
    def dagpi(self) -> Client:
        """The dagpi client."""

        return self.bot.dagpi_client

    async def pixel(self, img_url: str) -> File:
        """|coro|
        Parameters
        ----------
            img_url: `:class:str`
                The image url to apply the effect on.
        Returns
        -------
            file: `:class:disnake.File`
                The disnake File object.
        """

        while True:
            try:
                img = await self.dagpi.image_process(ImageFeatures.pixel(), url=img_url)
                break
            except Exception:
                pass

        file = File(fp=img.image, filename=f'pixel.{img.format}')
        return file

    async def ascii(self, img_url: str) -> File:
        """|coro|
        Parameters
        ----------
            img_url: `:class:str`
                The image url to apply the effect on.
        Returns
        -------
            file: `:class:disnake.File`
                The disnake File object.
        """

        while True:
            try:
                img = await self.dagpi.image_process(ImageFeatures.ascii(), url=img_url)
                break
            except Exception:
                pass

        file = File(fp=img.image, filename=f'ascii.{img.format}')
        return file

    async def blur(self, img_url: str) -> File:
        """|coro|
        Parameters
        ----------
            img_url: `:class:str`
                The image url to apply the effect on.
        Returns
        -------
            file: `:class:disnake.File`
                The disnake File object.
        """

        while True:
            try:
                img = await self.dagpi.image_process(ImageFeatures.blur(), url=img_url)
                break
            except Exception:
                pass

        file = File(fp=img.image, filename=f'blur.{img.format}')
        return file

    async def bonk(self, img_url: str) -> File:
        """|coro|
        Parameters
        ----------
            img_url: `:class:str`
                The image url to apply the effect on.
        Returns
        -------
            file: `:class:disnake.File`
                The disnake File object.
        """

        while True:
            try:
                img = await self.dagpi.image_process(ImageFeatures.bonk(), url=img_url)
                break
            except Exception:
                pass

        file = File(fp=img.image, filename=f'bonk.{img.format}')
        return file

    async def colors(self, img_url: str) -> File:
        """|coro|
        Parameters
        ----------
            img_url: `:class:str`
                The image url to apply the effect on.
        Returns
        -------
            file: `:class:disnake.File`
                The disnake File object.
        """

        while True:
            try:
                img = await self.dagpi.image_process(ImageFeatures.colors(), url=img_url)
                break
            except Exception:
                pass

        file = File(fp=img.image, filename=f'colors.{img.format}')
        return file

    async def burn(self, img_url: str) -> File:
        """|coro|
        Parameters
        ----------
            img_url: `:class:str`
                The image url to apply the effect on.
        Returns
        -------
            file: `:class:disnake.File`
                The disnake File object.
        """

        while True:
            try:
                img = await self.dagpi.image_process(ImageFeatures.burn(), url=img_url)
                break
            except Exception:
                pass

        file = File(fp=img.image, filename=f'burn.{img.format}')
        return file

    async def deepfry(self, img_url: str) -> File:
        """|coro|
        Parameters
        ----------
            img_url: `:class:str`
                The image url to apply the effect on.
        Returns
        -------
            file: `:class:disnake.File`
                The disnake File object.
        """

        while True:
            try:
                img = await self.dagpi.image_process(ImageFeatures.deepfry(), url=img_url)
                break
            except Exception:
                pass

        file = File(fp=img.image, filename=f'deepfry.{img.format}')
        return file

    async def gay(self, img_url: str) -> File:
        """|coro|
        Parameters
        ----------
            img_url: `:class:str`
                The image url to apply the effect on.
        Returns
        -------
            file: `:class:disnake.File`
                The disnake File object.
        """

        while True:
            try:
                img = await self.dagpi.image_process(ImageFeatures.gay(), url=img_url)
                break
            except Exception:
                pass

        file = File(fp=img.image, filename=f'gay.{img.format}')
        return file

    async def mirror(self, img_url: str) -> File:
        """|coro|
        Parameters
        ----------
            img_url: `:class:str`
                The image url to apply the effect on.
        Returns
        -------
            file: `:class:disnake.File`
                The disnake File object.
        """

        while True:
            try:
                img = await self.dagpi.image_process(ImageFeatures.mirror(), url=img_url)
                break
            except Exception:
                pass

        file = File(fp=img.image, filename=f'mirror.{img.format}')
        return file

    async def lego(self, img_url: str) -> File:
        """|coro|
        Parameters
        ----------
            img_url: `:class:str`
                The image url to apply the effect on.
        Returns
        -------
            file: `:class:disnake.File`
                The disnake File object.
        """

        while True:
            try:
                img = await self.dagpi.image_process(ImageFeatures.lego(), url=img_url)
                break
            except Exception:
                pass

        file = File(fp=img.image, filename=f'lego.{img.format}')
        return file

    async def flip(self, img_url: str) -> File:
        """|coro|
        Parameters
        ----------
            img_url: `:class:str`
                The image url to apply the effect on.
        Returns
        -------
            file: `:class:disnake.File`
                The disnake File object.
        """

        while True:
            try:
                img = await self.dagpi.image_process(ImageFeatures.flip(), url=img_url)
                break
            except Exception:
                pass

        file = File(fp=img.image, filename=f'lego.{img.format}')
        return file

    async def trigger_typing(self):
        try:
            channel = await self._get_channel()
            await self._state.http.send_typing(channel.id)
        except disnake.Forbidden:
            pass