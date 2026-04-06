package com.sunyaxin.report.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.sunyaxin.common.entity.Report;
import com.sunyaxin.common.result.Result;
import com.sunyaxin.report.dto.EnhancedReportDTO;
import com.sunyaxin.report.dto.ReportStatisticsDTO;
import com.sunyaxin.report.dto.ReviewDTO;
import com.sunyaxin.report.dto.TestResultItemDTO;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;

/**
 * 增强版报告服务接口
 * 支持双层审核流程、AI诊断集成、统计分析等
 */
public interface EnhancedReportService extends IService<Report> {

    // ==================== 核心业务流程 ====================

    /**
     * 创建检验报告（增强版，包含检验项目结构）
     */
    Result<Report> createEnhancedReport(Report report, List<TestResultItemDTO> testResults);

    /**
     * 录入检验结果（结构化数据）
     */
    Result<Report> inputStructuredResults(Long reportId, List<TestResultItemDTO> testResults,
                                          Long technicianId, String technicianName);

    /**
     * 调用AI辅助诊断
     */
    Result<String> invokeAiDiagnosis(Long reportId, List<TestResultItemDTO> testResults);

    /**
     * 提交技术审核
     */
    Result<Report> submitTechnicalReview(Long reportId, Long technicianId, String technicianName);

    /**
     * 进行技术审核
     */
    Result<Report> performTechnicalReview(Long reportId, ReviewDTO review);

    /**
     * 提交临床审核
     */
    Result<Report> submitClinicalReview(Long reportId, Long doctorId, String doctorName);

    /**
     * 进行临床审核
     */
    Result<Report> performClinicalReview(Long reportId, ReviewDTO review);

    /**
     * 发布报告
     */
    Result<Report> publishReport(Long reportId, Long publisherId, String publisherName);

    /**
     * 撤销报告
     */
    Result<Report> revokeReport(Long reportId, Long operatorId, String operatorName, String reason);

    /**
     * 归档报告
     */
    Result<Report> archiveReport(Long reportId, Long operatorId, String operatorName);

    // ==================== 查询统计功能 ====================

    /**
     * 获取增强版报告详情（包含双层审核信息）
     */
    Result<EnhancedReportDTO> getEnhancedReport(Long reportId);

    /**
     * 根据报告编号查询增强版报告
     */
    Result<EnhancedReportDTO> getEnhancedReportByNo(String reportNo);

    /**
     * 获取报告审核时间线
     */
    Result<List<com.sunyaxin.report.dto.ReviewTimelineDTO>> getReviewTimeline(Long reportId);

    /**
     * 获取报告统计信息（带缓存）
     */
    ReportStatisticsDTO getReportStatistics();

    /**
     * 清除报告统计缓存
     */
    void clearReportStatisticsCache();

    /**
     * 获取待技术审核报告列表
     */
    Result<List<EnhancedReportDTO>> getPendingTechnicalReviewReports();

    /**
     * 获取待临床审核报告列表
     */
    Result<List<EnhancedReportDTO>> getPendingClinicalReviewReports();

    /**
     * 获取异常报告列表
     */
    Result<List<EnhancedReportDTO>> getAbnormalReports(int limit);

    /**
     * 按状态统计报告数量
     */
    Map<String, Long> countReportsByStatus();

    /**
     * 按日期统计报告数量（最近N天）
     */
    Map<String, Long> countReportsByLastDays(int days);

    /**
     * 获取今日报告统计概览
     */
    Map<String, Object> getTodayReportStats();

    /**
     * 获取检验项目报告量排行
     */
    List<Map<String, Object>> getHotReportItems(int limit);

    /**
     * 获取审核效率统计
     */
    Map<String, Double> getReviewEfficiencyStats(LocalDate startDate, LocalDate endDate);

    // ==================== 批量操作 ====================

    /**
     * 批量提交技术审核
     */
    Result<String> batchSubmitTechnicalReview(List<Long> reportIds, Long technicianId, String technicianName);

    /**
     * 批量技术审核
     */
    Result<String> batchPerformTechnicalReview(List<Long> reportIds, ReviewDTO review);

    /**
     * 批量提交临床审核
     */
    Result<String> batchSubmitClinicalReview(List<Long> reportIds, Long doctorId, String doctorName);

    /**
     * 批量临床审核
     */
    Result<String> batchPerformClinicalReview(List<Long> reportIds, ReviewDTO review);

    /**
     * 批量发布报告
     */
    Result<String> batchPublishReports(List<Long> reportIds, Long publisherId, String publisherName);

    /**
     * 批量归档报告
     */
    Result<String> batchArchiveReports(List<Long> reportIds, Long operatorId, String operatorName);

    // ==================== 数据导入导出 ====================

    /**
     * 导出报告数据到Excel
     */
    byte[] exportReportsToExcel(String keyword, String status, String testItems,
                                 LocalDate startDate, LocalDate endDate);

    /**
     * 从Excel导入报告数据
     */
    Result<String> importReportsFromExcel(byte[] excelData, Long operatorId, String operatorName);

    /**
     * 导出报告审核流程到PDF
     */
    byte[] exportReportReviewProcessToPdf(Long reportId);
}
