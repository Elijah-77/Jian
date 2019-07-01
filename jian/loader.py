# -*- encoding:utf-8 -*-
"""
@ Created by Seven on  2019/01/19 <https://7yue.in>
"""
from importlib import import_module

from .redprint import Redprint
from .db import db
from .plugin import Plugin
from .core import gigi_config


class Loader(object):
    plugin_path: dict = None

    def __init__(self, plugin_path):
        self.plugins = {}
        assert type(plugin_path) is dict, 'plugin_path must be a dict'
        self.plugin_path = plugin_path
        self.load_plugins_config()
        self.load_plugins()

    def load_plugins(self):
        for name, conf in self.plugin_path.items():
            enable = conf.get('enable', None)
            if enable:
                path = conf.get('path')
                # load plugin
                path and self._load_plugin(f'{path}.app.__init__', name)

    def load_plugins_config(self):
        for name, conf in self.plugin_path.items():
            path = conf.get('path', None)
            # load config
            self._load_config(f'{path}.config', name, conf)

    def _load_plugin(self, path, name):
        mod = import_module(path)
        plugin = Plugin(name=name)
        dic = mod.__dict__
        for key in dic.keys():
            if not key.startswith('_'):
                attr = dic[key]
                if isinstance(attr, Redprint):
                    plugin.add_controller(attr.name, attr)
                elif issubclass(attr, db.Model):
                    plugin.add_model(attr.__name__, attr)
                # 暂时废弃加载service，用处不大
                # elif issubclass(attr, ServiceInterface):
                #     plugin.add_service(attr.__name__, attr)
        self.plugins[plugin.name] = plugin

    def _load_config(self, config_path, name, conf):
        default_conf = {**conf} if conf else {}
        try:
            if config_path:
                mod = import_module(config_path)
                dic = mod.__dict__
                for key in dic.keys():
                    if not key.startswith('_'):
                        default_conf[key] = dic[key]
        except ModuleNotFoundError as e:
            pass
        gigi_config.add_plugin_config(plugin_name=name, obj=default_conf)
