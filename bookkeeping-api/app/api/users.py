"""用户路由：当前登录用户的查看与修改。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.responses import Resp
from app.models.user import User
from app.schemas.user import UserUpdateRequest, UserVO
from app.services import user as user_service

router = APIRouter(prefix="/users", tags=["用户"])


@router.get("/me", response_model=Resp[UserVO])
def get_current_user_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Resp[UserVO]:
    return Resp.ok(user_service.get_profile(db, current_user.user_id))


@router.put("/me", response_model=Resp[UserVO])
def update_current_user_profile(
    request: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Resp[UserVO]:
    return Resp.ok(user_service.update_profile(db, current_user.user_id, request))
