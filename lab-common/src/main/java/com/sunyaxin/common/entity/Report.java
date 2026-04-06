package com.sunyaxin.common.entity;

import com.baomidou.mybatisplus.annotation.*;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.io.Serializable;
import java.time.LocalDateTime;

/**
 * 检验报告实体
 */
@Data
@TableName("lab_report")
public class Report implements Serializable {

    private static final long serialVersionUID = 1L;

    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 报告编号 - 由系统自动生成
     */
    private String reportNo;

    /**
     * 标本ID
     */
    @NotNull(message = "标本ID不能为空")
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
     * 患者姓名
     */
    @NotBlank(message = "患者姓名不能为空")
    private String patientName;

    /**
     * 检验项目
     */
    @NotBlank(message = "检验项目不能为空")
    private String testItems;

    /**
     * 检验结果（JSON格式存储）
     */
    private String testResults;

    /**
     * AI辅助诊断结果
     */
    private String aiDiagnosis;

    /**
     * AI诊断置信度（0-100）
     */
    private Integer aiConfidence;

    /**
     * AI模型版本
     */
    private String aiModelVersion;

    /**
     * AI诊断时间
     */
    private LocalDateTime aiDiagnosisTime;

    /**
     * 检验医师ID
     */
    private Long technicianId;

    /**
     * 检验医师姓名
     */
    private String technicianName;

    /**
     * 审核医师ID（兼容旧版，现为技术审核人）
     */
    private Long reviewerId;

    /**
     * 审核医师姓名（兼容旧版，现为技术审核人）
     */
    private String reviewerName;

    /**
     * 技术审核人ID
     */
    private Long technicalReviewerId;

    /**
     * 技术审核人姓名
     */
    private String technicalReviewerName;

    /**
     * 技术审核时间
     */
    private LocalDateTime technicalReviewTime;

    /**
     * 技术审核结果：APPROVED-通过，REJECTED-驳回
     */
    private String technicalReviewResult;

    /**
     * 技术审核意见
     */
    private String technicalReviewComment;

    /**
     * 临床审核人ID
     */
    private Long clinicalReviewerId;

    /**
     * 临床审核人姓名
     */
    private String clinicalReviewerName;

    /**
     * 临床审核时间
     */
    private LocalDateTime clinicalReviewTime;

    /**
     * 临床审核结果：APPROVED-通过，REJECTED-驳回
     */
    private String clinicalReviewResult;

    /**
     * 临床审核意见
     */
    private String clinicalReviewComment;

    /**
     * 状态：PENDING-待审核，REVIEWING-审核中，APPROVED-已通过，REJECTED-已驳回，PUBLISHED-已发布
     */
    private String status;

    /**
     * 检验时间
     */
    private LocalDateTime testTime;

    /**
     * 审核时间
     */
    private LocalDateTime reviewTime;

    /**
     * 备注
     */
    private String remark;

    /**
     * 异常指标数量
     */
    private Integer abnormalIndicatorCount;

    /**
     * 危急值数量
     */
    private Integer criticalIndicatorCount;

    /**
     * 撤销人ID
     */
    private Long revokedBy;

    /**
     * 撤销人姓名
     */
    private String revokedByName;

    /**
     * 撤销时间
     */
    private LocalDateTime revokedTime;

    /**
     * 撤销原因
     */
    private String revokedReason;

    /**
     * 归档人ID
     */
    private Long archivedBy;

    /**
     * 归档人姓名
     */
    private String archivedByName;

    /**
     * 归档时间
     */
    private LocalDateTime archivedTime;

    /**
     * 打印次数
     */
    private Integer printCount;

    /**
     * 首次打印时间
     */
    private LocalDateTime printTime;

    /**
     * 发布时间
     */
    private LocalDateTime publishedTime;

    /**
     * 发布人ID
     */
    private Long publishedBy;

    /**
     * 发布人姓名
     */
    private String publishedByName;

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
