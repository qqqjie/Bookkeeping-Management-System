"""Pydantic v2 请求/响应模型。"""

from app.schemas.account import AccountSaveRequest, AccountVO
from app.schemas.auth import LoginRequest, LoginResponse, RegisterRequest
from app.schemas.category import CategorySaveRequest, CategoryVO
from app.schemas.common import CamelBaseModel
from app.schemas.stats import CategoryShareItemVO, MonthlySummaryVO, TrendItemVO
from app.schemas.transaction import (
    TransactionQueryRequest,
    TransactionSaveRequest,
    TransactionVO,
)
from app.schemas.user import UserUpdateRequest, UserVO

__all__ = [
    "AccountSaveRequest",
    "AccountVO",
    "CamelBaseModel",
    "CategorySaveRequest",
    "CategoryShareItemVO",
    "CategoryVO",
    "LoginRequest",
    "LoginResponse",
    "MonthlySummaryVO",
    "RegisterRequest",
    "TransactionQueryRequest",
    "TransactionSaveRequest",
    "TransactionVO",
    "TrendItemVO",
    "UserUpdateRequest",
    "UserVO",
]
