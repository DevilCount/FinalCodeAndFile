package com.sunyaxin.report.dto;

import lombok.Data;

import java.io.Serializable;

/**
 * 异常指标DTO
 */
@Data
public class AbnormalIndicatorDTO implements Serializable {
    private static final long serialVersionUID = 1L;

    /**
     * 指标名称
     */
    private String indicatorName;

    /**
     * 当前值
     */
    private String currentValue;

    /**
     * 参考范围
     */
    private String referenceRange;

    /**
     * 异常程度：MILD-轻度，MODERATE-中度，SEVERE-重度，CRITICAL-危急
     */
    private String severity;

    /**
     * 临床意义
     */
    private String clinicalSignificance;
}
