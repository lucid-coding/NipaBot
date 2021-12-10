import datetime
import re
from enum import Enum
from typing import Optional, Union

import dateutil.parser
import arrow
from dateutil.relativedelta import relativedelta

RFC1123_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"
DISCORD_TIMESTAMP_REGEX = re.compile(r"<t:(\d+):f>")

_DURATION_REGEX = re.compile(
    r"((?P<years>\d+?) ?(years|year|Y|y) ?)?"
    r"((?P<months>\d+?) ?(months|month|m) ?)?"
    r"((?P<weeks>\d+?) ?(weeks|week|W|w) ?)?"
    r"((?P<days>\d+?) ?(days|day|D|d) ?)?"
    r"((?P<hours>\d+?) ?(hours|hour|H|h) ?)?"
    r"((?P<minutes>\d+?) ?(minutes|minute|M) ?)?"
    r"((?P<seconds>\d+?) ?(seconds|second|S|s))?"
)

ValidTimestamp = Union[int, datetime.datetime, datetime.date, datetime.timedelta, relativedelta]


class TimestampFormats(Enum):
    """
    Represents the different formats possible for Discord timestamps.
    Examples are given in epoch time.
    """

    DATE_TIME = "f"  # January 1, 1970 1:00 AM
    DAY_TIME = "F"  # Thursday, January 1, 1970 1:00 AM
    DATE_SHORT = "d"  # 01/01/1970
    DATE = "D"  # January 1, 1970
    TIME = "t"  # 1:00 AM
    TIME_SECONDS = "T"  # 1:00:00 AM
    RELATIVE = "R"  # 52 years ago

def parse_duration_string(duration: str) -> Optional[relativedelta]:
    """
    Converts a `duration` string to a relativedelta object.
    The function supports the following symbols for each unit of time:
    - years: `Y`, `y`, `year`, `years`
    - months: `m`, `month`, `months`
    - weeks: `w`, `W`, `week`, `weeks`
    - days: `d`, `D`, `day`, `days`
    - hours: `H`, `h`, `hour`, `hours`
    - minutes: `M`, `minute`, `minutes`
    - seconds: `S`, `s`, `second`, `seconds`
    The units need to be provided in descending order of magnitude.
    If the string does represent a durationdelta object, it will return None.
    """
    match = _DURATION_REGEX.fullmatch(duration)
    if not match:
        return None

    duration_dict = {unit: int(amount) for unit, amount in match.groupdict(default=0).items()}
    delta = relativedelta(**duration_dict)

    return delta

def relativedelta_to_timedelta(delta: relativedelta) -> datetime.timedelta:
    """Converts a relativedelta object to a timedelta object."""
    utcnow = arrow.utcnow(tzinfo=None)
    return utcnow + delta - utcnow

@staticmethod
def _stringify_relativedelta(delta: relativedelta) -> str:
    """Convert a relativedelta object to a duration string."""
    units = [("years", "y"), ("months", "m"), ("days", "d"), ("hours", "h"), ("minutes", "m"), ("seconds", "s")]
    return "".join(f"{getattr(delta, unit)}{symbol}" for unit, symbol in units if getattr(delta, unit)) or "0s"