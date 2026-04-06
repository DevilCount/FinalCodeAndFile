package com.sunyaxin.common.result;

/**
 * 响应状态码枚举
 */
public enum ResultCode {

    // ========== 成功 ==========
    SUCCESS(200, "操作成功"),

    // ========== 客户端错误 4xx ==========
    BAD_REQUEST(400, "请求参数错误"),
    UNAUTHORIZED(401, "未授权，请先登录"),
    FORBIDDEN(403, "没有权限访问该资源"),
    NOT_FOUND(404, "请求资源不存在"),
    METHOD_NOT_ALLOWED(405, "请求方法不支持"),
    TOO_MANY_REQUESTS(429, "请求过于频繁，请稍后重试"),

    // ========== 服务器错误 5xx ==========
    INTERNAL_SERVER_ERROR(500, "服务器内部错误"),
    SERVICE_UNAVAILABLE(503, "服务暂不可用"),

    // ========== 业务错误 2xxx ==========
    USER_NOT_FOUND(2001, "用户不存在"),
    USER_DISABLED(2002, "用户已被禁用"),
    USER_PASSWORD_ERROR(2003, "用户名或密码错误"),
    USER_ALREADY_EXISTS(2004, "用户已存在"),
    TOKEN_EXPIRED(2005, "登录已过期，请重新登录"),
    TOKEN_INVALID(2006, "无效的Token"),

    SAMPLE_NOT_FOUND(3001, "标本不存在"),
    SAMPLE_STATUS_ERROR(3002, "标本状态错误"),
    SAMPLE_ALREADY_EXISTS(3003, "标本已存在"),

    REPORT_NOT_FOUND(4001, "报告不存在"),
    REPORT_NOT_REVIEWED(4002, "报告待审核"),
    REPORT_REJECTED(4003, "报告审核不通过"),

    DEVICE_NOT_FOUND(5001, "设备不存在"),
    DEVICE_OFFLINE(5002, "设备离线"),

    VALIDATION_ERROR(6001, "数据校验失败");

    private final Integer code;
    private final String message;

    ResultCode(Integer code, String message) {
        this.code = code;
        this.message = message;
    }

    public Integer getCode() {
        return code;
    }

    public String getMessage() {
        return message;
    }
}
