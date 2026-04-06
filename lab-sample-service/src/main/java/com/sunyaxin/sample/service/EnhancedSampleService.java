package com.sunyaxin.sample.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.sunyaxin.common.entity.Sample;
import com.sunyaxin.common.result.Result;
import com.sunyaxin.sample.dto.DashboardStatsDTO;
import com.sunyaxin.sample.dto.TodoItemDTO;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;

/**
 * 标本服务（增强版）
 * 添加缓存支持和仪表盘统计功能
 */
public interface EnhancedSampleService extends IService<Sample> {

    /**
     * 获取仪表盘统计数据（带缓存）
     */
    DashboardStatsDTO getDashboardStats();

    /**
     * 清除仪表盘缓存
     */
    void clearDashboardCache();

    /**
     * 按状态统计标本数量
     */
    Map<String, Long> countByStatus();

    /**
     * 按日期统计标本数量（最近N天）
     */
    Map<String, Long> countByLastDays(int days);

    /**
     * 获取今日标本统计
     */
    Map<String, Object> getTodayStats();

    /**
     * 获取待办事项列表（用于仪表盘）
     */
    List<TodoItemDTO> getTodoList(Long userId);

    /**
     * 获取检验项目热度排行
     */
    List<Map<String, Object>> getHotTestItems(int limit);

    /**
     * 批量更新标本状态
     */
    Result<String> batchUpdateStatus(List<Long> sampleIds, String status, Long operatorId, String operatorName);

    /**
     * 批量删除标本（逻辑删除）
     */
    Result<String> batchDelete(List<Long> sampleIds, Long operatorId, String operatorName);

    /**
     * 导出标本数据到Excel
     */
    byte[] exportSamplesToExcel(String keyword, String status, String sampleType, LocalDate startDate, LocalDate endDate);

    /**
     * 导入标本数据从Excel
     */
    Result<String> importSamplesFromExcel(byte[] excelData, Long operatorId, String operatorName);
}
