package com.sunyaxin.sample.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 标本创建请求DTO
 */
@Data
public class SampleCreateDTO {

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
     * 患者性别：MALE-男，FEMALE-女，OTHER-其他
     */
    @Pattern(regexp = "^(MALE|FEMALE|OTHER|)$", message = "性别值无效，应为MALE/FEMALE/OTHER")
    private String patientGender;

    /**
     * 患者年龄
     */
    private Integer patientAge;

    /**
     * 申请医生ID
     */
    private Long doctorId;

    /**
     * 申请医生姓名
     */
    private String doctorName;

    /**
     * 检验项目（多个项目用逗号分隔）
     */
    @NotBlank(message = "检验项目不能为空")
    private String testItems;

    /**
     * 标本类型：BLOOD-血液，URINE-尿液，STOOL-粪便等
     */
    @NotBlank(message = "标本类型不能为空")
    private String sampleType;

    /**
     * 采集时间
     */
    private LocalDateTime collectTime;

    /**
     * 采集位置
     */
    private String collectLocation;

    /**
     * 备注
     */
    private String remark;
}
