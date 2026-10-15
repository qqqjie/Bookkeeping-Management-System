"""账户路由：增删改查与实时余额。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.responses import Resp
from app.models.user import User
from app.schemas.account import AccountSaveRequest, AccountVO
from app.services import account as account_service

router = APIRouter(prefix="/accounts", tags=["账户"])


@router.post("", response_model=Resp[AccountVO])
def create_account(
    request: AccountSaveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Resp[AccountVO]:
    return Resp.ok(account_service.create(db, current_user.user_id, request))


@router.get("", response_model=Resp[list[AccountVO]])
def list_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Resp[list[AccountVO]]:
    return Resp.ok(account_service.list_accounts(db, current_user.user_id))


@router.get("/{account_id}", response_model=Resp[AccountVO])
def get_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Resp[AccountVO]:
    return Resp.ok(account_service.get_by_id(db, current_user.user_id, account_id))


@router.get("/{account_id}/balance")
def get_account_balance(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Resp[str]:
    return Resp.ok(account_service.get_balance(db, current_user.user_id, account_id))


@router.put("/{account_id}", response_model=Resp[AccountVO])
def update_account(
    account_id: int,
    request: AccountSaveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Resp[AccountVO]:
    return Resp.ok(account_service.update(db, current_user.user_id, account_id, request))


@router.delete("/{account_id}")
def delete_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Resp[None]:
    account_service.delete(db, current_user.user_id, account_id)
    return Resp.ok()
