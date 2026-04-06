package com.sunyaxin.sample.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.sunyaxin.common.entity.Sample;
import com.sunyaxin.common.entity.SampleTrace;
import com.sunyaxin.common.result.Result;
import com.sunyaxin.sample.dto.DashboardStatsDTO;
import com.sunyaxin.sample.dto.SampleStatusStatsDTO;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;

/**
 * 标本Service接口（增强版）
 */
public interface SampleService extends IService<Sample> {

    /**
     * 创建标本
     */
    Result<Sample> createSample(Sample sample);

    /**
     * 更新标本状态
     */
    Result<Sample> updateStatus(Long sampleId, String status, Long operatorId, String operatorName, String location);

    /**
     * 获取标本追踪记录
     */
    Result<List<SampleTrace>> getTraceRecords(Long sampleId);

    /**
     * 扫码查询标本
     */
    Result<Sample> scanSample(String sampleNo);

    /**
     * 接收标本
     */
    Result<Sample> receiveSample(Long sampleId, Long technicianId, String technicianName);

    /**
     * 获取仪表盘统计数据（带Redis缓存）
     */
    Result<DashboardStatsDTO> getDashboardStats();

    /**
     * 获取标本状态分布统计
     */
    Result<List<SampleStatusStatsDTO>> getStatusStats();

    /**
     * 获取近7天标本趋势
     */
    Result<Map<String, Long>> getWeeklyTrend();

    /**
     * 获取检验项目热度排行
     */
    Result<List<Map<String, Object>>> getHotTestItems();

    /**
     * 获取待处理标本列表
     */
    Result<List<Sample>> getPendingSamples();

    /**
     * 获取异常标本列表
     */
    Result<List<Sample>> getAbnormalSamples();

    /**
     * 条件查询标本列表
     */
    Result<List<Sample>> searchSamples(String keyword, String status, String sampleType,
                                        LocalDate startDate, LocalDate endDate);

    /**
     * 批量更新标本状态
     */
    Result<Integer> batchUpdateStatus(List<Long> sampleIds, String status, Long operatorId, String operatorName);

    /**
     * 标记标本异常
     */
    Result<Sample> markAbnormal(Long sampleId, Long operatorId, String operatorName, String reason);

    /**
     * 根据状态查询标本列表（带完整异常处理）
     */
    Result<List<Sample>> listByStatus(String status);
}
