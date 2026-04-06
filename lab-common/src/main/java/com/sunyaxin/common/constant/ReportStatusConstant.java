package com.sunyaxin.common.constant;

import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * 报告状态常量（增强版）
 * 支持双层审核流程：技术审核 → 临床审核 → 发布
 */
public class ReportStatusConstant {

    // ==================== 基础状态 ====================

    /**
     * 待检验结果录入
     */
    public static final String PENDING = "PENDING";

    /**
     * 技术审核中（第一层审核）
     */
    public static final String TECHNICAL_REVIEWING = "TECHNICAL_REVIEWING";

    /**
     * 技术审核通过
     */
    public static final String TECHNICAL_APPROVED = "TECHNICAL_APPROVED";

    /**
     * 技术审核驳回
     */
    public static final String TECHNICAL_REJECTED = "TECHNICAL_REJECTED";

    /**
     * 临床审核中（第二层审核）
     */
    public static final String CLINICAL_REVIEWING = "CLINICAL_REVIEWING";

    /**
     * 临床审核通过
     */
    public static final String CLINICAL_APPROVED = "CLINICAL_APPROVED";

    /**
     * 临床审核驳回
     */
    public static final String CLINICAL_REJECTED = "CLINICAL_REJECTED";

    /**
     * 已发布
     */
    public static final String PUBLISHED = "PUBLISHED";

    /**
     * 已归档
     */
    public static final String ARCHIVED = "ARCHIVED";

    /**
     * 已撤销
     */
    public static final String REVOKED = "REVOKED";

    // ==================== 兼容老版本状态 ====================
    /**
     * 审核中（兼容旧版）
     */
    public static final String REVIEWING = "REVIEWING";

    /**
     * 已通过（兼容旧版）
     */
    public static final String APPROVED = "APPROVED";

    /**
     * 已驳回（兼容旧版）
     */
    public static final String REJECTED = "REJECTED";

    // ==================== 状态管理方法 ====================

    /**
     * 获取所有状态列表
     */
    public static List<String> getAllStatuses() {
        return Arrays.asList(
                PENDING,
                TECHNICAL_REVIEWING,
                TECHNICAL_APPROVED,
                TECHNICAL_REJECTED,
                CLINICAL_REVIEWING,
                CLINICAL_APPROVED,
                CLINICAL_REJECTED,
                PUBLISHED,
                ARCHIVED,
                REVOKED
        );
    }

    /**
     * 获取所有技术审核相关状态
     */
    public static List<String> getTechnicalReviewStatuses() {
        return Arrays.asList(
                TECHNICAL_REVIEWING,
                TECHNICAL_APPROVED,
                TECHNICAL_REJECTED
        );
    }

    /**
     * 获取所有临床审核相关状态
     */
    public static List<String> getClinicalReviewStatuses() {
        return Arrays.asList(
                CLINICAL_REVIEWING,
                CLINICAL_APPROVED,
                CLINICAL_REJECTED
        );
    }

    /**
     * 获取待处理状态（需要操作员关注的状态）
     */
    public static List<String> getPendingStatuses() {
        return Arrays.asList(
                PENDING,
                TECHNICAL_REVIEWING,
                CLINICAL_REVIEWING
        );
    }

    /**
     * 获取已完成状态
     */
    public static List<String> getCompletedStatuses() {
        return Arrays.asList(
                PUBLISHED,
                ARCHIVED
        );
    }

    /**
     * 获取异常状态
     */
    public static List<String> getAbnormalStatuses() {
        return Arrays.asList(
                TECHNICAL_REJECTED,
                CLINICAL_REJECTED,
                REVOKED
        );
    }

    /**
     * 检查状态是否有效
     */
    public static boolean isValidStatus(String status) {
        if (status == null) {
            return false;
        }
        
        Set<String> validStatuses = new HashSet<>(getAllStatuses());
        // 添加兼容状态
        validStatuses.add(REVIEWING);
        validStatuses.add(APPROVED);
        validStatuses.add(REJECTED);
        
        return validStatuses.contains(status);
    }

    /**
     * 检查状态是否为待处理状态
     */
    public static boolean isPendingStatus(String status) {
        return getPendingStatuses().contains(status);
    }

    /**
     * 检查状态是否为技术审核状态
     */
    public static boolean isTechnicalReviewStatus(String status) {
        return getTechnicalReviewStatuses().contains(status);
    }

    /**
     * 检查状态是否为临床审核状态
     */
    public static boolean isClinicalReviewStatus(String status) {
        return getClinicalReviewStatuses().contains(status);
    }

    /**
     * 检查状态是否允许发布
     */
    public static boolean canPublish(String status) {
        return CLINICAL_APPROVED.equals(status) || APPROVED.equals(status);
    }

    /**
     * 获取状态描述
     */
    public static String getStatusDescription(String status) {
        switch (status) {
            case PENDING: return "待检验结果录入";
            case TECHNICAL_REVIEWING: return "技术审核中";
            case TECHNICAL_APPROVED: return "技术审核通过";
            case TECHNICAL_REJECTED: return "技术审核驳回";
            case CLINICAL_REVIEWING: return "临床审核中";
            case CLINICAL_APPROVED: return "临床审核通过";
            case CLINICAL_REJECTED: return "临床审核驳回";
            case PUBLISHED: return "已发布";
            case ARCHIVED: return "已归档";
            case REVOKED: return "已撤销";
            case REVIEWING: return "审核中（兼容）";
            case APPROVED: return "已通过（兼容）";
            case REJECTED: return "已驳回（兼容）";
            default: return "未知状态";
        }
    }

    /**
     * 将旧版状态转换为新版状态
     */
    public static String convertToNewStatus(String oldStatus) {
        switch (oldStatus) {
            case REVIEWING: return TECHNICAL_REVIEWING;
            case APPROVED: return CLINICAL_APPROVED;
            case REJECTED: return TECHNICAL_REJECTED;
            default: return oldStatus;
        }
    }

    /**
     * 检查状态是否可以转移到目标状态
     */
    public static boolean canTransitionTo(String currentStatus, String targetStatus) {
        // 定义状态转换规则
        switch (currentStatus) {
            case PENDING:
                return targetStatus.equals(TECHNICAL_REVIEWING);
            case TECHNICAL_REVIEWING:
                return targetStatus.equals(TECHNICAL_APPROVED) || 
                       targetStatus.equals(TECHNICAL_REJECTED);
            case TECHNICAL_APPROVED:
                return targetStatus.equals(CLINICAL_REVIEWING);
            case TECHNICAL_REJECTED:
                return targetStatus.equals(PENDING); // 驳回后可重新录入
            case CLINICAL_REVIEWING:
                return targetStatus.equals(CLINICAL_APPROVED) || 
                       targetStatus.equals(CLINICAL_REJECTED);
            case CLINICAL_APPROVED:
                return targetStatus.equals(PUBLISHED);
            case CLINICAL_REJECTED:
                return targetStatus.equals(TECHNICAL_REVIEWING); // 临床驳回回到技术审核
            case PUBLISHED:
                return targetStatus.equals(ARCHIVED);
            case ARCHIVED:
                return false; // 归档后不可再修改
            default:
                return false;
        }
    }
}
