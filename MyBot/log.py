import logging
from logging import handlers


def setup() -> None:
    """Logger function that will be called when bot goes online"""
    format_string = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"

    log = logging.getLogger()

    logging.basicConfig(handlers=[logging.FileHandler("MyBot/discord.log", mode='a'), logging.StreamHandler()], format=format_string, level=logging.INFO)
