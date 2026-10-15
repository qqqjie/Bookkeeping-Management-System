"""统计模块响应模型：月度收支汇总、分类占比、近 N 个月趋势。"""

from app.schemas.common import CamelBaseModel


class MonthlySummaryVO(CamelBaseModel):
    month: str
    total_income: str
    total_expense: str
    net_amount: str
    income_count: int
    expense_count: int


class CategoryShareItemVO(CamelBaseModel):
    category_id: int
    category_name: str
    amount: str
    percentage: str


class TrendItemVO(CamelBaseModel):
    month: str
    total_income: str
    total_expense: str
