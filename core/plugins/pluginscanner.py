# SPDX-FileCopyrightText: 2022 Claudio Cambra <claudio.cambra@gmail.com>
# SPDX-License-Identifier: LGPL-2.1-or-later

from importlib import import_module
import inspect
import os
import pkgutil

from lib.plugin import PlatformPluginBase, PluginBase
from core.definitions import PLUGINS_PKG_DIR

class PluginScanner:
    def _available_plugins_at_path(self, plugin_pkg: str, checked_paths: list) -> list:
        if plugin_pkg == "__pycache__":
            return []

        available_plugins = []
        imported = import_module(plugin_pkg)

        # First scan the python files
        for loader, plugin_name, ispkg in pkgutil.iter_modules(imported.__path__, imported.__name__ + '.'):
            # This is a file and not a folder
            print(plugin_name)
            if not ispkg:
                plugin_module = import_module(plugin_name)
                module_members = inspect.getmembers(plugin_module)

                # In all the member values we are looking for the plugin class
                for (member_name, member_value) in module_members:
                    if inspect.isclass(member_value) and \
                        issubclass(member_value, PluginBase) and \
                        member_value is not PluginBase and \
                        member_value is not PlatformPluginBase:

                        print(f"Found plugin: '{plugin_name}' with main plugin class '{member_name}'")
                        # Add an instance of this class to our available plugins
                        available_plugins.append(member_value())
            
        # Go a level deeper into subfolders
        # Do this by recursively calling this function on the subfolders 
        imported_paths = []
        # If __path__ is a string then it is one path, otherwise it is a collection of several
        if isinstance(imported.__path__, str):
            imported_paths.append(imported.__path__)
        else:
            imported_paths.extend([path for path in imported.__path__])
        
        for pkg_path in imported_paths:
            if pkg_path not in checked_paths:
                checked_paths.append(pkg_path)

                # Get all subdirectory of the current package path directory
                child_paths = [path for path in os.listdir(pkg_path) if os.path.isdir(os.path.join(pkg_path, path))]

                for child_path in child_paths:
                    name_with_parents = imported.__name__ + '.' + child_path
                    available_plugins += self._available_plugins_at_path(name_with_parents, checked_paths)

        return available_plugins


    def available_plugins(self) -> tuple:
        return tuple(self._available_plugins_at_path(PLUGINS_PKG_DIR, []))