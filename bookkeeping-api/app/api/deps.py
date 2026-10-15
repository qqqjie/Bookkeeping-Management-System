"""公共依赖：数据库会话与当前登录用户。"""

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import BusinessException, ErrorCode
from app.core.security import JWTError, decode_access_token
from app.db.session import get_db
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """从 Authorization: Bearer <token> 解析当前用户；无效则 401。"""
    if credentials is None:
        raise BusinessException(ErrorCode.UNAUTHORIZED)
    settings = get_settings()
    try:
        payload = decode_access_token(
            credentials.credentials, settings.jwt_secret, settings.jwt_algorithm
        )
    except JWTError:
        raise BusinessException(ErrorCode.UNAUTHORIZED)
    username = payload.get("sub")
    if not username:
        raise BusinessException(ErrorCode.UNAUTHORIZED)
    user = db.scalar(select(User).where(User.username == username))
    if user is None or user.status != 1:
        raise BusinessException(ErrorCode.UNAUTHORIZED)
    return user
