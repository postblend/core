# SPDX-FileCopyrightText: 2022 Claudio Cambra <claudio.cambra@gmail.com>
# SPDX-License-Identifier: LGPL-2.1-or-later

import core.definitions
from core.coredatabase import CoreDatabase
from core.pluginmanager import PluginManager
from core.api.v1.post import PostBase, PostResult, PostResultStatus
from core.api.v1.plugin import PlatformPluginBase, BasicPlatformAccount
import core.api.v1.database as database


class TestPlugin(PlatformPluginBase):
    def __init__(self):
        self.id = "test_plugin"
        self.name = "Test Plugin"
        self.author = "Claudio Cambra"
        self.author_url = "https://claudiocambra.com"
        self.description = "A plugin to test our stuff :)"

        self.username_field = "username_field"
        self.password_field = "password_field" # TODO: IMPLEMENT ENCRYPTING      


    def init_database_data(self):
        self.plugin_table_name = "test_plugin_table"
        self.table_data_fields = (
            database.DatabaseFieldDefinition((self.username_field, "TEXT", "")), 
            database.DatabaseFieldDefinition((self.password_field, "TEXT", ""))
        )

        database.create_plugin_table(self.plugin_table_name, self.table_data_fields)

        test_user = {self.username_field: "username", self.password_field: "password"}
        row_id = self.add_account(test_user)
        print("AFTER INITIAL ADD: ", self.accounts())

        self.update_account(row_id, {self.password_field: "new_password"})
        print("AFTER UPDATE OF INITIAL ADD: ", self.accounts())


    def cleanup_database_data(self):
        account_ids = self.account_ids()

        for id in account_ids:
            self.delete_account(id)

        print("AFTER DELETE OF ACCOUNTS: ", self.accounts())

        database.delete_plugin_table(self.plugin_table_name)


    def accounts(self) -> tuple:
        accounts_data = database.plugin_data(self.plugin_table_name)
        accounts_tuple = []

        for account in accounts_data:
            basic_plat_acc = BasicPlatformAccount(
                account["id"], 
                account[self.username_field], 
                account[self.username_field], 
                account[self.password_field]
            )

            accounts_tuple.append(basic_plat_acc)

        return tuple(accounts_tuple)


    def account(self, account_id: int) -> BasicPlatformAccount:
        account = database.plugin_data_row(self.plugin_table_name, account_id)
        
        if not account:
            return None

        return BasicPlatformAccount(
            account["id"], 
            account[self.username_field], 
            account[self.username_field], 
            account[self.password_field]
        )

    
    def add_account(self, account_details: dict) -> int:
        return database.add_plugin_data(self.plugin_table_name, account_details)


    def update_account(self, account_id: int, account_details: dict):
        database.update_plugin_data(self.plugin_table_name, account_id, account_details)


    def delete_account(self, account_id: int):
        database.delete_plugin_data(self.plugin_table_name, account_id)


    def publish_post(self, post: PostBase, account_ids: tuple) -> dict[int, PostResult]:
        posting_results_dict = {}

        for acc_id in account_ids:
            account_details = self.account(acc_id)

            if account_details:
                printString = f"""
                    Post for account '{account_details.name}'

                    Post title: {post.title}
                    Post body: {post.body}
                """
                print (printString)
                posting_results_dict[acc_id] = PostResult(status = PostResultStatus.SUCCESS, post_data = printString)
            else:
                print(f"Account with id '{acc_id}' does not exist for this plugin.")
                posting_results_dict[acc_id] = PostResult(status = PostResultStatus.BAD_ACCOUNT, post_data = None)
        
        return posting_results_dict
                

print("Starting platform plugin test.")

# Init singleton instances
core_db = CoreDatabase.instance(core.definitions.DATABASE_PATH)
assert core_db

plugin_manager = PluginManager.instance()
assert plugin_manager

test_plugin_instance = TestPlugin()
test_plugin_instance.init_database_data()

plugin_manager._available_plugins.append(test_plugin_instance)

test_post = PostBase(title = "Test post", body = ("Test post body!"))

posting_results = plugin_manager.publish_post(post = test_post, platform_accounts = {"test_plugin": (0,1)})
assert posting_results["test_plugin"][0].status == PostResultStatus.BAD_ACCOUNT
assert posting_results["test_plugin"][1].status == PostResultStatus.SUCCESS

test_plugin_instance.cleanup_database_data()