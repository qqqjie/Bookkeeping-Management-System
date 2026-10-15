"""交易路由：分页、筛选、倒序的增删改查。"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Annotated

from app.api.deps import get_current_user, get_db
from app.core.responses import PageVO, Resp
from app.models.user import User
from app.schemas.transaction import (
    TransactionQueryRequest,
    TransactionSaveRequest,
    TransactionVO,
)
from app.services import transaction as transaction_service

router = APIRouter(prefix="/transactions", tags=["交易"])


@router.post("", response_model=Resp[TransactionVO])
def create_transaction(
    request: TransactionSaveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Resp[TransactionVO]:
    return Resp.ok(transaction_service.create(db, current_user.user_id, request))


@router.get("", response_model=Resp[PageVO[TransactionVO]])
def list_transactions(
    query: Annotated[TransactionQueryRequest, Query()],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Resp[PageVO[TransactionVO]]:
    return Resp.ok(
        transaction_service.list_transactions(db, current_user.user_id, query)
    )


@router.get("/{transaction_id}", response_model=Resp[TransactionVO])
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Resp[TransactionVO]:
    return Resp.ok(
        transaction_service.get_by_id(db, current_user.user_id, transaction_id)
    )


@router.put("/{transaction_id}", response_model=Resp[TransactionVO])
def update_transaction(
    transaction_id: int,
    request: TransactionSaveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Resp[TransactionVO]:
    return Resp.ok(
        transaction_service.update(db, current_user.user_id, transaction_id, request)
    )


@router.delete("/{transaction_id}")
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Resp[None]:
    transaction_service.delete(db, current_user.user_id, transaction_id)
    return Resp.ok()
