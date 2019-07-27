[![Build Status](https://travis-ci.org/PyConChina/PyConChina2019.svg?branch=master)](https://travis-ci.org/PyConChina/PyConChina2019)

# PyConChina2019

The official website of PyCon China 2019, 基于 [https://github.com/PyConChina/staticpycon](https://github.com/PyConChina/staticpycon)

## Dev

```bash
npm install uglify-js -g
sudo gem install sass
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

或

```bash
docker-compose up -d
docker exec -it pycon-dev-vm /bin/zsh
cd /PyConChina
```

开发模式(监控变化):

```bash
source venv/bin/activate
python ./bin/app.py -s
```

## 志愿者必读

只改动 `src` 里面的内容：

- `base` 是 html 结构，基本不需要改动
- `asset` 是静态资源，例如图片，所有的图片请放到这个文件夹通过 `git push` 到仓库
- `data` 是主要需要修改的内容，不同的 yaml 文件是不同的内容，例如日程，志愿者等
