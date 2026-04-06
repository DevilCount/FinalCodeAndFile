package com.sunyaxin.common.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.io.Serializable;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * 患者信息实体
 * 参考数据字典 LIS_LIST 简化版
 */
@Data
@TableName("lab_patient")
public class Patient implements Serializable {

    private static final long serialVersionUID = 1L;

    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 患者编号
     */
    private String patientNo;

    /**
     * 患者姓名
     */
    private String patientName;

    /**
     * 性别：1-男，2-女，3-未知
     */
    private String gender;

    /**
     * 性别描述
     */
    private String genderDesc;

    /**
     * 出生日期
     */
    private LocalDate birthday;

    /**
     * 年龄
     */
    private Integer age;

    /**
     * 年龄单位：岁、月、天
     */
    private String ageUnit;

    /**
     * 身份证号
     */
    private String idCard;

    /**
     * 联系电话
     */
    private String phone;

    /**
     * 联系地址
     */
    private String address;

    /**
     * 患者类型：OUTPATIENT-门诊，INPATIENT-住院，EMERGENCY-急诊
     */
    private String patientType;

    /**
     * 就诊卡号
     */
    private String cardNo;

    /**
     * 住院号
     */
    private String hospNo;

    /**
     * 病房
     */
    private String ward;

    /**
     * 床位
     */
    private String bedNo;

    /**
     * 科室
     */
    private String department;

    /**
     * 诊断
     */
    private String diagnosis;

    /**
     * 状态：0-禁用，1-启用
     */
    private Integer status;

    /**
     * 逻辑删除
     */
    @TableLogic
    private Integer deleted;

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
