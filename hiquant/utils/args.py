# -*- coding: utf-8; py-indent-offset:4 -*-

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
