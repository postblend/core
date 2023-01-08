# SPDX-FileCopyrightText: 2023 Claudio Cambra <developer@claudiocambra.com>
# SPDX-License-Identifier: LGPL-2.1-or-later

from dataclasses import dataclass

AccountId = int
AccountIdTuple = tuple[int]

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
    