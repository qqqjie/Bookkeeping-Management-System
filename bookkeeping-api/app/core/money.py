"""金额格式化：DECIMAL(15,2) 全程使用 Decimal，JSON 中以字符串输出，禁止 float。"""

from decimal import Decimal, ROUND_HALF_UP

_CENT = Decimal("0.01")


def format_money(value: Decimal | None) -> str:
    """格式化为两位小数字符串，如 "35.50"；None 视为 0。"""
    if value is None:
        return "0.00"
    return str(value.quantize(_CENT, rounding=ROUND_HALF_UP))


def format_percentage(part: Decimal, total: Decimal) -> str:
    """计算占比百分比（两位小数字符串）；分母为 0 时返回 "0.00"。"""
    if total == 0:
        return "0.00"
    return str((part / total * 100).quantize(_CENT, rounding=ROUND_HALF_UP))
