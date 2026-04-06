package com.sunyaxin.sample.dto;

import lombok.Data;

import java.io.Serializable;
import java.time.LocalDateTime;

/**
 * 待办事项DTO
 */
@Data
public class TodoItemDTO implements Serializable {
    private static final long serialVersionUID = 1L;

    /**
     * 待办ID
     */
    private Long id;

    /**
     * 待办类型：SAMPLE_RECEIVE-标本接收，REPORT_REVIEW-报告审核，DEVICE_MAINTENANCE-设备维护
     */
    private String type;

    /**
     * 待办标题
     */
    private String title;

    /**
     * 待办描述
     */
    private String description;

    /**
     * 关联数据ID（标本ID、报告ID等）
     */
    private Long relatedId;

    /**
     * 关联数据编号（标本号、报告号等）
     */
    private String relatedNo;

    /**
     * 优先级：HIGH-高，MEDIUM-中，LOW-低
     */
    private String priority;

    /**
     * 截止时间
     */
    private LocalDateTime deadline;

    /**
     * 创建时间
     */
    private LocalDateTime createTime;

    /**
     * 状态：PENDING-待处理，PROCESSING-处理中，COMPLETED-已完成
     */
    private String status;

    // ========== 标本相关扩展字段 ==========
    /**
     * 标本ID
     */
    private Long sampleId;

    /**
     * 标本编号
     */
    private String sampleNo;

    /**
     * 患者姓名
     */
    private String patientName;

    /**
     * 检验项目
     */
    private String testItems;

    /**
     * 采集时间
     */
    private LocalDateTime collectTime;

    /**
     * 操作建议
     */
    private String actionSuggestion;
}
