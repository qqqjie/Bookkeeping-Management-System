from functools import lru_cache
from urllib.parse import quote_plus

from pydantic import Field
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
