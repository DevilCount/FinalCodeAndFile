package com.sunyaxin.report.dto;

import lombok.Data;

import java.io.Serializable;
import java.time.LocalDateTime;

/**
 * 审核信息DTO
 */
@Data
public class ReviewDTO implements Serializable {
    private static final long serialVersionUID = 1L;

    /**
     * 审核类型：TECHNICAL-技术审核，CLINICAL-临床审核
     */
    private String reviewType;

    /**
     * 审核人ID
     */
    private Long reviewerId;

    /**
     * 审核人姓名
     */
    private String reviewerName;

    /**
     * 审核时间
     */
    private LocalDateTime reviewTime;

    /**
     * 审核结果：APPROVED-通过，REJECTED-驳回
     */
    private String result;

    /**
     * 审核意见
     */
    private String comment;

    /**
     * 审核备注
     */
    private String remark;

    /**
     * 是否需要重新检验
     */
    private Boolean needRetest;

    /**
     * 重新检验原因
     */
    private String retestReason;
}
