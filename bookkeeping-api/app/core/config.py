from functools import lru_cache
from urllib.parse import quote_plus

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """运行配置，全部支持环境变量覆盖；密码等敏感项不落代码。"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = Field(default="please-change-me", validation_alias="MYSQL_PASSWORD")
    mysql_database: str = "bookkeeping"

    jwt_secret: str = Field(
        default="bookkeeping-dev-only-secret-key-must-be-at-least-32-bytes-long",
        validation_alias="JWT_SECRET",
    )
    jwt_expire_hours: int = Field(default=24, validation_alias="JWT_EXPIRE_HOURS")
    jwt_algorithm: str = "HS256"

    cors_origins: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        validation_alias="CORS_ORIGINS",
    )

    @field_validator("mysql_host")
    @classmethod
    def validate_mysql_host(cls, value: str) -> str:
        """规范主机地址：云托管控制台的内网地址常展示为 "IP:端口"，被整体复制进
        MYSQL_HOST 时会与 MYSQL_PORT 拼接成 "IP:3306:3306"，导致 SQLAlchemy
        解析连接串抛 ValueError。此处自动剥离子主机名末尾的数字端口段；
        仅处理恰好一个冒号且冒号后全为数字的情况，IPv6（多个冒号）不受影响。
        """
        host = value.strip()
        if host.count(":") == 1:
            name, _, maybe_port = host.partition(":")
            if maybe_port.isdigit():
                host = name
        return host

    @property
    def database_url(self) -> str:
        password = quote_plus(self.mysql_password)
        return (
            f"mysql+pymysql://{self.mysql_user}:{password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}?charset=utf8mb4"
        )

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
