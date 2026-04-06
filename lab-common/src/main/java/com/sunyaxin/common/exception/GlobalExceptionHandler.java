package com.sunyaxin.common.exception;

import com.sunyaxin.common.result.Result;
import com.sunyaxin.common.result.ResultCode;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.validation.BindException;
import org.springframework.validation.FieldError;
import org.springframework.web.HttpMediaTypeNotSupportedException;
import org.springframework.web.HttpRequestMethodNotSupportedException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.MissingServletRequestParameterException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;
import org.springframework.web.servlet.NoHandlerFoundException;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.ConstraintViolation;
import jakarta.validation.ConstraintViolationException;
import java.util.stream.Collectors;

/**
 * 全局异常处理器
 * 统一捕获所有异常并返回标准的Result格式
 * 
 * 处理的异常类型：
 * - BusinessException: 业务异常
 * - MethodArgumentNotValidException: @Valid @Validated 对象校验异常 (400)
 * - ConstraintViolationException: @Validated 单个参数校验异常 (400)
 * - BindException: 参数绑定异常 (400)
 * - MissingServletRequestParameterException: 缺少请求参数 (400)
 * - HttpMessageNotReadableException: 请求体格式错误 (400)
 * - HttpMediaTypeNotSupportedException: 不支持的媒体类型 (415)
 * - AccessDeniedException: 权限不足 (403)
 * - MethodArgumentTypeMismatchException: 参数类型不匹配 (400)
 * - HttpRequestMethodNotSupportedException: 请求方法不支持 (405)
 * - NoHandlerFoundException: 404资源不存在 (404)
 * - DataAccessException: 数据库访问异常 (500)
 * - RuntimeException: 运行时异常 (500)
 * - Exception: 兜底异常处理 (500) - 不暴露内部细节
 */
@RestControllerAdvice
public class GlobalExceptionHandler {

    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    /**
     * 处理业务异常
     */
    @ExceptionHandler(BusinessException.class)
    public Result<Void> handleBusinessException(BusinessException e, HttpServletRequest request) {
        log.warn("业务异常: {} - {}", e.getCode(), e.getMessage());
        Result<Void> result = Result.error(e.getMessage());
        result.setPath(request.getRequestURI());
        return result;
    }

    /**
     * 处理参数校验异常 - @Valid @Validated (对象校验)
     * 返回 400 + 字段错误详情
     */
    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public Result<Void> handleMethodArgumentNotValidException(MethodArgumentNotValidException e, HttpServletRequest request) {
        String errors = e.getBindingResult().getFieldErrors().stream()
                .map(fieldError -> String.format("%s: %s", fieldError.getField(), fieldError.getDefaultMessage()))
                .collect(Collectors.joining("; "));
        log.warn("参数校验失败 [{}]: {}", request.getRequestURI(), errors);
        Result<Void> result = Result.badRequest("参数校验失败: " + errors);
        result.setPath(request.getRequestURI());
        return result;
    }

