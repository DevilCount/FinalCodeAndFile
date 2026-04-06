package com.sunyaxin.common.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.io.Serializable;
import java.time.LocalDateTime;

/**
 * 操作日志实体 - 用于记录关键业务操作
 */
@Data
@TableName("operation_log")
public class OperationLog implements Serializable {

    private static final long serialVersionUID = 1L;

    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 操作用户ID
     */
    private Long userId;

    /**
     * 操作用户名
     */
    private String username;

    /**
     * 操作人真实姓名
     */
    private String realName;

    /**
     * 操作模块(标本/报告/用户等)
     */
    private String module;

    /**
     * 操作类型
     */
    private String operationType;

    /**
     * 操作描述
     */
    private String operationDesc;

    /**
     * 操作对象类型(标本/报告等)
     */
    private String targetType;

    /**
     * 操作对象ID
     */
    private Long targetId;

    /**
     * 操作对象编号
     */
    private String targetNo;

    /**
     * 请求IP
     */
    private String requestIp;

    /**
     * 请求方法
     */
    private String requestMethod;

    /**
     * 请求参数
     */
    private String requestParams;

    /**
     * 返回结果
     */
    private String responseResult;

    /**
     * 操作状态(SUCCESS/FAIL)
     */
    private String status;

    /**
     * 错误信息
     */
    private String errorMsg;

    /**
     * 耗时(毫秒)
     */
    private Integer costTimeMs;

    /**
     * 操作时间
     */
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
}
