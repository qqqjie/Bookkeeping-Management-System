"""分类业务逻辑：系统预设 + 用户自定义，支持二级分类。"""

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import BusinessException, ErrorCode
from app.models.category import Category
from app.models.enums import CategoryType
from app.schemas.category import CategorySaveRequest, CategoryVO


def _to_vo(category: Category) -> CategoryVO:
    return CategoryVO(
        category_id=category.category_id,
        user_id=category.user_id,
        parent_id=category.parent_id,
        category_name=category.category_name,
        category_type=category.category_type,
        icon=category.icon,
        sort_order=category.sort_order,
        status=category.status,
        created_at=category.created_at,
    )


def _get_owned(db: Session, user_id: int, category_id: int) -> Category:
    category = db.get(Category, category_id)
    if category is None or category.user_id != user_id:
        raise BusinessException(ErrorCode.NOT_FOUND, "分类不存在")
    return category


def _exists_by_name(
    db: Session,
    user_id: int,
    category_name: str,
    category_type: CategoryType,
    exclude_id: int | None,
) -> bool:
    """同名同类型判重：同时覆盖用户自有分类与系统预设分类（user_id IS NULL），
    避免合并列表中出现两条同名分类。"""
    stmt = select(Category.category_id).where(
        Category.category_name == category_name,
        Category.category_type == category_type,
        (Category.user_id == user_id) | (Category.user_id.is_(None)),
    )
    if exclude_id is not None:
        stmt = stmt.where(Category.category_id != exclude_id)
    return db.scalar(stmt) is not None


def _validate_parent(
    db: Session, user_id: int, parent_id: int, category_type: CategoryType
) -> None:
    parent = db.get(Category, parent_id)
    if (
        parent is None
        or (parent.user_id != user_id and parent.user_id is not None)
        or parent.category_type != category_type
    ):
        raise BusinessException(
            ErrorCode.PARAM_INVALID, "父分类不存在、不属于当前用户或类型不一致"
        )


def create(db: Session, user_id: int, request: CategorySaveRequest) -> CategoryVO:
    if request.parent_id is not None:
        _validate_parent(db, user_id, request.parent_id, request.category_type)
    if _exists_by_name(db, user_id, request.category_name, request.category_type, None):
        raise BusinessException(ErrorCode.CONFLICT, "同名同类型分类已存在")
    category = Category(
        user_id=user_id,
        parent_id=request.parent_id,
        category_name=request.category_name,
        category_type=request.category_type,
        icon=request.icon,
        sort_order=request.sort_order if request.sort_order is not None else 0,
        status=1,
    )
    db.add(category)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise BusinessException(ErrorCode.CONFLICT, "同名同类型分类已存在")
    db.refresh(category)
    return _to_vo(category)


def get_by_id(db: Session, user_id: int, category_id: int) -> CategoryVO:
    return _to_vo(_get_owned(db, user_id, category_id))


def list_categories(db: Session, user_id: int) -> list[CategoryVO]:
    stmt = (
        select(Category)
        .where(
            Category.status == 1,
            (Category.user_id == user_id) | (Category.user_id.is_(None)),
        )
        .order_by(Category.sort_order.asc(), Category.category_id.asc())
    )
    return [_to_vo(category) for category in db.scalars(stmt).all()]


def update(
    db: Session, user_id: int, category_id: int, request: CategorySaveRequest
) -> CategoryVO:
    category = _get_owned(db, user_id, category_id)
    if request.parent_id is not None:
        if request.parent_id == category_id:
            raise BusinessException(ErrorCode.PARAM_INVALID, "父分类不能是自身")
        _validate_parent(db, user_id, request.parent_id, request.category_type)
    if request.category_name != category.category_name and _exists_by_name(
        db, user_id, request.category_name, request.category_type, category_id
    ):
        raise BusinessException(ErrorCode.CONFLICT, "同名同类型分类已存在")
    category.parent_id = request.parent_id
    category.category_name = request.category_name
    category.category_type = request.category_type
    category.icon = request.icon
    if request.sort_order is not None:
        category.sort_order = request.sort_order
    db.commit()
    db.refresh(category)
    return _to_vo(category)


def delete(db: Session, user_id: int, category_id: int) -> None:
    _get_owned(db, user_id, category_id)
    child_count = db.scalar(
        select(func.count()).select_from(Category).where(Category.parent_id == category_id)
    )
    if child_count:
        raise BusinessException(ErrorCode.CONFLICT, "该分类下存在子分类，无法删除")
    category = db.get(Category, category_id)
    try:
        db.delete(category)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise BusinessException(ErrorCode.CONFLICT, "该分类下存在交易流水，无法删除")
