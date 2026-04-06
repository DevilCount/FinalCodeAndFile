package com.sunyaxin.common.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.io.Serializable;
import java.time.LocalDateTime;

/**
 * 设备实体
 */
@Data
@TableName("lab_device")
public class Device implements Serializable {

    private static final long serialVersionUID = 1L;

    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 设备编号
     */
    private String deviceNo;

    /**
     * 设备名称
     */
    private String deviceName;

    /**
     * 设备型号
     */
    private String deviceModel;

    /**
     * 生产厂家
     */
    private String manufacturer;

    /**
     * 设备类型：ANALYZER-分析仪，MICROSCOPE-显微镜，CENTRIFUGE-离心机等
     */
    private String deviceType;

    /**
     * 所在位置
     */
    private String location;

    /**
     * 状态：IDLE-空闲，RUNNING-运行中，MAINTENANCE-维护中，FAULT-故障
     */
    private String status;

    /**
     * 购买日期
     */
    private LocalDateTime purchaseDate;

    /**
     * 维护日期
     */
    private LocalDateTime lastMaintenanceDate;

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
