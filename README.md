# PyConChina2019
The official website of PyCon China 2019, 基于 [https://github.com/PyConChina/staticpycon](https://github.com/PyConChina/staticpycon)

## Dev

```
npm install uglify-js -g
sudo gem install sass
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

开发模式(监控变化):

```
source venv/bin/activate
./bin/app.py -s
```

## 志愿者必读

只改动src里面的内容：

- base是html结构，基本不需要改动
- asset是静态资源，例如图片，所有的图片请放到这个文件夹通过git push到仓库
- data是主要需要修改的内容，不同的yaml文件是不同的内容，例如日程，志愿者等。