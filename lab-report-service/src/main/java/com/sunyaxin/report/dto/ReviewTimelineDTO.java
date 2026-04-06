package com.sunyaxin.report.dto;

import lombok.Data;

import java.io.Serializable;
import java.time.LocalDateTime;

/**
 * 审核时间线DTO
 */
@Data
public class ReviewTimelineDTO implements Serializable {
    private static final long serialVersionUID = 1L;

    /**
     * 时间点
     */
    private LocalDateTime time;

    /**
     * 事件类型：CREATE-创建报告，INPUT_RESULTS-录入结果，TECHNICAL_REVIEW-技术审核，CLINICAL_REVIEW-临床审核，PUBLISH-发布，ARCHIVE-归档
     */
    private String eventType;

    /**
     * 事件描述
     */
    private String description;

    /**
     * 操作人姓名
     */
    private String operatorName;

    /**
     * 操作详情
     */
    private String details;

    /**
     * 状态变更
     */
    private String statusChange;
}
