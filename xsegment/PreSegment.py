# coding=utf-8
#!/usr/bin/env python

import re
import sys
from hmm import HSegment
from b2 import system2
system2.reload_utf8()
REGX_ARRY = [(
    'URL', ur"((https?|ftp|news):\/\/)?([a-z]([a-z0-9\-]*[\.。])+([a-z]*)|(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))(\/[a-z0-9_\-\.~]+)*(\/([a-z0-9_\-\.]*)(\?[a-z0-9+_\-\.%=&]*)?)?(#[a-z][a-z0-9_]*)?"),
    ('SIGN', r"[\.\=、，!！_?？\[\]【】：:。“”…\"〜]+"),
    ('AT', ur"(//)?@[\u4e00-\u9fa5a-z0-9]+"),
    ('IP' , ur'((2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(2[0-4]\d|25[0-5]|[01]?\d\d?)'),
    ('FLOAT', ur"\d+\.\d+"),
    ('INTEGER', ur"[0-9]+"),
    ('ZN', ur"[\u4e00-\u9fa5]+"),
    ('EN', ur"[a-zA-Z]+"),
    ('MAIL',ur'[a-z]([a-z0-9]*[-_]?[a-z0-9]+)*@([a-z0-9]*[-_]?[a-z0-9]+)+[.][a-z]{2,3}([.][a-z]{2})?'),
    ]


WORD_EXTRACT_REGX = ur'|'.join(ur'(?P<%s>%s)' % (pair[0],pair[1]) for pair in REGX_ARRY)
WORD_EXTRACT = re.compile(WORD_EXTRACT_REGX, re.U|re.IGNORECASE).finditer




def getWordSign(d):
    if d and isinstance(d, dict):
        for _key, _val in d.items():
            if _val != None:
                return (_val, _key)
    return None


def token(words):
    for token in WORD_EXTRACT(words):
        yield getWordSign(token.groupdict())
