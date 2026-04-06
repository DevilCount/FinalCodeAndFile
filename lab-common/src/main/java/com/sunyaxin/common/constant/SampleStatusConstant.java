package com.sunyaxin.common.constant;

import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * 标本状态常量
 */
public class SampleStatusConstant {

    /**
     * 已采集
     */
    public static final String COLLECTED = "COLLECTED";

    /**
     * 运输中
     */
    public static final String IN_TRANSIT = "IN_TRANSIT";

    /**
     * 已接收
     */
    public static final String RECEIVED = "RECEIVED";

    /**
     * 检验中
     */
    public static final String TESTING = "TESTING";

    /**
     * 已完成
     */
    public static final String COMPLETED = "COMPLETED";

    /**
     * 已归档
     */
    public static final String ARCHIVED = "ARCHIVED";

    /**
     * 异常
     */
    public static final String ABNORMAL = "ABNORMAL";

    /**
     * 待处理（等待接收或检验）
     */
    public static final String PENDING = "PENDING";

    /**
     * 获取所有状态列表
     */
    public static List<String> getAllStatuses() {
        return Arrays.asList(
                COLLECTED,
                PENDING,
                IN_TRANSIT,
                RECEIVED,
                TESTING,
                COMPLETED,
                ARCHIVED,
                ABNORMAL
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
        return validStatuses.contains(status);
    }

    /**
     * 获取待处理状态列表（需要操作员关注的状态）
     */
    public static List<String> getPendingStatuses() {
        return Arrays.asList(
                COLLECTED,
                IN_TRANSIT,
                RECEIVED,
                TESTING
        );
    }

    /**
     * 获取已完成状态列表
     */
    public static List<String> getCompletedStatuses() {
        return Arrays.asList(
                COMPLETED,
                ARCHIVED
        );
    }

    /**
     * 检查状态是否为已完成状态
     */
    public static boolean isCompletedStatus(String status) {
        return getCompletedStatuses().contains(status);
    }

    /**
     * 检查状态是否为待处理状态
     */
    public static boolean isPendingStatus(String status) {
        return getPendingStatuses().contains(status);
    }
}
