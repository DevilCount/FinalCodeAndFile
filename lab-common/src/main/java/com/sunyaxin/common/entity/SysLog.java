package com.sunyaxin.common.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.io.Serializable;
import java.time.LocalDateTime;

/**
 * 系统日志实体
 */
@Data
@TableName("sys_log")
public class SysLog implements Serializable {

    private static final long serialVersionUID = 1L;

    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 日志类型: OPERATE-操作日志 LOGIN-登录日志 EXCEPTION-异常日志
     */
    private String logType;

    /**
     * 操作名称
     */
    private String operation;

    /**
     * 请求方法
     */
    private String requestMethod;

    /**
     * 请求URL
     */
    private String requestUrl;

    /**
     * 请求参数
     */
    private String requestParams;

    /**
     * 返回结果
     */
    private String responseResult;

    /**
     * 请求耗时(毫秒)
     */
    private Long requestTime;

    /**
     * IP地址
     */
    private String ipAddress;

    /**
     * 用户代理
     */
    private String userAgent;

    /**
     * 操作用户ID
     */
    private Long userId;

    /**
     * 操作用户名
     */
    private String username;

    /**
     * 操作时间
     */
    private LocalDateTime operationTime;

    /**
     * 异常信息
     */
    private String errorMessage;
}
