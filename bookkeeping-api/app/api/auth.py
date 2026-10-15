"""认证路由：注册 / 登录。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.responses import Resp
from app.schemas.auth import LoginRequest, LoginResponse, RegisterRequest
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=Resp[LoginResponse])
def register(request: RegisterRequest, db: Session = Depends(get_db)) -> Resp[LoginResponse]:
    return Resp.ok(auth_service.register(db, request))


@router.post("/login", response_model=Resp[LoginResponse])
def login(request: LoginRequest, db: Session = Depends(get_db)) -> Resp[LoginResponse]:
    return Resp.ok(auth_service.login(db, request))
