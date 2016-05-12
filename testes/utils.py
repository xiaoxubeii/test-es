__author__ = 'tardis'
from random import Random
import random

import ConfigParser


def random_int(randomlength=8):
    str = ''
    chars = '0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return int(str)


def random_list(l):
    return l[random.randint(0, len(l) - 1)]


class Config(object):
    def __init__(self, config_path, section='DEFAULTS'):
        self.section = section
        self.config = ConfigParser.RawConfigParser(allow_no_value=True)
        self.config.read(config_path)

    def __getattr__(self, item):
        return self.config.get(self.section, item)
