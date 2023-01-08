# SPDX-FileCopyrightText: 2022 Claudio Cambra <claudio.cambra@gmail.com>
# SPDX-License-Identifier: LGPL-2.1-or-later

from dataclasses import dataclass
from datetime import datetime

from lib.account import AccountIdTuple
from lib.post import PostBase, PostResult

PluginId = str

"""
A simple data class that can be used to set plugin versions in a X.Y.Z format.
"""
@dataclass
class PluginVersion:
    major: int
    minor: int
    micro: int


"""
Base plugin class. 

Provides the basis for any type of PostBlend plugin. 
Do not subclass this if you are creating a platform plugin -- use PlatformPluginBase instead.
"""
class PluginBase:
    def __init__(self):
        self.id: PluginId
        self.name: str
        self.description: str
        self.author: str
        self.author_url: str
        self.plugin_url: str
        self.version: PluginVersion
        self.release_date: datetime

    def displayVersion(self):
        return f"{self.version.major}.{self.version.minor}.{self.version.micro}"


"""
Basic data class to base a platform account off of.

The id field is necessary for database identification; the name can be whatever you want.
"""
@dataclass
class PlatformAccountBase:
    id: int
    name: str


"""
Extends the basic PlatformAccountBase by adding a standard username and password.
"""
@dataclass
class BasicPlatformAccount(PlatformAccountBase):
    username: str
    password: str
    

"""
The base for a platform plugin. 

Each of the methods defined is used by Core to allow for posting.
"""
class PlatformPluginBase(PluginBase):
    def publish_post(self, post: PostBase, account_ids: AccountIdTuple) -> dict[int, PostResult]:
        raise NotImplementedError
    
    def accounts(self) -> tuple[PlatformAccountBase]:
        raise NotImplementedError
    
    def account_ids(self) -> AccountIdTuple:
        return [plugin.id for plugin in self.accounts()]
    
    def account(self, account_id: int):
        raise NotImplementedError
    
    def add_account(self, account_details: dict) -> int:
        raise NotImplementedError
    
    def update_account(self, account_id: int, account_details: dict):
        raise NotImplementedError
    
    def delete_account(self, account_id: int):
        raise NotImplementedError