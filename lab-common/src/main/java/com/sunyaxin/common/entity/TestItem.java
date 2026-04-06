package com.sunyaxin.common.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.io.Serializable;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 检验项目实体
 * 参考数据字典 LIS_ITEM 简化版
 */
@Data
@TableName("lab_test_item")
public class TestItem implements Serializable {

    private static final long serialVersionUID = 1L;

    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 项目编码
     */
    private String itemCode;

    /**
     * 项目名称
     */
    private String itemName;

    /**
     * 项目简称
     */
    private String itemShortName;

    /**
     * 英文名称
     */
    private String englishName;

    /**
     * LOINC编码
     */
    private String loincCode;

    /**
     * 项目分类：血常规、尿常规、生化、免疫等
     */
    private String category;

    /**
     * 标本类型：BLOOD-血液，URINE-尿液，STOOL-粪便
     */
    private String sampleType;

    /**
     * 结果类型：NUMERIC-数值，TEXT-文本，FORMULA-公式
     */
    private String resultType;

    /**
     * 单位
     */
    private String unit;

    /**
     * 小数位数
     */
    private Integer decimalPlaces;

    /**
     * 价格
     */
    private BigDecimal price;

    /**
     * 默认值
     */
    private String defaultValue;

    /**
     * 打印顺序
     */
    private Integer printOrder;

    /**
     * 检验方法
     */
    private String testMethod;

    /**
     * 项目说明
     */
    private String itemDesc;

    /**
     * 临床意义
     */
    private String clinicalMeaning;

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
