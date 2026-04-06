package com.sunyaxin.common.entity;

import com.baomidou.mybatisplus.annotation.*;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.io.Serializable;
import java.time.LocalDateTime;

/**
 * 标本实体
 */
@Data
@TableName("lab_sample")
public class Sample implements Serializable {

    private static final long serialVersionUID = 1L;

    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 标本编号（唯一）- 由系统自动生成
     */
    private String sampleNo;

    /**
     * 患者ID
     */
    private Long patientId;

    /**
     * 患者姓名
     */
    @NotBlank(message = "患者姓名不能为空")
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
     * 申请医生ID
     */
    private Long doctorId;

    /**
     * 申请医生姓名
     */
    private String doctorName;

    /**
     * 检验项目
     */
    @NotBlank(message = "检验项目不能为空")
    private String testItems;

    /**
     * 标本类型：BLOOD-血液，URINE-尿液，STOOL-粪便等
     */
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
     * 接收时间
     */
    private LocalDateTime receiveTime;

    /**
     * 检验医师ID
     */
    private Long technicianId;

    /**
     * 检验医师姓名
     */
    private String technicianName;

    /**
     * 状态：COLLECTED-已采集，IN_TRANSIT-运输中，RECEIVED-已接收，TESTING-检验中，COMPLETED-已完成，ARCHIVED-已归档，ABNORMAL-异常
     */
    private String status;

    /**
     * 备注
     */
    private String remark;

    /**
     * 创建时间
     */
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;

    /**
     * 更新时间
     */
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updateTime;
}
