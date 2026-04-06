package com.sunyaxin.report.dto;

import lombok.Data;

import java.io.Serializable;

/**
 * 检验结果项DTO（结构化数据）
 */
@Data
public class TestResultItemDTO implements Serializable {
    private static final long serialVersionUID = 1L;

    /**
     * 检验项目名称
     */
    private String itemName;

    /**
     * 检验项目编码
     */
    private String itemCode;

    /**
     * 检验结果值
     */
    private String resultValue;

    /**
     * 单位
     */
    private String unit;

    /**
     * 参考范围下限
     */
    private String referenceLow;

    /**
     * 参考范围上限
     */
    private String referenceHigh;

    /**
     * 参考范围描述
     */
    private String referenceDescription;

    /**
     * 是否异常：NORMAL-正常，LOW-偏低，HIGH-偏高，CRITICAL_LOW-危急值低，CRITICAL_HIGH-危急值高
     */
    private String abnormalFlag;

    /**
     * 异常描述
     */
    private String abnormalDescription;
}
