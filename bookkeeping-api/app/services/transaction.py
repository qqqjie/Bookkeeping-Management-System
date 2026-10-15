"""交易业务逻辑：分页、筛选、倒序；所有查询强制带 user_id。"""

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.dates import month_range
from app.core.errors import BusinessException, ErrorCode
from app.core.money import format_money
from app.models.account import Account
from app.models.category import Category
from app.models.transaction import Transaction
from app.schemas.transaction import (
    TransactionQueryRequest,
    TransactionSaveRequest,
    TransactionVO,
)
from app.core.responses import PageVO


def _to_vo(transaction: Transaction) -> TransactionVO:
    return TransactionVO(
        transaction_id=transaction.transaction_id,
        account_id=transaction.account_id,
        category_id=transaction.category_id,
        transaction_type=transaction.transaction_type,
        amount=format_money(transaction.amount),
        transaction_time=transaction.transaction_time,
        remark=transaction.remark,
        created_at=transaction.created_at,
    )


def _validate_references(
    db: Session, user_id: int, account_id: int, category_id: int
) -> None:
    account = db.get(Account, account_id)
    if account is None or account.user_id != user_id:
        raise BusinessException(ErrorCode.NOT_FOUND, "账户不存在")
    category = db.get(Category, category_id)
    if (
        category is None
        or (category.user_id != user_id and category.user_id is not None)
    ):
        raise BusinessException(ErrorCode.NOT_FOUND, "分类不存在")


def _get_owned(db: Session, user_id: int, transaction_id: int) -> Transaction:
    transaction = db.get(Transaction, transaction_id)
    if transaction is None or transaction.user_id != user_id:
        raise BusinessException(ErrorCode.NOT_FOUND, "交易流水不存在")
    return transaction


def create(db: Session, user_id: int, request: TransactionSaveRequest) -> TransactionVO:
    _validate_references(db, user_id, request.account_id, request.category_id)
    transaction = Transaction(
        user_id=user_id,
        account_id=request.account_id,
        category_id=request.category_id,
        transaction_type=request.transaction_type,
        amount=request.amount,
        transaction_time=request.transaction_time,
        remark=request.remark,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return _to_vo(transaction)


def list_transactions(
    db: Session, user_id: int, query: TransactionQueryRequest
) -> PageVO[TransactionVO]:
    conditions = [Transaction.user_id == user_id]
    if query.account_id is not None:
        conditions.append(Transaction.account_id == query.account_id)
    if query.category_id is not None:
        conditions.append(Transaction.category_id == query.category_id)
    if query.transaction_type is not None:
        conditions.append(Transaction.transaction_type == query.transaction_type)
    if query.month is not None:
        start, end = month_range(query.month)
        conditions.append(Transaction.transaction_time >= start)
        conditions.append(Transaction.transaction_time < end)
    if query.start_time is not None:
        conditions.append(Transaction.transaction_time >= query.start_time)
    if query.end_time is not None:
        conditions.append(Transaction.transaction_time <= query.end_time)

    total = db.scalar(
        select(func.count()).select_from(Transaction).where(*conditions)
    )
    stmt = (
        select(Transaction)
        .where(*conditions)
        .order_by(Transaction.transaction_time.desc(), Transaction.transaction_id.desc())
        .limit(query.size)
        .offset((query.page - 1) * query.size)
    )
    records = [_to_vo(item) for item in db.scalars(stmt).all()]
    return PageVO.build(records, total or 0, query.page, query.size)


def get_by_id(db: Session, user_id: int, transaction_id: int) -> TransactionVO:
    return _to_vo(_get_owned(db, user_id, transaction_id))


def update(
    db: Session, user_id: int, transaction_id: int, request: TransactionSaveRequest
) -> TransactionVO:
    transaction = _get_owned(db, user_id, transaction_id)
    _validate_references(db, user_id, request.account_id, request.category_id)
    transaction.account_id = request.account_id
    transaction.category_id = request.category_id
    transaction.transaction_type = request.transaction_type
    transaction.amount = request.amount
    transaction.transaction_time = request.transaction_time
    transaction.remark = request.remark
    db.commit()
    db.refresh(transaction)
    return _to_vo(transaction)


def delete(db: Session, user_id: int, transaction_id: int) -> None:
    transaction = _get_owned(db, user_id, transaction_id)
    db.delete(transaction)
    db.commit()
