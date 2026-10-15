"""数据库枚举：与 schema.sql 中 MySQL ENUM 的小写字面量一一对应。"""

from enum import Enum


class AccountType(str, Enum):
    CASH = "cash"
    DEBIT_CARD = "debit_card"
    CREDIT_CARD = "credit_card"
    ALIPAY = "alipay"
    WECHAT = "wechat"
    OTHER = "other"


class CategoryType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"
