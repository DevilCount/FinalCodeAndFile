package com.sunyaxin.report.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 报告创建请求DTO
 */
@Data
public class ReportCreateDTO {

    /**
     * 标本ID
     */
    @NotNull(message = "标本ID不能为空")
    private Long sampleId;

    /**
     * 患者ID
     */
    @NotNull(message = "患者ID不能为空")
    private Long patientId;

    /**
     * 患者姓名
     */
    @NotBlank(message = "患者姓名不能为空")
    private String patientName;

    /**
     * 检验项目（多个项目用逗号分隔）
     */
    @NotBlank(message = "检验项目不能为空")
    private String testItems;

    /**
     * 检验结果（JSON格式存储）
     */
    private String testResults;

    /**
     * 检验医师ID
     */
    private Long technicianId;

    /**
     * 检验医师姓名
     */
    private String technicianName;

    /**
     * 检验时间
     */
    private LocalDateTime testTime;

    /**
     * 备注
     */
    private String remark;
}
