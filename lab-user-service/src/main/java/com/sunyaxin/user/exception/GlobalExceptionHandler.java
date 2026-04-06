package com.sunyaxin.user.exception;

import com.sunyaxin.common.result.Result;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.validation.BindException;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.util.stream.Collectors;

/**
 * 全局异常处理器
 * 统一捕获所有异常并返回标准的Result格式
 */
@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    /**
     * 处理@RequestBody参数校验异常（@Valid触发）
     */
    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public Result<Void> handleMethodArgumentNotValidException(MethodArgumentNotValidException e) {
        String errorMsg = e.getBindingResult().getFieldErrors().stream()
                .map(FieldError::getDefaultMessage)
                .collect(Collectors.joining("; "));

        log.warn("[参数校验失败] {}", errorMsg);
        return Result.error("参数校验失败：" + errorMsg);
    }

    /**
     * 处理@RequestParam/@PathVariable参数绑定异常
     */
    @ExceptionHandler(BindException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public Result<Void> handleBindException(BindException e) {
        String errorMsg = e.getFieldErrors().stream()
                .map(FieldError::getDefaultMessage)
                .collect(Collectors.joining("; "));

        log.warn("[参数绑定失败] {}", errorMsg);
        return Result.error("参数绑定失败：" + errorMsg);
    }

    /**
     * 处理非法参数异常
     */
    @ExceptionHandler(IllegalArgumentException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public Result<Void> handleIllegalArgumentException(IllegalArgumentException e) {
        log.warn("[非法参数] {}", e.getMessage());
        return Result.error(e.getMessage());
    }

    /**
     * 处理数据库异常
     */
    @ExceptionHandler(org.springframework.dao.DataAccessException.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public Result<Void> handleDataAccessException(org.springframework.dao.DataAccessException e) {
        log.error("[数据库操作失败] 异常类型: {}, 消息: {}", e.getClass().getName(), e.getMessage(), e);

        // 提供更友好的错误提示
        String errorMsg = "数据库操作失败";
        if (e.getMessage() != null) {
            if (e.getMessage().contains("Data too long") || e.getMessage().contains("Data truncation")) {
                errorMsg = "数据长度超出限制";
            } else if (e.getMessage().contains("Duplicate entry")) {
                errorMsg = "数据已存在（唯一约束冲突）";
            } else {
                errorMsg = "数据库操作失败：" + e.getMessage();
            }
        }
        return Result.error(errorMsg);
    }

    /**
     * [FIX] 处理404异常（Handler未找到）
     * application.yml配置了 throw-exception-if-no-handler-found: true
     * 需要此处理器来捕获NoHandlerFoundException并返回友好错误
     */
    @ExceptionHandler(org.springframework.web.servlet.NoHandlerFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public Result<Void> handleNoHandlerFoundException(org.springframework.web.servlet.NoHandlerFoundException e) {
        log.warn("[请求路径不存在] 请求方法: {}, 请求路径: {}", e.getHttpMethod(), e.getRequestURL());
        return Result.notFound("请求的资源不存在: " + e.getRequestURL());
    }

    /**
     * [FIX] 处理HTTP消息不可读异常（JSON解析失败等）
     */
    @ExceptionHandler(org.springframework.http.converter.HttpMessageNotReadableException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public Result<Void> handleHttpMessageNotReadableException(org.springframework.http.converter.HttpMessageNotReadableException e) {
        log.warn("[请求体解析失败] {}", e.getMessage());
        return Result.badRequest("请求体格式错误，请检查JSON格式是否正确");
    }

    /**
     * [FIX] 处理媒体类型不支持异常
     */
    @ExceptionHandler(org.springframework.web.HttpMediaTypeNotSupportedException.class)
    @ResponseStatus(HttpStatus.UNSUPPORTED_MEDIA_TYPE)
    public Result<Void> handleHttpMediaTypeNotSupportedException(org.springframework.web.HttpMediaTypeNotSupportedException e) {
        log.warn("[不支持的媒体类型]支持的类型: {}", e.getSupportedMediaTypes());
        return Result.error(415, "不支持的Content-Type: " + e.getContentType());
    }

    /**
     * 处理所有其他未捕获的异常
     */
    @ExceptionHandler(Exception.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public Result<Void> handleException(Exception e) {
        log.error("[系统内部错误] 异常类型: {}, 消息: {}", e.getClass().getName(), e.getMessage(), e);
        return Result.error("系统内部错误，请稍后重试");
    }
}
