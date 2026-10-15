"""安全相关：bcrypt 密码哈希与 JWT 签发/解析。

关于技术栈偏差的说明（可验证事实）：原始需求指定 passlib[bcrypt]，
但 passlib 1.7.4 是 2020 年最后一版，其 bcrypt 后端在初始化自检
（detect_wrap_bug）时会调用 bcrypt.hashpw 并传入超过 72 字节的测试
口令，bcrypt 4.1 及以上版本对此抛出 ValueError，导致哈希直接失败；
而 bcrypt 4.0.1 没有 Python 3.13/3.14 的预编译 wheel，源码构建需要
Rust 工具链。因此本模块直接使用 bcrypt 5.x（bcrypt 算法的上游实现，
pip 包名 bcrypt），对外接口 hash_password/verify_password 保持不变，
安全强度与 passlib 的 bcrypt scheme 相同。
"""

import bcrypt
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

# bcrypt 仅使用口令的前 72 字节，超出部分按历史行为截断
_BCRYPT_MAX_BYTES = 72


def hash_password(raw_password: str) -> str:
    digest = raw_password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    return bcrypt.hashpw(digest, bcrypt.gensalt()).decode("utf-8")


def verify_password(raw_password: str, hashed_password: str) -> bool:
    digest = raw_password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    return bcrypt.checkpw(digest, hashed_password.encode("utf-8"))


def create_access_token(
    user_id: int,
    username: str,
    secret: str,
    expire_hours: int,
    algorithm: str = "HS256",
) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": username,
        "uid": user_id,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=expire_hours)).timestamp()),
    }
    return jwt.encode(payload, secret, algorithm=algorithm)


def decode_access_token(token: str, secret: str, algorithm: str = "HS256") -> dict:
    """解析并校验令牌；显式限定算法，缓解 JWT 算法混淆风险。"""
    return jwt.decode(token, secret, algorithms=[algorithm])


__all__ = [
    "JWTError",
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_access_token",
]
