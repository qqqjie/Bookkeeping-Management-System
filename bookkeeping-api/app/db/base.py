from sqlalchemy import BigInteger, Integer
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """SQLAlchemy 2.0 声明式基类。"""


# 主键类型：MySQL 上为 BIGINT（对应 schema.sql），SQLite（仅测试用）上为 INTEGER，
# 从而获得 rowid 自增别名；不影响 MySQL 行为。
BigIntPK = BigInteger().with_variant(Integer, "sqlite")
