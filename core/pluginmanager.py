# SPDX-FileCopyrightText: 2022 Claudio Cambra <claudio.cambra@gmail.com>
# SPDX-License-Identifier: LGPL-2.1-or-later

from core.api.v1.plugin import PlatformPluginBase
from core.coredatabase import CoreDatabase
from core.plugintools import PluginScanner
from core.api.v1.post import PostBase, PostResult

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

        self._available_plugins = []

    
    def load_available_plugins(self) -> tuple:
        self._available_plugins = self.plugin_scanner.available_plugins()
        return self._available_plugins


    def available_plugins(self) -> tuple:
        return self._available_plugins


    def available_plugin_ids(self) -> tuple:
        return tuple([plugin.id for plugin in self.available_plugins()])

    
    # Provide a dict for the platform accounts with the keys being platform ids and the ints being account ids
    def publish_post(self, post: PostBase, platform_accounts: dict[str, list[int]]) -> dict[str, dict[int, PostResult]]:
        posting_result_dict = {}

        for plugin in self.available_plugins():
            if issubclass(plugin.__class__, PlatformPluginBase) and plugin.id in platform_accounts:
                result = plugin.publish_post(post, platform_accounts[plugin.id])
                posting_result_dict[plugin.id] = result

        return posting_result_dict


    def publish_post_on_all(self, post: PostBase):
        plugin_ids = self.available_plugin_ids()
        plugin_accounts = [plugin.accounts() for plugin in self.available_plugins()]
        return self.publish_post(post, dict(zip(plugin_ids, plugin_accounts)))


    