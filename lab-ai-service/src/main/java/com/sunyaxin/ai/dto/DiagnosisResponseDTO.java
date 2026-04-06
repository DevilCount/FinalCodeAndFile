package com.sunyaxin.ai.dto;

import lombok.Data;

/**
 * AI诊断响应DTO
 */
@Data
public class DiagnosisResponseDTO {

    /**
     * 诊断建议
     */
    private String diagnosis;

    /**
     * 异常指标提示
     */
    private String abnormalIndicators;

    /**
     * 参考范围说明
     */
    private String referenceNotes;

    /**
     * 建议进一步检查项目
     */
    private String recommendedTests;

    /**
     * 置信度（0-1）
     */
    private Double confidence;

    /**
     * 免责声明
     */
    private String disclaimer = "本诊断建议仅供参考，不作为最终诊断依据，具体诊断请咨询专业医师。";
}