    /**
     * 处理参数校验异常 - @Validated (单个参数校验)
     */
    @ExceptionHandler(ConstraintViolationException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public Result<Void> handleConstraintViolationException(ConstraintViolationException e, HttpServletRequest request) {
        String errors = e.getConstraintViolations().stream()
                .map(violation -> {
                    // 提取字段名（从路径最后一个部分）
                    String propertyPath = violation.getPropertyPath().toString();
                    String fieldName = propertyPath.substring(propertyPath.lastIndexOf('.') + 1);
                    return String.format("%s: %s", fieldName, violation.getMessage());
                })
                .collect(Collectors.joining("; "));
        log.warn("参数约束校验失败 [{}]: {}", request.getRequestURI(), errors);
        Result<Void> result = Result.badRequest("参数校验失败: " + errors);
        result.setPath(request.getRequestURI());
        return result;
    }

    /**
     * 处理参数绑定异常
     */
    @ExceptionHandler(BindException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public Result<Void> handleBindException(BindException e, HttpServletRequest request) {
        String errors = e.getBindingResult().getFieldErrors().stream()
                .map(fieldError -> String.format("%s: %s", fieldError.getField(), fieldError.getDefaultMessage()))
                .collect(Collectors.joining("; "));
        log.warn("参数绑定失败 [{}]: {}", request.getRequestURI(), errors);
        Result<Void> result = Result.badRequest("参数绑定失败: " + errors);
        result.setPath(request.getRequestURI());
        return result;
    }

    /**
     * 处理缺少请求参数异常
     * 返回 400 + 缺失参数名
     */
    @ExceptionHandler(MissingServletRequestParameterException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public Result<Void> handleMissingServletRequestParameterException(MissingServletRequestParameterException e, HttpServletRequest request) {
        String message = String.format("缺少必需参数: %s (类型: %s)", e.getParameterName(), e.getParameterType());
        log.warn("{} [{}]", message, request.getRequestURI());
        Result<Void> result = Result.badRequest(message);
        result.setPath(request.getRequestURI());
        return result;
    }

    /**
     * 处理HTTP消息不可读异常（JSON解析错误等）
     * 返回 400 + "请求体格式错误"
     */
    @ExceptionHandler(HttpMessageNotReadableException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public Result<Void> handleHttpMessageNotReadableException(HttpMessageNotReadableException e, HttpServletRequest request) {
        String message = "请求体格式错误";
        if (e.getMessage() != null) {
            if (e.getMessage().contains("Required request body is missing")) {
                message = "请求体不能为空";
            } else if (e.getMessage().contains("JSON parse error")) {
                message = "JSON格式错误";
            }
        }
        log.warn("{} [{}]", message, request.getRequestURI());
        Result<Void> result = Result.badRequest(message);
        result.setPath(request.getRequestURI());
        return result;
    }

    /**
     * 处理不支持的媒体类型异常
     * 返回 415
     */
    @ExceptionHandler(HttpMediaTypeNotSupportedException.class)
    @ResponseStatus(HttpStatus.UNSUPPORTED_MEDIA_TYPE)
    public Result<Void> handleHttpMediaTypeNotSupportedException(HttpMediaTypeNotSupportedException e, HttpServletRequest request) {
        String message = String.format("不支持的媒体类型: %s", e.getContentType());
        log.warn("{} [{}]", message, request.getRequestURI());
        Result<Void> result = Result.error(415, message);
        result.setPath(request.getRequestURI());
        return result;
    }

    /**
     * 处理权限不足异常
     * 返回 403 + "权限不足"
     */
    @ExceptionHandler(AccessDeniedException.class)
    @ResponseStatus(HttpStatus.FORBIDDEN)
    public Result<Void> handleAccessDeniedException(AccessDeniedException e, HttpServletRequest request) {
        log.warn("权限不足 [{}]: {}", request.getRequestURI(), e.getMessage());
        Result<Void> result = Result.forbidden();
        result.setPath(request.getRequestURI());
        return result;
    }

    /**
     * 处理参数类型不匹配异常
     */
    @ExceptionHandler(MethodArgumentTypeMismatchException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public Result<Void> handleMethodArgumentTypeMismatchException(MethodArgumentTypeMismatchException e, HttpServletRequest request) {
        String message = String.format("参数'%s'类型错误: 期望类型%s", e.getName(),
                e.getRequiredType() != null ? e.getRequiredType().getSimpleName() : "未知");
        log.warn("{} [{}]", message, request.getRequestURI());
        Result<Void> result = Result.badRequest(message);
        result.setPath(request.getRequestURI());
        return result;
    }

    /**
     * 处理请求方法不支持异常
     */
    @ExceptionHandler(HttpRequestMethodNotSupportedException.class)
    @ResponseStatus(HttpStatus.METHOD_NOT_ALLOWED)
    public Result<Void> handleHttpRequestMethodNotSupportedException(HttpRequestMethodNotSupportedException e, HttpServletRequest request) {
        String message = String.format("请求方法'%s'不支持, 支持的方法: %s", e.getMethod(), e.getSupportedHttpMethods());
        log.warn("{} [{}]", message, request.getRequestURI());
        Result<Void> result = Result.error(ResultCode.METHOD_NOT_ALLOWED.getCode(), message);
        result.setPath(request.getRequestURI());
        return result;
    }

    /**
     * 处理404异常
     */
    @ExceptionHandler(NoHandlerFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public Result<Void> handleNoHandlerFoundException(NoHandlerFoundException e, HttpServletRequest request) {
        String message = String.format("请求资源不存在: %s %s", e.getHttpMethod(), e.getRequestURL());
        log.warn("{} [{}]", message, request.getRequestURI());
        Result<Void> result = Result.notFound(message);
        result.setPath(request.getRequestURI());
        return result;
    }

    /**
     * 处理数据库访问异常
     * 不暴露内部细节给客户端
     */
    @ExceptionHandler(org.springframework.dao.DataAccessException.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public Result<Void> handleDataAccessException(org.springframework.dao.DataAccessException e, HttpServletRequest request) {
        log.error("数据库操作失败 [{}] - {}", request.getRequestURI(), e.getMessage());
        Result<Void> result = Result.error("数据操作失败，请稍后重试");
        result.setPath(request.getRequestURI());
        return result;
    }

    /**
     * 处理运行时异常
     */
    @ExceptionHandler(RuntimeException.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public Result<Void> handleRuntimeException(RuntimeException e, HttpServletRequest request) {
        log.error("运行时异常 [{}] - {}", request.getRequestURI(), e.getMessage(), e);
        Result<Void> result = Result.error(500, "系统繁忙，请稍后重试");
        result.setPath(request.getRequestURI());
        return result;
    }

    /**
     * 处理所有未捕获的异常（兜底）
     * 注意：不暴露内部异常细节给客户端，只返回通用错误信息
     */
    @ExceptionHandler(Exception.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public Result<Void> handleException(Exception e, HttpServletRequest request) {
        log.error("未捕获异常 [{}] - 类型: {}, 消息: {}",
                request.getRequestURI(), e.getClass().getName(), e.getMessage(), e);
        Result<Void> result = Result.error(500, "系统繁忙，请稍后重试");
        result.setPath(request.getRequestURI());
        return result;
    }
}
