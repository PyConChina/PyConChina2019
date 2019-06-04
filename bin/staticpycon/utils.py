# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

import datetime
import errno
import itertools
import logging
import os

from ._colorama_compat import colorama


_PROMPT_FMT_INVALID_ATTR = (
    colorama.Style.DIM +
    colorama.Fore.YELLOW +
    'warn ' +
    colorama.Style.RESET_ALL +
    colorama.Fore.MAGENTA +
    'invalid attribute ' +
    colorama.Fore.RESET +
    '%s'
)

_PROMPT_FMT_HTML = (
    colorama.Style.DIM +
    colorama.Fore.CYAN +
    '[%s] ' +
    'html ' +
    colorama.Fore.GREEN +
    '[%s] ' +
    colorama.Fore.RESET +
    colorama.Style.RESET_ALL +
    '%s'
)


def now_str():
    return datetime.datetime.now().strftime('%H:%M:%S')


# http://stackoverflow.com/a/600612/596531
def mkdirp(path):
    """``mkdir -p`` for Python."""
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def init_logger():
    log = logging.getLogger('webassets')
    log.addHandler(logging.StreamHandler())
    log.setLevel(logging.DEBUG)


def prompt_invalid_attr(fmts):
    print(_PROMPT_FMT_INVALID_ATTR % fmts)


def prompt_render_html(fmts):
    assert isinstance(fmts, list) or isinstance(fmts, tuple)
    fmts = tuple(itertools.chain([now_str()], fmts))
    print(_PROMPT_FMT_HTML % fmts)
