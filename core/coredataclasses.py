# SPDX-FileCopyrightText: 2022 Claudio Cambra <claudio.cambra@gmail.com>
# SPDX-License-Identifier: LGPL-2.1-or-later

from dataclasses import dataclass
import enum

DatabaseFieldDefinition = tuple[str, str, str] # Tuples with data info (field name, data type, constraints)

@dataclass
class UserAccountData:
    id: int
    account_name: str
    username: str
    key: str
    salt: str

@dataclass
class UserCredCheckResult(enum.Enum):
    UNKNOWN_USERNAME = 0
    INCORRECT_PASSWORD = 1
    CORRECT = 2