package com.sunyaxin.common.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.io.Serializable;
import java.time.LocalDateTime;

/**
 * 标本追踪记录实体
 */
@Data
@TableName("lab_sample_trace")
public class SampleTrace implements Serializable {

    private static final long serialVersionUID = 1L;

    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 标本ID
     */
    private Long sampleId;

    /**
     * 标本编号
     */
    private String sampleNo;

    /**
     * 操作类型：COLLECT-采集，TRANSPORT-运输，RECEIVE-接收，TEST-检验，COMPLETE-完成，ARCHIVE-归档
     */
    private String operationType;

    /**
     * 操作描述
     */
    private String operationDesc;

    /**
     * 操作人ID
     */
    private Long operatorId;

    /**
     * 操作人姓名
     */
    private String operatorName;

    /**
     * 操作位置
     */
    private String location;

    /**
     * 创建时间
     */
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
}
