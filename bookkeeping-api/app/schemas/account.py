"""账户模块请求/响应模型。"""

import re
from datetime import datetime
from decimal import Decimal

from pydantic import field_validator

from app.models.enums import AccountType
from app.schemas.common import CamelBaseModel

_CURRENCY_PATTERN = re.compile(r"^[A-Z]{3}$")


class AccountSaveRequest(CamelBaseModel):
    account_name: str
    account_type: AccountType
    currency: str | None = None
    initial_balance: Decimal | None = None
    include_in_total: int | None = None

    @field_validator("account_name")
    @classmethod
    def validate_account_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("账户名称不能为空")
        if len(value) > 50:
            raise ValueError("账户名称长度不能超过 50")
        return value

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, value: str | None) -> str | None:
        if value is not None and not _CURRENCY_PATTERN.match(value):
            raise ValueError("币种须为三位大写字母，如 CNY")
        return value

    @field_validator("initial_balance")
    @classmethod
    def validate_initial_balance(cls, value: Decimal | None) -> Decimal | None:
        if value is not None:
            if value < 0:
                raise ValueError("初始余额不能为负数")
            if value != value.quantize(Decimal("0.01")):
                raise ValueError("初始余额最多两位小数")
        return value

    @field_validator("include_in_total")
    @classmethod
    def validate_include_in_total(cls, value: int | None) -> int | None:
        if value is not None and value not in (0, 1):
            raise ValueError("includeInTotal 只能为 0 或 1")
        return value


class AccountVO(CamelBaseModel):
    """账户视图对象；金额字段为字符串，保证 JSON 中不损失精度。"""

    account_id: int
    account_name: str
    account_type: AccountType
    currency: str
    initial_balance: str
    include_in_total: int
    status: int
    created_at: datetime
    current_balance: str | None = None
