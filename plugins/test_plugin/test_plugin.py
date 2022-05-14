# SPDX-FileCopyrightText: 2022 Claudio Cambra <claudio.cambra@gmail.com>
# SPDX-License-Identifier: LGPL-2.1-or-later

from core.api.v1.plugin import PlatformPluginBase
from core.api.v1.post import PostBase
import core.api.v1.database as database

class TestPlugin(PlatformPluginBase):
    def __init__(self):
        self.id = "test_plugin"
        self.name = "Test Plugin"
        self.author = "Claudio Cambra"
        self.author_url = "https://claudiocambra.com"
        self.description = "A plugin to test our stuff :)"

        self.test_database()


    # TODO: Link with database test
    def account_ids(self) -> tuple[int]:
        return (0,)


    def publish_post(self, post: PostBase, account_ids: tuple[int]):
        print(f"""
            Post title: {post.title}
            Post body: {post.body}
        """)


    def test_database(self):
        self.plugin_table_name = "test_plugin_table"
        self.table_data_fields = (
            database.DatabaseFieldDefinition(("username_field", "TEXT", "")), 
            database.DatabaseFieldDefinition(("password_field", "TEXT", ""))
        )

        database.create_plugin_table(self.plugin_table_name, self.table_data_fields)

        test_user = {"username_field": "username", "password_field": "password"}
        row_id = database.add_plugin_data(self.plugin_table_name, test_user)
        print("AFTER INITIAL ADD: ", database.plugin_data(self.plugin_table_name))

        database.update_plugin_data(self.plugin_table_name, row_id, {"password_field": "new_password"})
        print("AFTER UPDATE OF INITIAL ADD: ", database.plugin_data(self.plugin_table_name))

        database.delete_plugin_data(self.plugin_table_name, row_id)
        print("AFTER DELETE OF INITIAL ADD: ", database.plugin_data(self.plugin_table_name))

        database.delete_plugin_table(self.plugin_table_name)