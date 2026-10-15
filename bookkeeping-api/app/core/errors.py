from enum import IntEnum

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError


class ErrorCode(IntEnum):
    """与 Spring Boot 版保持一致的错误码。"""

    SUCCESS = 200
    PARAM_INVALID = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    INTERNAL_ERROR = 500


_ERROR_MESSAGES = {
    ErrorCode.SUCCESS: "操作成功",
    ErrorCode.PARAM_INVALID: "请求参数不合法",
    ErrorCode.UNAUTHORIZED: "未登录或登录已过期",
    ErrorCode.FORBIDDEN: "无权限访问该资源",
    ErrorCode.NOT_FOUND: "资源不存在",
    ErrorCode.CONFLICT: "数据冲突",
    ErrorCode.INTERNAL_ERROR: "服务器内部错误，请稍后重试",
}


class BusinessException(Exception):
    """业务异常，由全局处理器转换为统一错误响应。"""

    def __init__(self, error_code: ErrorCode, message: str | None = None):
        self.error_code = error_code
        self.message = message or _ERROR_MESSAGES[error_code]
        super().__init__(self.message)


def error_response(code: int, message: str, status: int) -> JSONResponse:
    return JSONResponse(status_code=status, content={"code": code, "message": message, "data": None})


async def business_exception_handler(_: Request, exc: BusinessException) -> JSONResponse:
    return error_response(int(exc.error_code), exc.message, int(exc.error_code))


async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    message = "请求参数不合法"
    if exc.errors():
        raw = exc.errors()[0].get("msg", message)
        message = raw.removeprefix("Value error, ")
    return error_response(int(ErrorCode.PARAM_INVALID), message, int(ErrorCode.PARAM_INVALID))


async def integrity_exception_handler(_: Request, __: IntegrityError) -> JSONResponse:
    return error_response(
        int(ErrorCode.CONFLICT), "数据冲突：可能存在重复数据或关联数据限制", int(ErrorCode.CONFLICT)
    )


async def unhandled_exception_handler(_: Request, __: Exception) -> JSONResponse:
    return error_response(int(ErrorCode.INTERNAL_ERROR), _ERROR_MESSAGES[ErrorCode.INTERNAL_ERROR], 500)


def register_exception_handlers(app) -> None:
    app.add_exception_handler(BusinessException, business_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
