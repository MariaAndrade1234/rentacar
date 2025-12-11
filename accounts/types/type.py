"""
Type definitions for accounts app.
"""

from typing import TypedDict, Optional
from datetime import datetime


class AccountType(TypedDict):
    """Type definition for account data."""
    id: Optional[int]
    username: str
    email: str
    first_name: str
    last_name: str
    is_active: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class AccountCreateType(TypedDict):
    """Type definition for account creation."""
    username: str
    email: str
    password: str
    first_name: str
    last_name: str


class AccountUpdateType(TypedDict, total=False):
    """Type definition for account update."""
    email: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    is_active: Optional[bool]
