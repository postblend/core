# SPDX-FileCopyrightText: 2022 Claudio Cambra <claudio.cambra@gmail.com>
# SPDX-License-Identifier: LGPL-2.1-or-later

import core.definitions
from core.coredatabase import CoreDatabase
from core.pluginmanager import PluginManager
from core.api.v1.post import PostBase

# Init singleton instances
core_db = CoreDatabase.instance(core.definitions.DATABASE_PATH)
assert core_db

plugin_manager = PluginManager.instance()
assert plugin_manager

test_post = PostBase
test_post.title = "Test post"
test_post.body = "Test post body!"

plugin_manager.publish_on_all(test_post)