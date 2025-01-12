"""Define user models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

import ciso8601
from mashumaro import DataClassDictMixin


@dataclass(frozen=True, kw_only=True)
class User(DataClassDictMixin):
    """Define a Notion user."""

    id: str
    uuid: str
    first_name: str
    last_name: str
    email: str
    phone_number: str | None
    role: str
    organization: str
    created_at: datetime = field(metadata={"deserialize": ciso8601.parse_datetime})
    updated_at: datetime = field(metadata={"deserialize": ciso8601.parse_datetime})


@dataclass(frozen=True, kw_only=True)
class AuthenticateViaCredentialsResponse(DataClassDictMixin):
    """Define an API response for authentication via credentials."""

    id: str
    token: str
