# -*- coding: utf-8; py-indent-offset:4 -*-

_lang_res = {
    '_current_lang': 'en'
    # 'en' = {},
    # 'zh' = {},
}

def add_lang(lang, translation):
    _lang_res[ lang ] = translation

def set_lang(lang = 'en'):
    _lang_res['_current_lang'] = lang

def get_lang():
    return _lang_res['_current_lang']

def LANG(key, lang = None):
    if lang is None:
        lang = _lang_res['_current_lang']

    if lang in _lang_res:
        lang_dict = _lang_res[ lang ]
        if key in lang_dict:
            return lang_dict[ key ]
        else:
            return key
    else:
        raise ValueError('Unknown language: ' + lang)
