package com.sunyaxin.sample.dto;

import lombok.Data;

import java.io.Serializable;
import java.time.LocalDate;
import java.util.List;
import java.util.Map;

/**
 * 仪表盘统计数据DTO
 */
@Data
public class DashboardStatsDTO implements Serializable {
    private static final long serialVersionUID = 1L;

    /**
     * 今日标本总数
     */
    private Long todaySampleCount;

    /**
     * 今日报告总数
     */
    private Long todayReportCount;

    /**
     * 待处理标本数
     */
    private Long pendingSampleCount;

    /**
     * 异常报告数
     */
    private Long abnormalReportCount;

    /**
     * 标本状态分布
     */
    private List<SampleStatusStatsDTO> statusDistribution;

    /**
     * 近7天标本趋势（日期->数量）
     */
    private Map<String, Long> weeklyTrend;

    /**
     * 近7天报告趋势（日期->数量）
     */
    private Map<String, Long> weeklyReportTrend;

    /**
     * 检验项目热度排行（项目名称->数量）
     */
    private List<Map<String, Object>> hotTestItems;

    /**
     * 设备状态统计
     */
    private Map<String, Long> deviceStatusStats;

    /**
     * 待办事项列表
     */
    private List<TodoItemDTO> todoList;

    /**
     * 危急值提醒列表
     */
    private List<PanicAlertDTO> panicAlerts;
}
