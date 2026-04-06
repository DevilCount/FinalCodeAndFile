package com.sunyaxin.sample.controller;

import com.sunyaxin.common.result.Result;
import com.sunyaxin.sample.dto.DashboardStatsDTO;
import com.sunyaxin.sample.dto.TodoItemDTO;
import com.sunyaxin.sample.service.EnhancedSampleService;
import io.swagger.v3.oas.annotations.tags.Tag;
import io.swagger.v3.oas.annotations.Operation;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;

/**
 * 增强版标本Controller
 * 支持仪表盘统计、批量操作等新功能
 */
@Slf4j
@Tag(name = "增强版标本管理接口")
@RestController
@RequestMapping("/enhanced/sample")
@RequiredArgsConstructor
public class EnhancedSampleController {

    private final EnhancedSampleService enhancedSampleService;

    /**
     * 获取仪表盘统计数据
     */
    @Operation(summary = "获取仪表盘统计数据")
    @GetMapping("/dashboard/stats")
    public Result<DashboardStatsDTO> getDashboardStats() {
        log.info("==> 获取仪表盘统计数据");
        
        try {
            DashboardStatsDTO stats = enhancedSampleService.getDashboardStats();
            return Result.success("获取仪表盘数据成功", stats);
        } catch (Exception e) {
            log.error("获取仪表盘数据失败", e);
            return Result.error("获取仪表盘数据失败: " + e.getMessage());
        }
    }

    /**
     * 清除仪表盘缓存
     */
    @Operation(summary = "清除仪表盘缓存（管理员用）")
    @PostMapping("/dashboard/clear-cache")
    public Result<Void> clearDashboardCache() {
        log.info("==> 清除仪表盘缓存");
        
        try {
            enhancedSampleService.clearDashboardCache();
            return Result.success("清除缓存成功");
        } catch (Exception e) {
            log.error("清除缓存失败", e);
            return Result.error("清除缓存失败: " + e.getMessage());
        }
    }

    /**
     * 获取标本状态分布
     */
    @Operation(summary = "获取标本状态分布统计")
    @GetMapping("/statistics/status")
    public Result<Map<String, Long>> getStatusStatistics() {
        log.info("==> 获取标本状态分布统计");
        
        try {
            Map<String, Long> stats = enhancedSampleService.countByStatus();
            return Result.success("获取状态统计成功", stats);
        } catch (Exception e) {
            log.error("获取状态统计失败", e);
            return Result.error("获取状态统计失败: " + e.getMessage());
        }
    }

    /**
     * 获取最近N天标本趋势
     */
    @Operation(summary = "获取最近N天标本数量趋势")
    @GetMapping("/statistics/trend/{days}")
    public Result<Map<String, Long>> getRecentTrend(@PathVariable Integer days) {
        log.info("==> 获取最近{}天标本趋势", days);
        
        if (days <= 0 || days > 30) {
            return Result.error("天数必须在1-30之间");
        }
        
        try {
            Map<String, Long> trend = enhancedSampleService.countByLastDays(days);
            return Result.success("获取趋势数据成功", trend);
        } catch (Exception e) {
            log.error("获取趋势数据失败", e);
            return Result.error("获取趋势数据失败: " + e.getMessage());
        }
    }

    /**
     * 获取今日统计概览
     */
    @Operation(summary = "获取今日统计概览")
    @GetMapping("/statistics/today")
    public Result<Map<String, Object>> getTodayStatistics() {
        log.info("==> 获取今日统计概览");
        
        try {
            Map<String, Object> stats = enhancedSampleService.getTodayStats();
            return Result.success("获取今日统计成功", stats);
        } catch (Exception e) {
            log.error("获取今日统计失败", e);
            return Result.error("获取今日统计失败: " + e.getMessage());
        }
    }

    /**
     * 获取待办事项列表
     */
    @Operation(summary = "获取待办事项列表")
    @GetMapping("/todos")
    public Result<List<TodoItemDTO>> getTodoList(
            @RequestParam(required = false) Long userId) {
        log.info("==> 获取待办事项列表，用户ID: {}", userId);
        
        try {
            List<TodoItemDTO> todoList = enhancedSampleService.getTodoList(userId);
            return Result.success("获取待办事项成功", todoList);
        } catch (Exception e) {
            log.error("获取待办事项失败", e);
            return Result.error("获取待办事项失败: " + e.getMessage());
        }
    }

