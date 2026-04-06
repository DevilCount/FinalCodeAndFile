package com.sunyaxin.ai.dto;

import lombok.Data;

import java.util.Map;

/**
 * AI诊断请求DTO
 */
@Data
public class DiagnosisRequestDTO {

    /**
     * 患者ID
     */
    private Long patientId;

    /**
     * 患者姓名
     */
    private String patientName;

    /**
     * 患者性别
     */
    private String patientGender;

    /**
     * 患者年龄
     */
    private Integer patientAge;

    /**
     * 检验项目类型：BLOOD_ROUTINE-血常规，URINE_ROUTINE-尿常规
     */
    private String testType;

    /**
     * 检验项目
     */
    private String testItems;

    /**
     * 检验结果（键值对形式）
     */
    private Map<String, Object> testResults;
}
