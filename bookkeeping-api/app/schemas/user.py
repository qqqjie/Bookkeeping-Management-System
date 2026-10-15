"""用户模块请求/响应模型。"""

import re
from datetime import datetime

from pydantic import field_validator

from app.schemas.common import CamelBaseModel

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class UserUpdateRequest(CamelBaseModel):
    email: str | None = None
    nickname: str | None = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        if value is not None and not _EMAIL_PATTERN.match(value):
            raise ValueError("邮箱格式不正确")
        return value

    @field_validator("nickname")
    @classmethod
    def validate_nickname(cls, value: str | None) -> str | None:
        if value is not None and len(value) > 50:
            raise ValueError("昵称长度不能超过 50")
        return value


class UserVO(CamelBaseModel):
    """用户视图对象：刻意不含 password_hash。"""

    user_id: int
    username: str
    email: str
    nickname: str | None
    status: int
    created_at: datetime
