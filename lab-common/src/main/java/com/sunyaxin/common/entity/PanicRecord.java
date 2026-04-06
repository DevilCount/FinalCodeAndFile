package com.sunyaxin.common.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.io.Serializable;
import java.time.LocalDateTime;

/**
 * 危急值记录实体
 * 参考数据字典 Lab_PanicRepTrace 简化版
 */
@Data
@TableName("lab_panic_record")
public class PanicRecord implements Serializable {

    private static final long serialVersionUID = 1L;

    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 报告ID
     */
    private Long reportId;

    /**
     * 标本ID
     */
    private Long sampleId;

    /**
     * 标本编号
     */
    private String sampleNo;

    /**
     * 患者ID
     */
    private Long patientId;

    /**
     * 患者姓名
     */
    private String patientName;

    /**
     * 项目编码
     */
    private String itemCode;

    /**
     * 项目名称
     */
    private String itemName;

    /**
     * 结果值
     */
    private String resultValue;

    /**
     * 参考范围
     */
    private String referenceRange;

    /**
     * 危急值
     */
    private String panicValue;

    /**
     * 状态：PENDING-待处理，NOTIFIED-已通知，CONFIRMED-已确认，HANDLED-已处理
     */
    private String status;

    /**
     * 通知时间
     */
    private LocalDateTime notifyTime;

    /**
     * 通知方式：PHONE-电话，SMS-短信，SYSTEM-系统
     */
    private String notifyMethod;

    /**
     * 通知人
     */
    private String notifyPerson;

    /**
     * 接收人
     */
    private String receivePerson;

    /**
     * 接收时间
     */
    private LocalDateTime receiveTime;

    /**
     * 确认时间
     */
    private LocalDateTime confirmTime;

    /**
     * 处理时间
     */
    private LocalDateTime handleTime;

    /**
     * 处理结果
     */
    private String handleResult;

    /**
     * 处理备注
     */
    private String handleRemark;

    /**
     * 创建时间
     */
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;

    /**
     * 更新时间
     */
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updateTime;
}
