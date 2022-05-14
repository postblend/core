# SPDX-FileCopyrightText: 2022 Claudio Cambra <claudio.cambra@gmail.com>
# SPDX-License-Identifier: LGPL-2.1-or-later

from core.api.v1.plugin import PlatformPluginBase
from core.coredatabase import CoreDatabase
from core.plugintools import PluginScanner
from core.api.v1.post import PostBase

class PluginManager:
    __instance = None

    @staticmethod
    def instance():
        if PluginManager.__instance == None:
            PluginManager()

        return PluginManager.__instance
    

    def __init__(self):
        if PluginManager.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            PluginManager.__instance = self

        self._database = CoreDatabase.instance()
        self.plugin_scanner = PluginScanner()

        self.available_plugins = self.load_available_plugins()
    
    def load_available_plugins(self):
        return self.plugin_scanner.available_plugins()
    
    # Provide a dict for the platform accounts with the keys being platform ids and the ints being account ids
    def publish_on_all(self, post: PostBase, platform_accounts: dict[str, int]):
        for plugin in self.available_plugins:
            if issubclass(plugin.__class__, PlatformPluginBase):
                plugin.publish_post(post)


    