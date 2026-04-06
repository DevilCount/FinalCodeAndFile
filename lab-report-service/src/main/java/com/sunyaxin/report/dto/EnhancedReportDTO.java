package com.sunyaxin.report.dto;

import lombok.Data;

import java.io.Serializable;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

/**
 * 报告双层审核流程DTO
 */
@Data
public class EnhancedReportDTO implements Serializable {
    private static final long serialVersionUID = 1L;

    /**
     * 报告ID
     */
    private Long id;

    /**
     * 报告编号
     */
    private String reportNo;

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
     * 检验结果（结构化数据）
     */
    private List<TestResultItemDTO> testResults;

    /**
     * AI辅助诊断结果
     */
    private AiDiagnosisDTO aiDiagnosis;

    /**
     * 检验医师信息
     */
    private TechnicianDTO technician;

    /**
     * 技术审核信息
     */
    private ReviewDTO technicalReview;

    /**
     * 临床审核信息
     */
    private ReviewDTO clinicalReview;

    /**
     * 当前状态
     */
    private String status;

    /**
     * 状态描述
     */
    private String statusDescription;

    /**
     * 检验时间
     */
    private LocalDateTime testTime;

    /**
     * 审核状态时间线
     */
    private List<ReviewTimelineDTO> reviewTimeline;

    /**
     * 是否可以发布
     */
    private Boolean canPublish;

    /**
     * 是否可以撤销
     */
    private Boolean canRevoke;

    /**
     * 是否可以重新审核
     */
    private Boolean canReReview;

    /**
     * 备注信息
     */
    private String remark;
}
