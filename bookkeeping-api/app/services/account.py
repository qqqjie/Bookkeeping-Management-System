"""账户业务逻辑：增删改查与实时余额。"""

from decimal import Decimal

from sqlalchemy import case, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import BusinessException, ErrorCode
from app.core.money import format_money
from app.models.account import Account
from app.models.enums import TransactionType
from app.models.transaction import Transaction
from app.schemas.account import AccountSaveRequest, AccountVO


def _to_vo(account: Account, current_balance: Decimal | None = None) -> AccountVO:
    return AccountVO(
        account_id=account.account_id,
        account_name=account.account_name,
        account_type=account.account_type,
        currency=account.currency,
        initial_balance=format_money(account.initial_balance),
        include_in_total=account.include_in_total,
        status=account.status,
        created_at=account.created_at,
        current_balance=format_money(current_balance) if current_balance is not None else None,
    )


def _get_owned(db: Session, user_id: int, account_id: int) -> Account:
    account = db.get(Account, account_id)
    if account is None or account.user_id != user_id:
        raise BusinessException(ErrorCode.NOT_FOUND, "账户不存在")
    return account


def _exists_by_name(db: Session, user_id: int, account_name: str, exclude_id: int | None) -> bool:
    stmt = select(Account.account_id).where(
        Account.user_id == user_id, Account.account_name == account_name
    )
    if exclude_id is not None:
        stmt = stmt.where(Account.account_id != exclude_id)
    return db.scalar(stmt) is not None


def _balance_map(db: Session, user_id: int) -> dict[int, Decimal]:
    """一次分组查询算清某用户全部账户的实时余额。"""
    income = func.coalesce(
        func.sum(
            case(
                (Transaction.transaction_type == TransactionType.INCOME, Transaction.amount),
                else_=0,
            )
        ),
        0,
    )
    expense = func.coalesce(
        func.sum(
            case(
                (Transaction.transaction_type == TransactionType.EXPENSE, Transaction.amount),
                else_=0,
            )
        ),
        0,
    )
    stmt = (
        select(Account.account_id, Account.initial_balance + income - expense)
        .select_from(Account)
        .outerjoin(Transaction, Transaction.account_id == Account.account_id)
        .where(Account.user_id == user_id)
        .group_by(Account.account_id, Account.initial_balance)
    )
    return {account_id: balance for account_id, balance in db.execute(stmt).all()}


def create(db: Session, user_id: int, request: AccountSaveRequest) -> AccountVO:
    if _exists_by_name(db, user_id, request.account_name, None):
        raise BusinessException(ErrorCode.CONFLICT, "账户名称已存在")
    account = Account(
        user_id=user_id,
        account_name=request.account_name,
        account_type=request.account_type,
        currency=request.currency or "CNY",
        initial_balance=request.initial_balance if request.initial_balance is not None else Decimal("0"),
        include_in_total=request.include_in_total if request.include_in_total is not None else 1,
        status=1,
    )
    db.add(account)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise BusinessException(ErrorCode.CONFLICT, "账户名称已存在")
    db.refresh(account)
    return _to_vo(account)


def get_by_id(db: Session, user_id: int, account_id: int) -> AccountVO:
    account = _get_owned(db, user_id, account_id)
    balance = _balance_map(db, user_id).get(account_id)
    return _to_vo(account, balance)


def list_accounts(db: Session, user_id: int) -> list[AccountVO]:
    stmt = (
        select(Account)
        .where(Account.user_id == user_id, Account.status == 1)
        .order_by(Account.created_at.desc(), Account.account_id.desc())
    )
    accounts = db.scalars(stmt).all()
    if not accounts:
        return []
    balances = _balance_map(db, user_id)
    return [_to_vo(account, balances.get(account.account_id)) for account in accounts]


def update(db: Session, user_id: int, account_id: int, request: AccountSaveRequest) -> AccountVO:
    account = _get_owned(db, user_id, account_id)
    if request.account_name != account.account_name and _exists_by_name(
        db, user_id, request.account_name, account_id
    ):
        raise BusinessException(ErrorCode.CONFLICT, "账户名称已存在")
    account.account_name = request.account_name
    account.account_type = request.account_type
    account.currency = request.currency or "CNY"
    account.initial_balance = (
        request.initial_balance if request.initial_balance is not None else Decimal("0")
    )
    account.include_in_total = (
        request.include_in_total if request.include_in_total is not None else 1
    )
    db.commit()
    db.refresh(account)
    return _to_vo(account)


def delete(db: Session, user_id: int, account_id: int) -> None:
    account = _get_owned(db, user_id, account_id)
    try:
        db.delete(account)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise BusinessException(ErrorCode.CONFLICT, "该账户下存在交易流水，无法删除")


def get_balance(db: Session, user_id: int, account_id: int) -> str:
    _get_owned(db, user_id, account_id)
    balance = _balance_map(db, user_id).get(account_id, Decimal("0"))
    return format_money(balance)
