from datetime import datetime, timedelta, tzinfo
from django.utils import timezone

def time_diff_raw(creationTimestamp = None):
    epoch = datetime(1970, 1, 1).replace(tzinfo = timezone.utc)
    timeDiff = creationTimestamp - epoch
    seconds = timeDiff.days*86400 + timeDiff.seconds + (float(timeDiff.microseconds) / 1000000)
    return seconds

def humanize_time(creationTimestamp = None):
    """
    Returns a humanized string representing time difference
    between now() and the input timestamp.

    IMPORTANT TIME REFERENCE:
    timezone.now() = the current time based on UTC, aka the real time zone. (aware)
    datetime.datetime.now() = the system time (naive)
    """
    timeDiff = timezone.now().replace(tzinfo = timezone.utc) - creationTimestamp

    one_hour = 3600
    one_day = 3600 * 24

    if timeDiff.seconds < (one_hour * 7):
        return "Just In!"
    elif timeDiff.seconds < one_day:
        return "Fresh"
    else:
        return "Expiring"
