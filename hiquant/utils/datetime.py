# -*- coding: utf-8; py-indent-offset:4 -*-

import os
import datetime as dt

def str_now():
    return dt.datetime.now().strftime('%Y:%m:%d %H:%M:%S')

def datetime_today():
    now = dt.datetime.now()
    return dt.datetime(now.year, now.month, now.day)

def get_file_modify_time(fname):
    ts = os.stat(fname).st_mtime
    return dt.datetime.fromtimestamp(ts)

# 20180101
# 1 year ago
# 2 days later
# future
# etc.
def date_from_str(str):
    today = datetime_today()
    if ('ago' in str) or ('later' in str):
        items = str.split(' ')
        n = int(items[0])
        unit = items[1]
        ago_later = +1 if (items[2] == 'later') else -1
        if 'day' in items[1]:
            return today + ago_later * dt.timedelta(days=n)
        elif 'month' in items[1]:
            return today + ago_later * dt.timedelta(days=n*30)
        elif 'year' in items[1]:
            return today + ago_later * dt.timedelta(days=n*365)
        elif 'week' in items[1]:
            return today + ago_later * dt.timedelta(days=n*7)
        else:
            raise ValueError('invalid format:' + str)
    elif 'today' == str:
        return today
    elif 'future' == str:
        return today + dt.timedelta(days=99*365)
    elif 'yesterday' == str:
        return today - dt.timedelta(days=1)
    elif 'tomorrow' == str:
        return today + dt.timedelta(days=1)
    else:
        return dt.datetime.strptime(str, '%Y%m%d')

# 00:01:00
# 1 hour/day/week/month/year
# 5 min
# 30 sec
def seconds_from_str(str):
    if ':' in str:
        d = dt.datetime.strptime(str, '%Y:%M:%S')
        return (d - dt.datetime(d.year, d.month, d.day)).total_seconds()
    else:
        items = str.split(' ')
        n = int(items[0])
        unit = items[1]
        if 'sec' in unit:
            return n * 1
        elif 'min' in unit:
            return n * 60
        elif 'hour' in unit:
            return n * 3600
        elif 'day' in unit:
            return n * 3600 * 24
        elif 'week' in unit:
            return n * 3600 * 24 * 7
        elif 'month' in unit:
            return n * 3600 * 24 * 30
        elif 'year' in unit:
            return n * 3600 * 24 * 365
        else:
            raise ValueError('invalid format:' + str)
