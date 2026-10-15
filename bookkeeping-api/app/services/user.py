"""用户业务逻辑。"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import BusinessException, ErrorCode
from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserUpdateRequest, UserVO


def to_vo(user: User) -> UserVO:
    return UserVO(
        user_id=user.user_id,
        username=user.username,
        email=user.email,
        nickname=user.nickname,
        status=user.status,
        created_at=user.created_at,
    )


def get_by_id(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise BusinessException(ErrorCode.NOT_FOUND, "用户不存在")
    return user


def find_by_login_id(db: Session, login_id: str) -> User | None:
    stmt = (
        select(User)
        .where((User.username == login_id) | (User.email == login_id))
        .limit(1)
    )
    return db.scalar(stmt)


def exists_by_username(db: Session, username: str) -> bool:
    return db.scalar(select(User.user_id).where(User.username == username)) is not None


def exists_by_email(db: Session, email: str) -> bool:
    return db.scalar(select(User.user_id).where(User.email == email)) is not None


def create_user(
    db: Session,
    username: str,
    email: str,
    raw_password: str,
    nickname: str | None,
) -> User:
    user = User(
        username=username,
        email=email,
        password_hash=hash_password(raw_password),
        nickname=nickname or username,
        status=1,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_profile(db: Session, user_id: int) -> UserVO:
    return to_vo(get_by_id(db, user_id))


def update_profile(db: Session, user_id: int, request: UserUpdateRequest) -> UserVO:
    user = get_by_id(db, user_id)
    if request.email and request.email != user.email:
        if exists_by_email(db, request.email):
            raise BusinessException(ErrorCode.CONFLICT, "邮箱已被使用")
        user.email = request.email
    if request.nickname:
        user.nickname = request.nickname
    db.commit()
    db.refresh(user)
    return to_vo(user)
