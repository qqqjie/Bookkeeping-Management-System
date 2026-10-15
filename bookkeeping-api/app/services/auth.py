"""认证业务逻辑：注册与登录。"""

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import BusinessException, ErrorCode
from app.core.security import create_access_token, verify_password
from app.schemas.auth import LoginRequest, LoginResponse, RegisterRequest
from app.services import user as user_service


def register(db: Session, request: RegisterRequest) -> LoginResponse:
    if user_service.exists_by_username(db, request.username):
        raise BusinessException(ErrorCode.CONFLICT, "用户名已被注册")
    if user_service.exists_by_email(db, request.email):
        raise BusinessException(ErrorCode.CONFLICT, "邮箱已被注册")
    user = user_service.create_user(
        db, request.username, request.email, request.password, request.nickname
    )
    return _build_login_response(user)


def login(db: Session, request: LoginRequest) -> LoginResponse:
    user = user_service.find_by_login_id(db, request.login_id)
    if user is None or not verify_password(request.password, user.password_hash):
        raise BusinessException(ErrorCode.UNAUTHORIZED, "登录账号或密码错误")
    if user.status != 1:
        raise BusinessException(ErrorCode.UNAUTHORIZED, "账号已被禁用")
    return _build_login_response(user)


def _build_login_response(user) -> LoginResponse:
    settings = get_settings()
    token = create_access_token(
        user_id=user.user_id,
        username=user.username,
        secret=settings.jwt_secret,
        expire_hours=settings.jwt_expire_hours,
        algorithm=settings.jwt_algorithm,
    )
    return LoginResponse(token=token, user=user_service.to_vo(user))
