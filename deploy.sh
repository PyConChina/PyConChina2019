#!/bin/sh

git ck master
git pull
/Users/laixintao/.virtualenvs/pycon2017/bin/python bin/app.py -g
scp -r  public/ spawnris@106.187.97.72:/home/spawnris/
ssh spawnris@106.187.97.72 "sudo rm -rf /home/wwwroot/cn.pycon.org/2019; sudo mv /home/spawnris/public /home/wwwroot/cn.pycon.org/2019; sudo chown -R www:www  /home/wwwroot/cn.pycon.org/2019; sudo chmod 755  /home/wwwroot/cn.pycon.org/2019"
