# -*- coding: utf-8 -*-

from __future__ import unicode_literals

__all__ = [
    'colorama',
]


try:
    import colorama
except ImportError:
    # just stub out ANSI control codes
    class colorama(object):
        class Style(object):
            DIM = RESET_ALL = ''

        class Fore(object):
            BLACK = RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = ''
            RESET = ''

        @staticmethod
        def init():
            pass

# vim:set ai et ts=4 sts=4 fenc=utf-8:
