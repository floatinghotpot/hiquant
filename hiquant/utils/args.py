# -*- coding: utf-8; py-indent-offset:4 -*-

import datetime as dt
from .datetime import date_from_str, datetime_today

def parse_params_options(argv):
    params = []
    options = []
    for i in range(1, len(argv)):
        str = argv[i]
        if str[0] == '-':
            options.append(str)
        else:
            params.append(str)

    return params, options

def parse_arg(argv, required, defaults, syntax_tips):
    params, options = parse_params_options(argv)

    n = len(params)
    if n < required:
        print(syntax_tips.replace('__argv0__', argv[0]))
        exit()

    vals = list(defaults.values())
    m = len(vals)
    if n < m:
        params = params + vals[n:]

    return params[0:m], options

def dict_from_config_items(items, verbose = False):
    mapping = {}
    for k, v in items:
        mapping[ k ] = v
        if verbose:
            print(k, '=', v)
    return mapping

def date_range_from_options(options):
    date_from = None
    date_to = None
    days = None
    for option in options:
        if option.startswith('-days='):
            days = int(option.replace('-days=',''))
            date_from = date_from_str('{} days ago'.format(days))
            date_to = datetime_today()
        if option.startswith('-years='):
            days = int(option.replace('-years=','')) * 365
            date_from = date_from_str('{} days ago'.format(days))
            date_to = datetime_today()
        if option.startswith('-date='):
            date_range = option.replace('-date=','').split('-')
            date_from = date_from_str(date_range[0])
            date_to = date_from_str(date_range[1]) if (len(date_range)>1 and len(date_range[1])>0) else datetime_today()
        if option.startswith('-year='):
            date_range = option.replace('-year=','').split('-')
            date_from = dt.datetime(int(date_range[0]), 1, 1)
            date_to = dt.datetime(int(date_range[1]), 12, 31) if (len(date_range)>1 and len(date_range[1])>0) else datetime_today()

    if date_from is None:
        days = 365 * 3
        date_from = date_from_str('{} days ago'.format(days))
        date_to = datetime_today()

    return date_from, date_to

def range_from_options(options):
    range_from = 0
    range_to = 0
    for k in options:
        if k.startswith('-limit='):
            k = k.replace('-limit=','-range=')
        if k.startswith('-range='):
            k = k.replace('-range=','')
            if '-' in k:
                ranges = k.split('-')
                range_from = int(ranges[0])
                range_to = int(ranges[1]) if (len(ranges)>1 and len(ranges[1])>0) else 0
                return range_from, range_to
            else:
                return 0, int(k)
    return range_from, range_to

def csv_xlsx_from_options(options):
    csv = ''
    xlsx = ''
    for k in options:
        if k.startswith('-out='):
            if k.endswith('.csv'):
                csv = k.replace('-out=', '')
            if k.endswith('.xlsx'):
                xlsx = k.replace('-out=', '')
    return csv, xlsx

