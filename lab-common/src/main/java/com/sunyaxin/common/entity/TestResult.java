package com.sunyaxin.common.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.io.Serializable;
import java.time.LocalDateTime;

/**
 * 检验结果明细实体
 * 参考数据字典 LIS_RESULT 简化版
 */
@Data
@TableName("lab_test_result")
public class TestResult implements Serializable {

    private static final long serialVersionUID = 1L;

    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 报告ID
     */
    private Long reportId;

    /**
     * 标本ID
     */
    private Long sampleId;

    /**
     * 标本编号
     */
    private String sampleNo;

    /**
     * 患者ID
     */
    private Long patientId;

    /**
     * 检验项目ID
     */
    private Long itemId;

    /**
     * 项目编码
     */
    private String itemCode;

    /**
     * 项目名称
     */
    private String itemName;

    /**
     * 结果值
     */
    private String resultValue;

    /**
     * 结果描述
     */
    private String resultText;

    /**
     * 单位
     */
    private String unit;

    /**
     * 参考范围
     */
    private String referenceRange;

    /**
     * 提示信息
     */
    private String hintInfo;

    /**
     * 高低标志：H-偏高，L-偏低，HH-严重偏高，LL-严重偏低，P-阳性
     */
    private String highLowFlag;

    /**
     * 是否异常：0-正常，1-异常
     */
    private Integer isAbnormal;

    /**
     * 是否危急值
     */
    private Integer isPanic;

    /**
     * 结果来源：MANUAL-人工，DEVICE-设备
     */
    private String resultSource;

    /**
     * 检验时间
     */
    private LocalDateTime resultTime;

    /**
     * 检验人ID
     */
    private Long technicianId;

    /**
     * 检验人姓名
     */
    private String technicianName;

    /**
     * 逻辑删除
     */
    @TableLogic
    private Integer isDeleted;

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
