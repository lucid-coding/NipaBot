import pathlib
import yaml

#path pre set
DATABASE = r"MyBot/database/sqlite.db"
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

#returns list of moderators roles
def check_author():
    with open(f"{CONFIG_PATH}") as file:
        items = yaml.load(file, Loader=yaml.FullLoader)
    mod_id = []
    for x in items['modroles']:
        mod_id.append(x)
    #print(mod_id)
    return mod_id

##returns owner role
def owner_check():
    with open(f"{CONFIG_PATH}") as file:
        items = yaml.load(file, Loader=yaml.FullLoader)
    owner_id = []
    for x in items['owners']:
        owner_id.append(x)
    return owner_id[0]
#returns a channel where DMs are relayed in 
def channel_forward():
    with open(f"{CONFIG_PATH}") as file:
        items = yaml.load(file, Loader=yaml.FullLoader)
    chann = []
    for x in items['forward']:
        chann.append(x)
    return chann[0]
#returns the default member role
def default_role():
    with open(f"{CONFIG_PATH}") as file:
        items = yaml.load(file, Loader=yaml.FullLoader)
    def_role = items['roles']['default']
    return def_role
#returns muted role id.
def mute():
    with open(f"{CONFIG_PATH}") as file:
        items = yaml.load(file, Loader=yaml.FullLoader)
    muted = items['infraction']
    return muted[0]

def modlog():
    with open(f"{CONFIG_PATH}") as file:
        items = yaml.load(file, Loader=yaml.FullLoader)
    modlog_channel = items["channels"]["modlog"]
    return modlog_channel

def welcome():
    with open(f"{CONFIG_PATH}") as file:
        items = yaml.load(file, Loader=yaml.FullLoader)
    welcome_channel = items['channels']['welcome']
    return welcome_channel

def is_trusted():
    with open(f"{CONFIG_PATH}") as file:
        items = yaml.load(file, Loader=yaml.FullLoader)
    trusted_roles = []
    for x in items['trusted']:
        trusted_roles.append(x)
    return trusted_roles

def meme():
    with open(f"{CONFIG_PATH}") as file:
        items = yaml.load(file, Loader=yaml.FullLoader)
    info = []
    for x in items["api"]:
        info.append(x)
    return info