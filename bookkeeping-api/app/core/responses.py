from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Resp(BaseModel, Generic[T]):
    """统一响应体：{"code": 200, "message": "...", "data": ...}。"""

    code: int = 200
    message: str = "操作成功"
    data: T | None = None

    @classmethod
    def ok(cls, data: T | None = None, message: str = "操作成功") -> "Resp[T]":
        return cls(code=200, message=message, data=data)


class PageVO(BaseModel, Generic[T]):
    """分页响应体。"""

    records: list[T] = []
    total: int = 0
    page: int = 1
    size: int = 20
    pages: int = 0

    @classmethod
    def build(cls, records: list[T], total: int, page: int, size: int) -> "PageVO[T]":
        pages = (total + size - 1) // size if size > 0 else 0
        return cls(records=records, total=total, page=page, size=size, pages=pages)
