"""分类模块请求/响应模型。"""

from datetime import datetime

from pydantic import field_validator

from app.models.enums import CategoryType
from app.schemas.common import CamelBaseModel


class CategorySaveRequest(CamelBaseModel):
    category_name: str
    category_type: CategoryType
    parent_id: int | None = None
    icon: str | None = None
    sort_order: int | None = None

    @field_validator("category_name")
    @classmethod
    def validate_category_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("分类名称不能为空")
        if len(value) > 50:
            raise ValueError("分类名称长度不能超过 50")
        return value

    @field_validator("icon")
    @classmethod
    def validate_icon(cls, value: str | None) -> str | None:
        if value is not None and len(value) > 50:
            raise ValueError("图标标识长度不能超过 50")
        return value


class CategoryVO(CamelBaseModel):
    category_id: int
    user_id: int | None
    parent_id: int | None
    category_name: str
    category_type: CategoryType
    icon: str | None
    sort_order: int
    status: int
    created_at: datetime
