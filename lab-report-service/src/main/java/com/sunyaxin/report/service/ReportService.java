package com.sunyaxin.report.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.sunyaxin.common.entity.Report;
import com.sunyaxin.common.result.Result;

import java.util.List;

/**
 * 报告Service接口
 */
public interface ReportService extends IService<Report> {

    /**
     * 创建报告
     */
    Result<Report> createReport(Report report);

    /**
     * 录入检验结果
     */
    Result<Report> inputResults(Long reportId, String results, Long technicianId, String technicianName);

    /**
     * 审核报告
     */
    Result<Report> reviewReport(Long reportId, Long reviewerId, String reviewerName, boolean approved, String remark);

    /**
     * 发布报告
     */
    Result<Report> publishReport(Long reportId);

    /**
     * 根据患者ID查询报告
     */
    Result<List<Report>> getReportsByPatientId(Long patientId);

    /**
     * 获取待审核报告列表
     */
    Result<List<Report>> getPendingReports();
}
