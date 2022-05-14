# SPDX-FileCopyrightText: 2022 Claudio Cambra <claudio.cambra@gmail.com>
# SPDX-License-Identifier: LGPL-2.1-or-later

from dataclasses import dataclass
from datetime import datetime

from core.api.v1.post import PostBase

@dataclass
class PluginVersion:
    major: int
    minor: int
    micro: int


# Plugins should subclass this to implement plugins.
class PluginBase:
    def __init__(self):
        self.id: str
        self.name: str
        self.description: str
        self.author: str
        self.author_url: str
        self.plugin_url: str
        self.version: PluginVersion
        self.release_date: datetime

    def displayVersion(self):
        return f"{self.version.major}.{self.version.minor}.{self.version.micro}"


@dataclass
class PlatformAccountBase:
    id: int
    name: str


class PlatformPluginBase(PluginBase):
    def publish_post(self, post: PostBase, account_ids: tuple[int]):
        raise NotImplementedError
    
    def accounts(self) -> tuple[PlatformAccountBase]:
        raise NotImplementedError
    
    def account_ids(self) -> tuple[int]:
        raise NotImplementedError
    
    def add_account(self, account_details: dict) -> int:
        raise NotImplementedError
    
    def update_account(self, account_id: int, account_details: dict):
        raise NotImplementedError
    
    def delete_account(self, account_id: int):
        raise NotImplementedError