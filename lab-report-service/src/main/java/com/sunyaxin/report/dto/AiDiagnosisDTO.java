package com.sunyaxin.report.dto;

import lombok.Data;

import java.io.Serializable;
import java.util.List;

/**
 * AI辅助诊断DTO
 */
@Data
public class AiDiagnosisDTO implements Serializable {
    private static final long serialVersionUID = 1L;

    /**
     * AI诊断结果
     */
    private String diagnosis;

    /**
     * 诊断置信度（0-100）
     */
    private Integer confidence;

    /**
     * 异常指标列表
     */
    private List<AbnormalIndicatorDTO> abnormalIndicators;

    /**
     * 诊断建议
     */
    private List<String> suggestions;

    /**
     * 需要关注的指标
     */
    private List<String> attentionItems;

    /**
     * AI模型版本
     */
    private String modelVersion;

    /**
     * 诊断时间
     */
    private String diagnosisTime;

    /**
     * 备注
     */
    private String remark;
}
