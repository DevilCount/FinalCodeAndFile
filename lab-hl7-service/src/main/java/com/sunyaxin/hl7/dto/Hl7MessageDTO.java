package com.sunyaxin.hl7.dto;

import lombok.Data;

/**
 * HL7消息DTO
 */
@Data
public class Hl7MessageDTO {

    /**
     * 消息类型：ADT^A01-患者入院，ORM^O01-检验申请，ORU^R01-检验结果
     */
    private String messageType;

    /**
     * 患者ID
     */
    private String patientId;

    /**
     * 患者姓名
     */
    private String patientName;

    /**
     * 患者性别
     */
    private String patientGender;

    /**
     * 患者出生日期
     */
    private String patientBirthDate;

    /**
     * 申请单号
     */
    private String orderNo;

    /**
     * 申请医生
     */
    private String orderingProvider;

    /**
     * 检验项目
     */
    private String testItems;

    /**
     * 检验结果（JSON格式）
     */
    private String testResults;

    /**
     * 原始HL7消息
     */
    private String rawMessage;
}
