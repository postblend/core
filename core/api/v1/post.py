# SPDX-FileCopyrightText: 2022 Claudio Cambra <claudio.cambra@gmail.com>
# SPDX-License-Identifier: LGPL-2.1-or-later

from dataclasses import dataclass
from enum import Enum
from typing import Any

@dataclass
class PostBase:
    title: str
    body: str


@dataclass
class PostResultStatus(Enum):
    SUCCESS = 0
    UNAVAILABLE = 1
    NETWORK_ERROR = 2
    BAD_CREDENTIALS = 3
    BAD_ACCOUNT = 4


@dataclass
class PostResult:
    status: PostResultStatus
    post_data: Any
