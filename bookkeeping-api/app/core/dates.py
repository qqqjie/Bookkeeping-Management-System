"""月份工具：YYYY-MM 与 [月初, 次月初) 区间的换算。"""

from datetime import datetime


def current_month() -> str:
    return datetime.now().strftime("%Y-%m")


def month_range(month: str) -> tuple[datetime, datetime]:
    """'2026-10' -> (2026-10-01 00:00:00, 2026-11-01 00:00:00)。"""
    year = int(month[0:4])
    month_number = int(month[5:7])
    if not 1 <= month_number <= 12:
        raise ValueError("月份必须在 01-12 之间")
    start = datetime(year, month_number, 1)
    if month_number == 12:
        end = datetime(year + 1, 1, 1)
    else:
        end = datetime(year, month_number + 1, 1)
    return start, end


def shift_month(year: int, month_number: int, offset: int) -> tuple[int, int]:
    """把 (年, 月) 平移 offset 个月，offset 可为负。"""
    total = year * 12 + (month_number - 1) + offset
    return total // 12, total % 12 + 1
