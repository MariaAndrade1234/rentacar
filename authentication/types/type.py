from typing import TypedDict, Optional


class LoginType(TypedDict):
    username: str
    password: str


class RegisterType(TypedDict):
    username: str
    email: str
    password: str
    first_name: Optional[str]
    last_name: Optional[str]


class TokenType(TypedDict):
    access: str
    refresh: str
    token_type: str
    expires_in: int


class PasswordChangeType(TypedDict):
    old_password: str
    new_password: str
    confirm_password: str


class PasswordResetType(TypedDict):
    email: str


class PasswordResetConfirmType(TypedDict):
    token: str
    new_password: str
    confirm_password: str
