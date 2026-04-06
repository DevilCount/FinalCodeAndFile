package com.sunyaxin.sample.dto;

import lombok.Data;

import java.io.Serializable;
import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * 标本状态统计DTO
 * 用于仪表盘展示
 */
@Data
public class SampleStatusStatsDTO implements Serializable {
    private static final long serialVersionUID = 1L;

    /**
     * 状态编码
     */
    private String status;

    /**
     * 状态名称
     */
    private String statusName;

    /**
     * 数量
     */
    private Long count;

    /**
     * 占比（百分比）
     */
    private Double percentage;

    /**
     * 较昨日变化
     */
    private Long changeFromYesterday;
}