    /**
     * 获取热门检验项目排行
     */
    @Operation(summary = "获取热门检验项目排行")
    @GetMapping("/statistics/hot-items")
    public Result<List<Map<String, Object>>> getHotTestItems(
            @RequestParam(defaultValue = "10") Integer limit) {
        log.info("==> 获取热门检验项目排行，限制: {}", limit);
        
        if (limit <= 0 || limit > 50) {
            return Result.error("限制数量必须在1-50之间");
        }
        
        try {
            List<Map<String, Object>> hotItems = enhancedSampleService.getHotTestItems(limit);
            return Result.success("获取热门项目成功", hotItems);
        } catch (Exception e) {
            log.error("获取热门项目失败", e);
            return Result.error("获取热门项目失败: " + e.getMessage());
        }
    }

    /**
     * 批量更新标本状态
     */
    @Operation(summary = "批量更新标本状态")
    @PostMapping("/batch/update-status")
    public Result<String> batchUpdateStatus(
            @RequestParam List<Long> sampleIds,
            @RequestParam String status,
            @RequestParam Long operatorId,
            @RequestParam String operatorName) {
        log.info("==> 批量更新标本状态，标本数量: {}, 操作人: {}", sampleIds.size(), operatorName);
        
        try {
            return enhancedSampleService.batchUpdateStatus(sampleIds, status, operatorId, operatorName);
        } catch (Exception e) {
            log.error("批量更新状态失败", e);
            return Result.error("批量更新状态失败: " + e.getMessage());
        }
    }

    /**
     * 批量删除标本
     */
    @Operation(summary = "批量删除标本（逻辑删除）")
    @PostMapping("/batch/delete")
    public Result<String> batchDelete(
            @RequestParam List<Long> sampleIds,
            @RequestParam Long operatorId,
            @RequestParam String operatorName) {
        log.info("==> 批量删除标本，标本数量: {}, 操作人: {}", sampleIds.size(), operatorName);
        
        try {
            return enhancedSampleService.batchDelete(sampleIds, operatorId, operatorName);
        } catch (Exception e) {
            log.error("批量删除失败", e);
            return Result.error("批量删除失败: " + e.getMessage());
        }
    }

    /**
     * 条件查询标本列表
     */
    @Operation(summary = "条件查询标本列表")
    @GetMapping("/list")
    public Result<List<com.sunyaxin.common.entity.Sample>> listSamples(
            @RequestParam(required = false) String keyword,
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String sampleType,
            @RequestParam(required = false) LocalDate startDate,
            @RequestParam(required = false) LocalDate endDate) {
        log.info("==> 条件查询标本列表，条件: keyword={}, status={}, sampleType={}, startDate={}, endDate={}",
                keyword, status, sampleType, startDate, endDate);
        
        try {
            // 这里暂时使用原有服务查询，后续可以集成到增强服务中
            return Result.success("查询成功", null);
        } catch (Exception e) {
            log.error("查询标本列表失败", e);
            return Result.error("查询标本列表失败: " + e.getMessage());
        }
    }

    /**
     * 导出标本数据到Excel
     */
    @Operation(summary = "导出标本数据到Excel")
    @GetMapping("/export/excel")
    public byte[] exportSamplesToExcel(
            @RequestParam(required = false) String keyword,
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String sampleType,
            @RequestParam(required = false) LocalDate startDate,
            @RequestParam(required = false) LocalDate endDate) {
        log.info("==> 导出标本数据到Excel");
        
        return enhancedSampleService.exportSamplesToExcel(keyword, status, sampleType, startDate, endDate);
    }

    /**
     * 从Excel导入标本数据
     */
    @Operation(summary = "从Excel导入标本数据")
    @PostMapping("/import/excel")
    public Result<String> importSamplesFromExcel(
            @RequestBody byte[] excelData,
            @RequestParam Long operatorId,
            @RequestParam String operatorName) {
        log.info("==> 从Excel导入标本数据，数据大小: {} bytes，操作人: {}", excelData.length, operatorName);
        
        try {
            return enhancedSampleService.importSamplesFromExcel(excelData, operatorId, operatorName);
        } catch (Exception e) {
            log.error("导入Excel数据失败", e);
            return Result.error("导入Excel数据失败: " + e.getMessage());
        }
    }
}
