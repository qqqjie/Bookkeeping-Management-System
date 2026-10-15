"""统计业务逻辑：月度收支汇总、分类占比、近 N 个月趋势。金额全程 Decimal。"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.dates import current_month, month_range, shift_month
from app.core.money import format_money, format_percentage
from app.models.category import Category
from app.models.enums import TransactionType
from app.models.transaction import Transaction
from app.schemas.stats import CategoryShareItemVO, MonthlySummaryVO, TrendItemVO

_MAX_TREND_MONTHS = 12


def monthly_summary(db: Session, user_id: int, month: str | None = None) -> MonthlySummaryVO:
    month = month or current_month()
    start, end = month_range(month)
    stmt = (
        select(
            Transaction.transaction_type,
            func.coalesce(func.sum(Transaction.amount), 0),
            func.count(),
        )
        .where(
            Transaction.user_id == user_id,
            Transaction.transaction_time >= start,
            Transaction.transaction_time < end,
        )
        .group_by(Transaction.transaction_type)
    )
    total_income = Decimal("0")
    total_expense = Decimal("0")
    income_count = 0
    expense_count = 0
    for tx_type, amount_sum, count in db.execute(stmt).all():
        if tx_type == TransactionType.INCOME:
            total_income, income_count = amount_sum, count
        else:
            total_expense, expense_count = amount_sum, count
    return MonthlySummaryVO(
        month=month,
        total_income=format_money(total_income),
        total_expense=format_money(total_expense),
        net_amount=format_money(total_income - total_expense),
        income_count=income_count,
        expense_count=expense_count,
    )


def category_share(
    db: Session,
    user_id: int,
    month: str | None = None,
    transaction_type: TransactionType = TransactionType.EXPENSE,
) -> list[CategoryShareItemVO]:
    month = month or current_month()
    start, end = month_range(month)
    stmt = (
        select(
            Category.category_id,
            Category.category_name,
            func.coalesce(func.sum(Transaction.amount), 0),
        )
        .select_from(Transaction)
        .join(Category, Category.category_id == Transaction.category_id)
        .where(
            Transaction.user_id == user_id,
            Transaction.transaction_type == transaction_type,
            Transaction.transaction_time >= start,
            Transaction.transaction_time < end,
        )
        .group_by(Category.category_id, Category.category_name)
        .order_by(func.sum(Transaction.amount).desc())
    )
    rows = db.execute(stmt).all()
    total = sum((amount for _, _, amount in rows), Decimal("0"))
    return [
        CategoryShareItemVO(
            category_id=category_id,
            category_name=category_name,
            amount=format_money(amount),
            percentage=format_percentage(amount, total),
        )
        for category_id, category_name, amount in rows
    ]


def trend(db: Session, user_id: int, months: int = 6) -> list[TrendItemVO]:
    months = max(1, min(_MAX_TREND_MONTHS, months))
    now = datetime.now()
    end_year, end_month = now.year, now.month
    start_year, start_month = shift_month(end_year, end_month, -(months - 1))
    start = datetime(start_year, start_month, 1)

    rows = db.execute(
        select(
            Transaction.transaction_time,
            Transaction.transaction_type,
            Transaction.amount,
        ).where(
            Transaction.user_id == user_id,
            Transaction.transaction_time >= start,
        )
    ).all()
    buckets: dict[str, dict[str, Decimal]] = {}
    for tx_time, tx_type, amount in rows:
        key = tx_time.strftime("%Y-%m")
        bucket = buckets.setdefault(key, {"income": Decimal("0"), "expense": Decimal("0")})
        if tx_type == TransactionType.INCOME:
            bucket["income"] += amount
        else:
            bucket["expense"] += amount

    result: list[TrendItemVO] = []
    year, month_number = start_year, start_month
    while (year, month_number) <= (end_year, end_month):
        key = f"{year:04d}-{month_number:02d}"
        bucket = buckets.get(key, {"income": Decimal("0"), "expense": Decimal("0")})
        result.append(
            TrendItemVO(
                month=key,
                total_income=format_money(bucket["income"]),
                total_expense=format_money(bucket["expense"]),
            )
        )
        year, month_number = shift_month(year, month_number, 1)
    return result
