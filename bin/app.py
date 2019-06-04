#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

from multiprocessing import Process
import os
import sys
from SimpleHTTPServer import SimpleHTTPRequestHandler
from SocketServer import TCPServer

import click

from staticpycon import utils, gen


def do_serve():
    print('Listening on 0.0.0.0:8080 ...\n')
    TCPServer.allow_reuse_address = True
    server = TCPServer(('0.0.0.0', 8080), SimpleHTTPRequestHandler)
    os.chdir(gen.SITE_DIR)
    server.serve_forever()


@click.command()
@click.option('--debug', '-d', is_flag=True, default=False,
              help=u'调试模式下不合并/压缩 Assets')
@click.option('--generate', '-g', is_flag=True, default=False,
              help=u'生成站点')
@click.option('--serve', '-s', is_flag=True, default=False,
              help=u'启动本地server')
def run(debug, generate, serve):
    utils.init_logger()

    if generate and serve:
        print(u'--generate和--serve不能同时使用')
        sys.exit(1)

    if serve:
        Process(target=do_serve).start()

    gen.create_site(debug=debug, use_reloader=serve, generate=generate)


if __name__ == '__main__':
    run()
