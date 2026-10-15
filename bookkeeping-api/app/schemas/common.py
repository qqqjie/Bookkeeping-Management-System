"""Schema 基类：JSON 字段统一 camelCase，与 Spring Boot 版保持一致。"""

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelBaseModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
