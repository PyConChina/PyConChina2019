# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

import json
import logging
import pipes
import re
import yaml

from copy import deepcopy
from multiprocessing import Process
from os.path import dirname, realpath, join, getmtime, relpath
from os import listdir, system
from collections import OrderedDict

from staticjinja import make_site, Reloader
from webassets import Environment, Bundle
from webassets.ext.jinja2 import AssetsExtension
from webassets.script import CommandLineEnvironment

from .utils import mkdirp, prompt_invalid_attr, prompt_render_html

log = logging.getLogger('webassets')


data_mtimes = {}
data_pattern = re.compile("_(\w+)\.yaml")
data_contexts = {
    'cn': {'lang': 'cn', 'lang_suffix': '_cn', 'lang_dir': ''},
    'en': {'lang': 'en', 'lang_suffix': '_en', 'lang_dir': 'en'},
}


# HACK: 当 js/css 变化时, 强制重新渲染
def event_handler(self, event_type, src_path):
    filename = relpath(src_path, self.searchpath)
    if self.should_handle(event_type, src_path):
        print("%s %s" % (event_type, filename))
        if self.site.is_static(filename):
            files = self.site.get_dependencies(filename)
            self.site.copy_static(files)
            # js/css变化时, 强制重新渲染
            self.site.render_templates(self.site.templates)
        elif data_pattern.match(filename):
            # 数据文件变动时, 重新渲染
            self.site.render_templates(self.site.templates)
        else:
            templates = self.site.get_dependencies(filename)
            self.site.render_templates(templates)


Reloader.event_handler = event_handler


PROJECT_ROOT_DIR = dirname(dirname(realpath(dirname(__file__))))

SITE_SRC_DIR = join(PROJECT_ROOT_DIR, 'src')
SITE_ASSET_SRC_DIR = join(PROJECT_ROOT_DIR, 'asset')
DATA_SRC_DIR = join(SITE_SRC_DIR, "data")

SITE_ASSET_URL_PREFIX = './asset'
# 不能使用默认的 Cache 目录, 否则 Cache 也会被 staticjinja 拷贝
WEBASSETS_CACHE_DIR = join(PROJECT_ROOT_DIR, '.webassets-cache')

# 静态站点输出根目录
SITE_DIR = join(PROJECT_ROOT_DIR, 'public')
# webassets 输出根目录, 要输出到 SITE_SRC_DIR, 以便 staticjinja 监控文件变化
SITE_ASSET_DIR = join(SITE_SRC_DIR, 'asset')
REL_SITE_ASSET_DIR = 'asset'

# HACK: 因为站点是靠location来区分历届的, 因此资源目录需要特殊处理
EN_SITE_DIR = join(SITE_DIR, 'en')


def _sp_printlog(msg):
    '''模板函数, 在生成日志中输出消息.'''
    print(msg)


def _sp_selectspeakers(speakers, city):
    '''模板函数，选择指定city的speakers'''
    keyname = "city_" + city
    city_speakers = [speaker for speaker_id, speaker in speakers.iteritems()
                     if keyname in speaker]
    print(u'城市: %s' % (city, ))
    [print(speaker['name']) for speaker in city_speakers]
    return city_speakers


def _process_data(data, suffix):
    '''数据处理函数，用于实现翻译文本的自动替换

    主要目的是把用suffix结尾的键对应的值覆盖无suffix结尾的键对应的值，
    如把name_en（_en是suffix）的值写到name中。处理过程中使用了递归。
    '''
    if isinstance(data, list):
        for v in data:
            _process_data(v, suffix)
    elif isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, list) or isinstance(v, dict):
                _process_data(v, suffix)
            if k.endswith(suffix):
                kn = k[:-len(suffix)]
                if kn in data:
                    data[kn] = v
                    del data[k]
                else:
                    prompt_invalid_attr(kn)
            elif k.endswith('_en') or k.endswith('_cn'):    # HARDCODE
                del data[k]


def _write_json():
    for lang, context in data_contexts.items():
        outfile = join(SITE_DIR, context['lang_dir'], "pycon.json")
        mkdirp(dirname(outfile))

        with open(outfile, "w") as fp:
            output_context = deepcopy(context)
            # TODO better way to clean context
            del output_context['printlog']
            del output_context['selectspeakers']
            json.dump(output_context, fp, indent=2, sort_keys=True)


def _ordered_yaml_load(stream, default_loader=yaml.Loader, object_pairs_hook=OrderedDict):
    class OrderedLoader(default_loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)


def _load_data():
    '''载入数据文件，保存了文件的mtime以减少不必要的读操作'''
    data_modified = False
    for filename in listdir(DATA_SRC_DIR):
        filepath = join(DATA_SRC_DIR, filename)
        filemtime = int(getmtime(filepath))
        if filepath in data_mtimes and filemtime == data_mtimes[filepath]:
            continue    # skip unmodified file
        data_modified = True
        match = data_pattern.match(filename)
        if match:
            data_mtimes[filepath] = filemtime
            entryname = match.group(1)
            data = _ordered_yaml_load(open(filepath))
            # data = yaml.load(open(filepath))
            for lang, context in data_contexts.items():
                data_copy = deepcopy(data)
                _process_data(data_copy, context['lang_suffix'])
                context[entryname] = data_copy

    if data_modified:
        _write_json()


def _render_page(renderer, template, **context):
    _load_data()

    for lang, context in data_contexts.items():
        outfile = join(SITE_DIR, context['lang_dir'], template.name)
        mkdirp(dirname(outfile))
        prompt_render_html((context['lang'], outfile))
        template.stream(context).dump(outfile, "utf-8")


def _init_dirs():
    mkdirp(WEBASSETS_CACHE_DIR)
    mkdirp(SITE_DIR)
    # shutil.rmtree(join(SITE_ASSET_DIR, 'js'), ignore_errors=True)
    # shutil.rmtree(join(SITE_ASSET_DIR, 'css'), ignore_errors=True)


def _init_webassets(debug=False, generate=False):
    assets_env = Environment(directory=SITE_ASSET_DIR,
                             url=SITE_ASSET_URL_PREFIX,
                             cache=WEBASSETS_CACHE_DIR,
                             load_path=[SITE_ASSET_SRC_DIR])
    assets_env.debug = debug

    # js = Bundle('js/*.js', filters='jsmin', output='js/app_js.js')
    # css = Bundle('css/*.css', filters='cssmin', output='css/app_css.css')

    # assets_env.register('app_js', js)
    # assets_env.register('app_css', css)

    cmd = CommandLineEnvironment(assets_env, log)

    if generate:
        cmd.build()
        return assets_env

    Process(target=lambda: cmd.watch()).start()

    return assets_env


def create_site(debug=False, use_reloader=False, generate=False):
    _init_dirs()
    assets_env = _init_webassets(debug=debug, generate=generate)

    for lang, context in data_contexts.iteritems():
        context['printlog'] = _sp_printlog
        context['selectspeakers'] = _sp_selectspeakers

    site = make_site(searchpath=SITE_SRC_DIR,
                     staticpaths=[REL_SITE_ASSET_DIR],
                     outpath=SITE_DIR,
                     extensions=[AssetsExtension],
                     rules=[
                         ("[\w-]+\.html", _render_page)
                     ])

    # HACK: staticjinja没有提供 jinja2.Environment 的引用,
    # 因此这里只能访问其私有属性进行设置
    site._env.assets_environment = assets_env
    site.render(use_reloader=use_reloader)

    if generate:
        system('cp -R {} {}'.format(pipes.quote(SITE_ASSET_DIR),
                                    pipes.quote(EN_SITE_DIR)))


