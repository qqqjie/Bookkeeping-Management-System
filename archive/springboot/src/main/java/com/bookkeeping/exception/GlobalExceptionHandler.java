package com.bookkeeping.exception;

import com.bookkeeping.common.Result;
import lombok.extern.slf4j.Slf4j;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.BindException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<Result<Void>> handleBusinessException(BusinessException ex) {
        log.warn("业务异常: code={}, message={}", ex.getErrorCode().getCode(), ex.getMessage());
        HttpStatus httpStatus = HttpStatus.resolve(ex.getErrorCode().getCode());
        HttpStatus finalStatus = httpStatus != null ? httpStatus : HttpStatus.BAD_REQUEST;
        return ResponseEntity.status(finalStatus)
                .body(Result.fail(ex.getErrorCode().getCode(), ex.getMessage()));
    }

    @ExceptionHandler({MethodArgumentNotValidException.class, BindException.class})
    public ResponseEntity<Result<Void>> handleValidationException(Exception ex) {
        String message = ErrorCode.PARAM_INVALID.getMessage();
        if (ex instanceof MethodArgumentNotValidException argumentNotValidEx
                && argumentNotValidEx.getBindingResult().getFieldError() != null) {
            message = argumentNotValidEx.getBindingResult().getFieldError().getDefaultMessage();
        } else if (ex instanceof BindException bindEx && bindEx.getBindingResult().getFieldError() != null) {
            message = bindEx.getBindingResult().getFieldError().getDefaultMessage();
        }
        return ResponseEntity.badRequest()
                .body(Result.fail(ErrorCode.PARAM_INVALID.getCode(), message));
    }

    @ExceptionHandler(DataIntegrityViolationException.class)
    public ResponseEntity<Result<Void>> handleDataIntegrityViolation(DataIntegrityViolationException ex) {
        log.warn("数据完整性冲突: {}", ex.getMessage());
        return ResponseEntity.status(HttpStatus.CONFLICT)
                .body(Result.fail(ErrorCode.CONFLICT.getCode(), "数据冲突：可能存在重复数据或关联数据限制"));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<Result<Void>> handleException(Exception ex) {
        log.error("未处理的系统异常", ex);
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(Result.fail(ErrorCode.INTERNAL_ERROR));
    }
}
