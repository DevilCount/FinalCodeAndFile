package com.sunyaxin.report.dto;

import lombok.Data;

import java.io.Serializable;
import java.util.List;
import java.util.Map;

/**
 * 报告统计DTO（用于仪表盘）
 */
@Data
public class ReportStatisticsDTO implements Serializable {
    private static final long serialVersionUID = 1L;

    /**
     * 今日报告总数
     */
    private Long todayReportCount;

    /**
     * 今日异常报告数
     */
    private Long todayAbnormalReportCount;

    /**
     * 待技术审核报告数
     */
    private Long pendingTechnicalReviewCount;

    /**
     * 待临床审核报告数
     */
    private Long pendingClinicalReviewCount;

    /**
     * 今日已发布报告数
     */
    private Long todayPublishedReportCount;

    /**
     * 报告状态分布
     */
    private Map<String, Long> statusDistribution;

    /**
     * 近7天报告趋势（日期->数量）
     */
    private Map<String, Long> weeklyTrend;

    /**
     * 审核效率统计（平均审核时间）
     */
    private Map<String, Double> reviewEfficiency;

    /**
     * 检验项目报告量排行
     */
    private List<Map<String, Object>> hotReportItems;

    /**
     * AI诊断使用率
     */
    private Double aiDiagnosisUsageRate;

    /**
     * 报告质量统计（异常率、驳回率等）
     */
    private Map<String, Double> qualityMetrics;
}
