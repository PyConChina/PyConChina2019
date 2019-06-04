# -*- coding: utf-8 -*-

from os.path import dirname, realpath, join
from fabric.api import local, env
from fabric.contrib.project import rsync_project

env.user = 'imust'
env.hosts = ['119.254.110.163']
VPS_DEPLOY_PATH = '/home/imust/data/www/public/'

PROJECT_ROOT_DIR = realpath(dirname(__file__))
DIST_DIR = join(PROJECT_ROOT_DIR, 'public') + '/'
VENV_PYTHON = join(PROJECT_ROOT_DIR, 'venv', 'bin', 'python2')


def clean():
    local(u'rm -rf {}'.format(DIST_DIR))


def build():
    clean()
    local(u'{python} bin/app.py -g'.format(python=VENV_PYTHON))


def deploy_vps():
    build()
    rsync_project(remote_dir=VPS_DEPLOY_PATH,
                  local_dir=DIST_DIR, delete=True)
