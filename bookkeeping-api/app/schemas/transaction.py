"""交易模块请求/响应模型。"""

import re
from datetime import datetime
from decimal import Decimal

from pydantic import field_validator

from app.models.enums import TransactionType
from app.schemas.common import CamelBaseModel

_MONTH_PATTERN = re.compile(r"^\d{4}-\d{2}$")


class TransactionSaveRequest(CamelBaseModel):
    account_id: int
    category_id: int
    transaction_type: TransactionType
    amount: Decimal
    transaction_time: datetime
    remark: str | None = None

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, value: Decimal) -> Decimal:
        if value <= 0:
            raise ValueError("金额必须大于 0")
        if value != value.quantize(Decimal("0.01")):
            raise ValueError("金额最多两位小数")
        return value

    @field_validator("remark")
    @classmethod
    def validate_remark(cls, value: str | None) -> str | None:
        if value is not None and len(value) > 255:
            raise ValueError("备注长度不能超过 255")
        return value


class TransactionQueryRequest(CamelBaseModel):
    """交易列表查询参数：分页 + 月份/类型/账户/分类筛选。"""

    account_id: int | None = None
    category_id: int | None = None
    transaction_type: TransactionType | None = None
    month: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    page: int = 1
    size: int = 20

    @field_validator("month")
    @classmethod
    def validate_month(cls, value: str | None) -> str | None:
        if value is not None:
            if not _MONTH_PATTERN.match(value):
                raise ValueError("month 参数格式应为 YYYY-MM")
            month_number = int(value[5:7])
            if not 1 <= month_number <= 12:
                raise ValueError("month 参数月份必须在 01-12 之间")
        return value

    @field_validator("page")
    @classmethod
    def validate_page(cls, value: int) -> int:
        if value < 1:
            raise ValueError("页码不能小于 1")
        return value

    @field_validator("size")
    @classmethod
    def validate_size(cls, value: int) -> int:
        if not 1 <= value <= 100:
            raise ValueError("每页数量必须在 1-100 之间")
        return value


class TransactionVO(CamelBaseModel):
    transaction_id: int
    account_id: int
    category_id: int
    transaction_type: TransactionType
    amount: str
    transaction_time: datetime
    remark: str | None
    created_at: datetime
