import pathlib
import yaml
import functools
from pathlib import path

#path pre set
if path("MyBot/database/sqlite.db").exists():
    """Will check if database used for development exists"""
    DATABASE = r"MyBot/database/sqlite.db" 
    #this is database file that will be ignored on commit
elif path("MyBot/database/database.db").exists():
    """Checks if the database given by default exist."""
    DATABASE = r"MyBot/database/database.db"

#path pre set
CONFIG_PATH = pathlib.Path(r"MyBot/utils/config.yaml")

#this user is allowed to run moderation commands WITHOUT moderator role, so be sure to give it to someone trusted
#Set this to None, if you don't want to use it (if causes error give the owner user_id)
SPECIAL = 534738044004335626

NAMES = [
    "Default User",
    "Discord User",
    "My name is polite",
    "Normal user",
    "Carrot",
    "Potato",
    "ButterFingers"
    "Captain Starified"
]
@functools.lru_cache
def load():
    """Loader function to load data from connfig.yaml"""
    with open(CONFIG_PATH) as file:
        items = yaml.load(file, Loader=yaml.FullLoader)
    return items

class Constants:
    """Constants class to manage receiving information from config.yaml"""
    def __init__(self):
        self.path = CONFIG_PATH

    def check_author():
        """Returns a list of mod roles"""
        mod_id = []
        for x in load()['modroles']:
            mod_id.append(x)
        return mod_id

    def is_trusted():
        """Returns the list of trusted roles, does not yet have a usage"""
        trusted_roles = []
        for x in load()['trusted']:
            trusted_roles.append(x)
        return trusted_roles

    def meme():
        """Returns the information of Reddit API. Sadly the API does not work anymore"""
        info = []
        for x in load()["api"]:
            info.append(x)
        return info

    def owner_check():
        """Returns the owners role"""
        return load()['owners'][0]

    def channel_forward():
        """Returns the channel where DMs are forwarded to."""
        return load()['forward'][0]

    def default_role():
        """Returns the default role of server that is given in the configuration file."""
        return load()['roles']['default']
    
    def modlog():
        """Returns the modlog channel of the server"""
        return load()["channels"]["modlog"]

    def welcome():
        """Returns the welcome channel of the server"""
        return load()['channels']['welcome']

    def mute():
        """Returns the muted role of the server"""
        return load()['infraction'][0]

