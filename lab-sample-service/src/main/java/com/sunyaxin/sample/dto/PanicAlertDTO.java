package com.sunyaxin.sample.dto;

import lombok.Data;

import java.io.Serializable;
import java.time.LocalDateTime;

/**
 * 危急值提醒DTO
 */
@Data
public class PanicAlertDTO implements Serializable {
    private static final long serialVersionUID = 1L;

    /**
     * 提醒ID
     */
    private Long id;

    /**
     * 报告ID
     */
    private Long reportId;

    /**
     * 报告编号
     */
    private String reportNo;

    /**
     * 患者姓名
     */
    private String patientName;

    /**
     * 异常项目
     */
    private String panicItem;

    /**
     * 异常值
     */
    private String panicValue;

    /**
     * 危急程度：CRITICAL-危急，WARNING-警告
     */
    private String level;

    /**
     * 通知时间
     */
    private LocalDateTime notifyTime;

    /**
     * 是否已确认
     */
    private Boolean confirmed;

    /**
     * 确认人
     */
    private String confirmedBy;

    /**
     * 确认时间
     */
    private LocalDateTime confirmedTime;
}
