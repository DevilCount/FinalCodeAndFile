package com.sunyaxin.report.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.sunyaxin.common.constant.OperationTypeConstant;
import com.sunyaxin.common.constant.ReportStatusConstant;
import com.sunyaxin.common.entity.OperationLog;
import com.sunyaxin.common.entity.Report;
import com.sunyaxin.common.result.Result;
import com.sunyaxin.common.service.OperationLogService;
import com.sunyaxin.common.utils.CodeGenerator;
import com.sunyaxin.report.feign.AiServiceClient;
import com.sunyaxin.report.mapper.ReportMapper;
import com.sunyaxin.report.service.ReportService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.CacheConfig;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 报告Service实现类
 */
@Slf4j
@Service
@RequiredArgsConstructor
@CacheConfig(cacheNames = "report")
public class ReportServiceImpl extends ServiceImpl<ReportMapper, Report> implements ReportService {

    private final AiServiceClient aiServiceClient;
    private final OperationLogService operationLogService;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public Result<Report> createReport(Report report) {
        try {
            // ========== 参数校验 ==========
            if (report.getPatientName() == null || report.getPatientName().trim().isEmpty()) {
                return Result.badRequest("患者姓名不能为空");
            }
            if (report.getTestItems() == null || report.getTestItems().trim().isEmpty()) {
                return Result.badRequest("检验项目不能为空");
            }

            // 如果没有传patientId，使用sampleId作为patientId（兼容前端不传patientId的情况）
            if (report.getPatientId() == null && report.getSampleId() != null) {
                log.info("==> patientId为空，使用sampleId: {} 作为patientId", report.getSampleId());
                report.setPatientId(report.getSampleId());
            }

            // 生成报告编号
            report.setReportNo(CodeGenerator.generateReportNo());
            report.setStatus(ReportStatusConstant.PENDING);
            report.setTestTime(LocalDateTime.now());

            // 保存前日志
            log.info("==> 保存报告信息, 报告编号: {}, 患者ID: {}, 标本ID: {}",
                    report.getReportNo(), report.getPatientId(), report.getSampleId());

            this.save(report);

            // 验证保存结果
            if (report.getId() == null) {
                log.error("报告保存后ID为空");
                throw new RuntimeException("报告保存失败：未获取到报告ID");
            }

            log.info("==> 报告保存成功, ID: {}, 编号: {}", report.getId(), report.getReportNo());

            // 记录操作日志
            operationLogService.recordOperation(
                    OperationTypeConstant.MODULE_REPORT,
                    OperationTypeConstant.REPORT_CREATE,
                    "创建检验报告: " + report.getReportNo(),
                    "Report",
                    report.getId(),
                    report.getReportNo(),
                    report.getTechnicianId(),
                    report.getTechnicianName(),
                    "患者: " + report.getPatientName()
            );

            log.info("==> 创建报告成功: {} | 患者: {}", report.getReportNo(), report.getPatientName());
            return Result.success("创建成功", report);
            
        } catch (Exception e) {
            log.error("创建报告异常: {}", e.getMessage(), e);
            // 返回错误信息而非抛出异常，避免500错误
            return Result.error("创建报告失败: " + e.getMessage());
        }
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public Result<Report> inputResults(Long reportId, String results, Long technicianId, String technicianName) {
        Report report = this.getById(reportId);
        if (report == null) {
            return Result.error("报告不存在");
        }

        report.setTestResults(results);
        report.setTechnicianId(technicianId);
        report.setTechnicianName(technicianName);
        report.setStatus(ReportStatusConstant.REVIEWING);

        // 调用AI辅助诊断
        String aiDiagnosis = null;
        try {
            Map<String, Object> testData = new HashMap<>();
            testData.put("testItems", report.getTestItems());
            testData.put("testResults", results);
            testData.put("patientId", report.getPatientId());
            Result<String> aiResult = aiServiceClient.diagnose(testData);
            if (aiResult != null && aiResult.getCode() == 200) {
                aiDiagnosis = aiResult.getData();
                report.setAiDiagnosis(aiDiagnosis);
            }
        } catch (Exception e) {
            log.warn("==> AI诊断调用失败: {}", e.getMessage());
            aiDiagnosis = "AI诊断暂时不可用";
            report.setAiDiagnosis(aiDiagnosis);
        }

        this.updateById(report);

        // 记录操作日志
        String operationDesc = "录入检验结果 [" + report.getReportNo() + "]";
        if (aiDiagnosis != null) {
            operationDesc += " - AI诊断: " + aiDiagnosis;
        }

        operationLogService.recordOperation(
                OperationTypeConstant.MODULE_REPORT,
                aiDiagnosis != null ? OperationTypeConstant.REPORT_AI_DIAGNOSE : OperationTypeConstant.REPORT_INPUT,
                operationDesc,
                "Report",
                reportId,
                report.getReportNo(),
                technicianId,
                technicianName,
                "检验项目: " + report.getTestItems()
        );

        log.info("==> 录入检验结果成功: {} | AI诊断: {}", report.getReportNo(), aiDiagnosis != null ? "已生成" : "不可用");
        return Result.success("结果录入成功", report);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public Result<Report> reviewReport(Long reportId, Long reviewerId, String reviewerName, boolean approved, String remark) {
        Report report = this.getById(reportId);
        if (report == null) {
            return Result.error("报告不存在");
        }

        report.setReviewerId(reviewerId);
        report.setReviewerName(reviewerName);
        report.setReviewTime(LocalDateTime.now());
        report.setRemark(remark);

        String operationType;
        if (approved) {
            report.setStatus(ReportStatusConstant.APPROVED);
            operationType = OperationTypeConstant.REPORT_REVIEW;
        } else {
            report.setStatus(ReportStatusConstant.REJECTED);
            operationType = OperationTypeConstant.REPORT_REJECT;
        }

        this.updateById(report);

        // 记录操作日志
        String operationDesc = (approved ? "审核通过" : "审核驳回") + " [" + report.getReportNo() + "]";
        if (remark != null && !remark.isEmpty()) {
            operationDesc += " - 备注: " + remark;
        }

        operationLogService.recordOperation(
                OperationTypeConstant.MODULE_REPORT,
                operationType,
                operationDesc,
                "Report",
                reportId,
                report.getReportNo(),
                reviewerId,
                reviewerName,
                approved ? "审核通过" : "驳回原因: " + remark
        );

        log.info("==> 报告审核: {} | {} | 审核人: {}", report.getReportNo(), 
                approved ? "通过" : "驳回", reviewerName);
        return Result.success("审核完成", report);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public Result<Report> publishReport(Long reportId) {
        Report report = this.getById(reportId);
        if (report == null) {
            return Result.error("报告不存在");
        }
        if (!ReportStatusConstant.APPROVED.equals(report.getStatus())) {
            return Result.error("报告未通过审核，无法发布");
        }

        report.setStatus(ReportStatusConstant.PUBLISHED);
        report.setPublishedTime(LocalDateTime.now());
        this.updateById(report);

        // 记录操作日志
        operationLogService.recordOperation(
                OperationTypeConstant.MODULE_REPORT,
                OperationTypeConstant.REPORT_PUBLISH,
                "发布检验报告: " + report.getReportNo(),
                "Report",
                reportId,
                report.getReportNo(),
                report.getPublishedBy(),
                report.getPublishedByName(),
                "患者: " + report.getPatientName()
        );

        log.info("==> 发布报告成功: {}", report.getReportNo());
        return Result.success("发布成功", report);
    }

    @Override
    public Result<List<Report>> getReportsByPatientId(Long patientId) {
        List<Report> list = baseMapper.selectByPatientId(patientId);
        return Result.success(list);
    }

    @Override
    public Result<List<Report>> getPendingReports() {
        List<Report> list = baseMapper.selectByStatus(ReportStatusConstant.REVIEWING);
        return Result.success(list);
    }
}
