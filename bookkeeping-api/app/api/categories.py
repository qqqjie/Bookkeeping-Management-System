"""分类路由：系统预设 + 用户自定义分类的增删改查。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.responses import Resp
from app.models.user import User
from app.schemas.category import CategorySaveRequest, CategoryVO
from app.services import category as category_service

router = APIRouter(prefix="/categories", tags=["分类"])


@router.post("", response_model=Resp[CategoryVO])
def create_category(
    request: CategorySaveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Resp[CategoryVO]:
    return Resp.ok(category_service.create(db, current_user.user_id, request))


@router.get("", response_model=Resp[list[CategoryVO]])
def list_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Resp[list[CategoryVO]]:
    return Resp.ok(category_service.list_categories(db, current_user.user_id))


@router.get("/{category_id}", response_model=Resp[CategoryVO])
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Resp[CategoryVO]:
    return Resp.ok(category_service.get_by_id(db, current_user.user_id, category_id))


@router.put("/{category_id}", response_model=Resp[CategoryVO])
def update_category(
    category_id: int,
    request: CategorySaveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Resp[CategoryVO]:
    return Resp.ok(
        category_service.update(db, current_user.user_id, category_id, request)
    )


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Resp[None]:
    category_service.delete(db, current_user.user_id, category_id)
    return Resp.ok()
