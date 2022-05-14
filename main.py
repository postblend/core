# SPDX-FileCopyrightText: 2022 Claudio Cambra <claudio.cambra@gmail.com>
# SPDX-License-Identifier: LGPL-2.1-or-later

import definitions
from core.coredatabase import CoreDatabase
from core.pluginmanager import PluginManager
from core.api.v1.post import PostBase

# Init singleton instances
core_db = CoreDatabase.instance(definitions.DATABASE_PATH)
plugin_manager = PluginManager.instance()