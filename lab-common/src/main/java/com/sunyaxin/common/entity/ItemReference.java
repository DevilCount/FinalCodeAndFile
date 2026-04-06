package com.sunyaxin.common.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.io.Serializable;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 参考值配置实体
 * 参考数据字典 LIS_ITEMREFERANCE 简化版
 */
@Data
@TableName("lab_item_reference")
public class ItemReference implements Serializable {

    private static final long serialVersionUID = 1L;

    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 检验项目ID
     */
    private Long itemId;

    /**
     * 项目编码
     */
    private String itemCode;

    /**
     * 参考值类型：NORMAL-正常，PANIC-危急值，FORMULA-计算公式
     */
    private String referenceType;

    /**
     * 性别：M-男，F-女，A-全部
     */
    private String gender;

    /**
     * 年龄最小值
     */
    private Integer ageMin;

    /**
     * 年龄最大值
     */
    private Integer ageMax;

    /**
     * 年龄单位：岁、月、天
     */
    private String ageUnit;

    /**
     * 下限
     */
    private BigDecimal lowLimit;

    /**
     * 上限
     */
    private BigDecimal highLimit;

    /**
     * 警告下限
     */
    private BigDecimal lowWarn;

    /**
     * 警告上限
     */
    private BigDecimal highWarn;

    /**
     * 危机下限
     */
    private BigDecimal lowPanic;

    /**
     * 危机上限
     */
    private BigDecimal highPanic;

    /**
     * 参考值文本描述
     */
    private String referenceText;

    /**
     * 标本类型
     */
    private String sampleType;

    /**
     * 状态：0-停用，1-启用
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
