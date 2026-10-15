"""认证相关请求/响应模型。"""

import re

from pydantic import field_validator

from app.schemas.common import CamelBaseModel
from app.schemas.user import UserVO

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_PASSWORD_PATTERN = re.compile(r"^(?=.*[a-zA-Z])(?=.*\d).+$")
_USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]{3,50}$")


class RegisterRequest(CamelBaseModel):
    username: str
    email: str
    password: str
    nickname: str | None = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        if not _USERNAME_PATTERN.match(value):
            raise ValueError("用户名只能包含字母、数字、下划线，长度 3-50")
        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if not _EMAIL_PATTERN.match(value):
            raise ValueError("邮箱格式不正确")
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not 8 <= len(value) <= 64:
            raise ValueError("密码长度必须在 8-64 之间")
        if not _PASSWORD_PATTERN.match(value):
            raise ValueError("密码必须同时包含字母和数字")
        return value

    @field_validator("nickname")
    @classmethod
    def validate_nickname(cls, value: str | None) -> str | None:
        if value is not None and len(value) > 50:
            raise ValueError("昵称长度不能超过 50")
        return value


class LoginRequest(CamelBaseModel):
    login_id: str
    password: str

    @field_validator("login_id")
    @classmethod
    def validate_login_id(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("登录账号不能为空")
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not value:
            raise ValueError("密码不能为空")
        return value


class LoginResponse(CamelBaseModel):
    token: str
    user: UserVO
