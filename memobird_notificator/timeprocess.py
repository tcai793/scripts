from crontab import CronTab
from datetime import datetime, timezone, timedelta


def get_utctimestamp():
    utctime = datetime.utcnow().timestamp()
    return strip_second(utctime)


def strip_second(timestamp):
    return timestamp - (timestamp % 60)


def timestamp_to_str(timestamp):
    timestamp = strip_second(timestamp)
    delta = timedelta(seconds=timestamp)

    day = delta.days
    hours, rem = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(rem, 60)

    return '{} days {} hours {} minutes'.format(day, hours, minutes)
