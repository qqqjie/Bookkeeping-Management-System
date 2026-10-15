"""统计路由：月度收支汇总、分类占比、近 N 个月趋势。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.responses import Resp
from app.models.enums import TransactionType
from app.models.user import User
from app.schemas.stats import CategoryShareItemVO, MonthlySummaryVO, TrendItemVO
from app.services import stats as stats_service

router = APIRouter(prefix="/stats", tags=["统计"])


@router.get("/monthly-summary", response_model=Resp[MonthlySummaryVO])
def get_monthly_summary(
    month: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Resp[MonthlySummaryVO]:
    return Resp.ok(stats_service.monthly_summary(db, current_user.user_id, month))


@router.get("/category-share", response_model=Resp[list[CategoryShareItemVO]])
def get_category_share(
    month: str | None = None,
    transaction_type: TransactionType = TransactionType.EXPENSE,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Resp[list[CategoryShareItemVO]]:
    return Resp.ok(
        stats_service.category_share(db, current_user.user_id, month, transaction_type)
    )


@router.get("/trend", response_model=Resp[list[TrendItemVO]])
def get_trend(
    months: int = 6,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Resp[list[TrendItemVO]]:
    return Resp.ok(stats_service.trend(db, current_user.user_id, months))
