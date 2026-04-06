package com.sunyaxin.report.controller;

import com.sunyaxin.common.entity.Report;
import com.sunyaxin.common.result.Result;
import com.sunyaxin.report.dto.ReportCreateDTO;
import com.sunyaxin.report.service.ReportService;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.BeanUtils;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 报告Controller
 * 
 * API端点参数校验说明：
 * - POST /create: @Valid ReportCreateDTO (sampleId, patientId, patientName, testItems 必填)
 */
@RestController
@RequestMapping("/report")
@RequiredArgsConstructor
@Validated
@Slf4j
public class ReportController {

    private final ReportService reportService;

    /**
     * 创建报告
     * 使用 ReportCreateDTO 进行参数校验
     * 
     * 参数校验:
     * - sampleId (@NotNull)
     * - patientId (@NotNull)
     * - patientName (@NotBlank)
     * - testItems (@NotBlank)
     */
    @PostMapping("/create")
    public Result<Report> createReport(@Valid @RequestBody ReportCreateDTO createDTO) {
        // 将DTO转换为实体
        Report report = new Report();
        BeanUtils.copyProperties(createDTO, report);
        return reportService.createReport(report);
    }

    /**
     * 根据ID获取报告
     * 路径参数校验: id (@Min(1))
     */
    @GetMapping("/{id}")
    public Result<Report> getReportById(
            @PathVariable(name = "id") @Min(value = 1, message = "报告ID必须大于0") Long id) {
        Report report = reportService.getById(id);
        return Result.success(report);
    }

    /**
     * 根据报告编号查询
     */
    @GetMapping("/no/{reportNo}")
    public Result<Report> getReportByNo(@PathVariable(name = "reportNo") String reportNo) {
        Report report = reportService.lambdaQuery().eq(Report::getReportNo, reportNo).one();
        return Result.success(report);
    }

    /**
     * 录入检验结果
     * 请求参数校验: results, technicianId, technicianName (必填)
     */
    @PostMapping("/{id}/input-results")
    public Result<Report> inputResults(
            @PathVariable(name = "id") @Min(value = 1, message = "报告ID必须大于0") Long id,
            @RequestParam(name = "results") @NotBlank(message = "检验结果不能为空") String results,
            @RequestParam(name = "technicianId") @Min(value = 1, message = "检验师ID无效") Long technicianId,
            @RequestParam(name = "technicianName") @NotBlank(message = "检验师姓名不能为空") String technicianName) {
        return reportService.inputResults(id, results, technicianId, technicianName);
    }

    /**
     * 审核报告
     * 请求参数校验: reviewerId, reviewerName, approved (必填), remark (可选)
     */
    @PostMapping("/{id}/review")
    public Result<Report> reviewReport(
            @PathVariable(name = "id") @Min(value = 1, message = "报告ID必须大于0") Long id,
            @RequestParam(name = "reviewerId") @Min(value = 1, message = "审核人ID无效") Long reviewerId,
            @RequestParam(name = "reviewerName") @NotBlank(message = "审核人姓名不能为空") String reviewerName,
            @RequestParam(name = "approved") boolean approved,
            @RequestParam(name = "remark", required = false) String remark) {
        return reportService.reviewReport(id, reviewerId, reviewerName, approved, remark);
    }

    /**
     * 发布报告
     */
    @PostMapping("/{id}/publish")
    public Result<Report> publishReport(
            @PathVariable(name = "id") @Min(value = 1, message = "报告ID必须大于0") Long id) {
        return reportService.publishReport(id);
    }

    /**
     * 根据患者ID查询报告
     */
    @GetMapping("/patient/{patientId}")
    public Result<List<Report>> getReportsByPatientId(
            @PathVariable(name = "patientId") @Min(value = 1, message = "患者ID必须大于0") Long patientId) {
        return reportService.getReportsByPatientId(patientId);
    }

    /**
     * 获取待审核报告列表
     */
    @GetMapping("/pending-list")
    public Result<List<Report>> getPendingReports() {
        return reportService.getPendingReports();
    }

    /**
     * 获取所有报告
     */
    @GetMapping("/list")
    public Result<List<Report>> listReports() {
        List<Report> list = reportService.list();
        return Result.success(list);
    }
}
