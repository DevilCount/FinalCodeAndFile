package com.sunyaxin.common.entity;

import com.baomidou.mybatisplus.annotation.*;

import java.io.Serializable;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 检验项目实体
 * 参考数据字典 LIS_ITEM 简化版
 */
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

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getItemCode() {
        return itemCode;
    }

    public void setItemCode(String itemCode) {
        this.itemCode = itemCode;
    }

    public String getItemName() {
        return itemName;
    }

    public void setItemName(String itemName) {
        this.itemName = itemName;
    }

    public String getItemShortName() {
        return itemShortName;
    }

    public void setItemShortName(String itemShortName) {
        this.itemShortName = itemShortName;
    }

    public String getEnglishName() {
        return englishName;
    }

    public void setEnglishName(String englishName) {
        this.englishName = englishName;
    }

    public String getLoincCode() {
        return loincCode;
    }

    public void setLoincCode(String loincCode) {
        this.loincCode = loincCode;
    }

    public String getCategory() {
        return category;
    }

    public void setCategory(String category) {
        this.category = category;
    }

    public String getSampleType() {
        return sampleType;
    }

    public void setSampleType(String sampleType) {
        this.sampleType = sampleType;
    }

    public String getResultType() {
        return resultType;
    }

    public void setResultType(String resultType) {
        this.resultType = resultType;
    }

    public String getUnit() {
        return unit;
    }

    public void setUnit(String unit) {
        this.unit = unit;
    }

    public Integer getDecimalPlaces() {
        return decimalPlaces;
    }

    public void setDecimalPlaces(Integer decimalPlaces) {
        this.decimalPlaces = decimalPlaces;
    }

    public BigDecimal getPrice() {
        return price;
    }

    public void setPrice(BigDecimal price) {
        this.price = price;
    }

    public String getDefaultValue() {
        return defaultValue;
    }

    public void setDefaultValue(String defaultValue) {
        this.defaultValue = defaultValue;
    }

    public Integer getPrintOrder() {
        return printOrder;
    }

    public void setPrintOrder(Integer printOrder) {
        this.printOrder = printOrder;
    }

    public String getTestMethod() {
        return testMethod;
    }

    public void setTestMethod(String testMethod) {
        this.testMethod = testMethod;
    }

    public String getItemDesc() {
        return itemDesc;
    }

    public void setItemDesc(String itemDesc) {
        this.itemDesc = itemDesc;
    }

    public String getClinicalMeaning() {
        return clinicalMeaning;
    }

    public void setClinicalMeaning(String clinicalMeaning) {
        this.clinicalMeaning = clinicalMeaning;
    }

    public Integer getStatus() {
        return status;
    }

    public void setStatus(Integer status) {
        this.status = status;
    }

    public Integer getDeleted() {
        return deleted;
    }

    public void setDeleted(Integer deleted) {
        this.deleted = deleted;
    }

    public LocalDateTime getCreateTime() {
        return createTime;
    }

    public void setCreateTime(LocalDateTime createTime) {
        this.createTime = createTime;
    }

    public LocalDateTime getUpdateTime() {
        return updateTime;
    }

    public void setUpdateTime(LocalDateTime updateTime) {
        this.updateTime = updateTime;
    }
}
