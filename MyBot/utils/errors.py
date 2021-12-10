import disnake
from disnake.ext.commands import ConversionError, Converter
import logging



class NonExistentRoleError(ValueError):
    """
    Raised by the Information Cog when encountering a Role that does not exist.

    Attributes:
        `role_id` -- the ID of the role that does not exist
    """

    def __init__(self, role_id: int):
        super().__init__(f"Could not fetch data for role {role_id}")

        self.role_id = role_id

class InvalidInfractedUserError(Exception):
    """
    Exception raised upon attempt of infracting an invalid user.

    Attributes:
        `user` -- User or Member which is invalid
    """

    def __init__(self, user: disnake.Member, reason: str = "User infracted is a bot."):

        self.user = user
        self.reason = reason

        super().__init__(reason)

