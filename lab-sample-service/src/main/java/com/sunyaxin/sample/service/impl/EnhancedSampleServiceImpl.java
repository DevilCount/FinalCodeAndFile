package com.sunyaxin.sample.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.sunyaxin.common.entity.Sample;
import com.sunyaxin.common.result.Result;
import com.sunyaxin.sample.dto.DashboardStatsDTO;
import com.sunyaxin.sample.dto.TodoItemDTO;
import com.sunyaxin.sample.mapper.SampleMapper;
import com.sunyaxin.sample.service.EnhancedSampleService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.util.*;
import java.util.stream.Collectors;

/**
 * 标本服务（增强版）实现类
 * 提供仪表盘统计、缓存支持等增强功能
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class EnhancedSampleServiceImpl extends ServiceImpl<SampleMapper, Sample> implements EnhancedSampleService {

    @Override
    @Cacheable(value = "dashboard", key = "'stats'")
    public DashboardStatsDTO getDashboardStats() {
        log.info("==> 查询仪表盘统计数据（从数据库）");
        
        DashboardStatsDTO stats = new DashboardStatsDTO();
        
        try {
            // 今日开始时间
            LocalDateTime todayStart = LocalDate.now().atStartOfDay();
            LocalDateTime todayEnd = LocalDate.now().atTime(LocalTime.MAX);
            
            // 1. 今日标本数量
            LambdaQueryWrapper<Sample> todayWrapper = new LambdaQueryWrapper<>();
            todayWrapper.between(Sample::getCollectTime, todayStart, todayEnd);
            Long todaySampleCount = this.count(todayWrapper);
            stats.setTodaySampleCount(todaySampleCount);
            
            // 2. 待处理标本数量（已采集、运输中、已接收）
            LambdaQueryWrapper<Sample> pendingWrapper = new LambdaQueryWrapper<>();
            pendingWrapper.in(Sample::getStatus, Arrays.asList("COLLECTED", "IN_TRANSIT", "RECEIVED"));
            Long pendingSampleCount = this.count(pendingWrapper);
            stats.setPendingSampleCount(pendingSampleCount);
            
            // 3. 异常标本数量
            LambdaQueryWrapper<Sample> abnormalWrapper = new LambdaQueryWrapper<>();
            abnormalWrapper.eq(Sample::getStatus, "ABNORMAL");
            Long abnormalSampleCount = this.count(abnormalWrapper);
            stats.setAbnormalReportCount(abnormalSampleCount);
            
            // 4. 今日报告数量（通过检验完成的标本估算）
            LambdaQueryWrapper<Sample> completedTodayWrapper = new LambdaQueryWrapper<>();
            completedTodayWrapper.eq(Sample::getStatus, "COMPLETED")
                               .between(Sample::getCollectTime, todayStart, todayEnd);
            Long todayReportCount = this.count(completedTodayWrapper);
            stats.setTodayReportCount(todayReportCount);
            
            log.info("==> 仪表盘统计: 今日标本={}, 待处理={}, 异常={}, 今日报告={}", 
                    todaySampleCount, pendingSampleCount, abnormalSampleCount, todayReportCount);
            
        } catch (Exception e) {
            log.error("查询仪表盘统计数据失败", e);
            // 返回默认值，避免前端显示异常
            stats.setTodaySampleCount(0L);
            stats.setTodayReportCount(0L);
            stats.setPendingSampleCount(0L);
            stats.setAbnormalReportCount(0L);
        }
        
        return stats;
    }

    @Override
    @CacheEvict(value = {"dashboard", "statistics"}, allEntries = true)
    public void clearDashboardCache() {
        log.info("==> 清除仪表盘缓存");
        // 缓存清除由@CacheEvict注解自动处理
    }

    @Override
    public Map<String, Long> countByStatus() {
        log.info("==> 按状态统计标本数量");
        
        Map<String, Long> result = new LinkedHashMap<>();
        
        try {
            // 定义所有状态
            List<String> statuses = Arrays.asList(
                "PENDING", "COLLECTED", "IN_TRANSIT", "RECEIVED", 
                "TESTING", "COMPLETED", "ABNORMAL", "ARCHIVED"
            );
            
            for (String status : statuses) {
                LambdaQueryWrapper<Sample> wrapper = new LambdaQueryWrapper<>();
                wrapper.eq(Sample::getStatus, status);
                long count = this.count(wrapper);
                result.put(status, count);
            }
            
            log.info("==> 状态统计完成: {}", result);
            
        } catch (Exception e) {
            log.error("按状态统计失败", e);
            // 返回空统计
            for (String status : Arrays.asList("PENDING", "RECEIVED", "TESTING", "COMPLETED", "ABNORMAL")) {
                result.put(status, 0L);
            }
        }
        
        return result;
    }

    @Override
    public Map<String, Long> countByLastDays(int days) {
        log.info("==> 按最近{}天统计标本数量", days);
        
        Map<String, Long> result = new LinkedHashMap<>();
        LocalDate today = LocalDate.now();
        
        try {
            for (int i = days - 1; i >= 0; i--) {
                LocalDate date = today.minusDays(i);
                LocalDateTime dayStart = date.atStartOfDay();
                LocalDateTime dayEnd = date.atTime(LocalTime.MAX);
                
                LambdaQueryWrapper<Sample> wrapper = new LambdaQueryWrapper<>();
                wrapper.between(Sample::getCollectTime, dayStart, dayEnd);
                long count = this.count(wrapper);
                
                result.put(date.toString(), count);
            }
            
            log.info("==> 最近{}天趋势统计完成", days);
            
        } catch (Exception e) {
            log.error("按日期统计失败", e);
            // 返回空数据
            for (int i = days - 1; i >= 0; i--) {
                LocalDate date = today.minusDays(i);
                result.put(date.toString(), 0L);
            }
        }
        
        return result;
    }

    @Override
    public Map<String, Object> getTodayStats() {
        log.info("==> 获取今日标本统计概览");
        
        Map<String, Object> result = new HashMap<>();
        
        try {
            LocalDateTime todayStart = LocalDate.now().atStartOfDay();
            LocalDateTime todayEnd = LocalDate.now().atTime(LocalTime.MAX);
            
            // 总数
            LambdaQueryWrapper<Sample> totalWrapper = new LambdaQueryWrapper<>();
            totalWrapper.between(Sample::getCollectTime, todayStart, todayEnd);
            long total = this.count(totalWrapper);
            result.put("total", total);
            
            // 已完成
            LambdaQueryWrapper<Sample> completedWrapper = new LambdaQueryWrapper<>();
            completedWrapper.eq(Sample::getStatus, "COMPLETED")
                           .between(Sample::getCollectTime, todayStart, todayEnd);
            long completed = this.count(completedWrapper);
            result.put("completed", completed);
            
            // 待处理
            LambdaQueryWrapper<Sample> pendingWrapper = new LambdaQueryWrapper<>();
            pendingWrapper.in(Sample::getStatus, Arrays.asList("COLLECTED", "IN_TRANSIT", "RECEIVED"))
                         .between(Sample::getCollectTime, todayStart, todayEnd);
            long pending = this.count(pendingWrapper);
            result.put("pending", pending);
            
            // 异常
            LambdaQueryWrapper<Sample> abnormalWrapper = new LambdaQueryWrapper<>();
            abnormalWrapper.eq(Sample::getStatus, "ABNORMAL")
                          .between(Sample::getCollectTime, todayStart, todayEnd);
            long abnormal = this.count(abnormalWrapper);
            result.put("abnormal", abnormal);
            
            log.info("==> 今日统计: 总数={}, 完成={}, 待处理={}, 异常={}", total, completed, pending, abnormal);
            
        } catch (Exception e) {
            log.error("获取今日统计失败", e);
            result.put("total", 0L);
            result.put("completed", 0L);
            result.put("pending", 0L);
            result.put("abnormal", 0L);
        }
        
        return result;
    }

    @Override
    public List<TodoItemDTO> getTodoList(Long userId) {
        log.info("==> 获取待办事项列表，用户ID: {}", userId);
        
        List<TodoItemDTO> todoList = new ArrayList<>();
        
        try {
            // 查询待处理的标本（已采集、运输中、已接收、检验中）
            LambdaQueryWrapper<Sample> wrapper = new LambdaQueryWrapper<>();
            wrapper.in(Sample::getStatus, Arrays.asList("COLLECTED", "IN_TRANSIT", "RECEIVED", "TESTING"))
                   .orderByAsc(Sample::getCollectTime)
                   .last("LIMIT 20");  // 限制返回数量
            
            List<Sample> samples = this.list(wrapper);
            
            // 转换为待办事项DTO
            for (Sample sample : samples) {
                TodoItemDTO todo = new TodoItemDTO();
                todo.setSampleId(sample.getId());
                todo.setSampleNo(sample.getSampleNo());
                todo.setPatientName(sample.getPatientName());
                todo.setStatus(sample.getStatus());
                todo.setTestItems(sample.getTestItems());
                todo.setCollectTime(sample.getCollectTime());
                
                // 设置优先级描述
                String priority = getPriorityDesc(sample.getStatus());
                todo.setPriority(priority);
                
                // 设置操作建议
                String actionSuggestion = getActionSuggestion(sample.getStatus());
                todo.setActionSuggestion(actionSuggestion);
                
                todoList.add(todo);
            }
            
            log.info("==> 获取到{}条待办事项", todoList.size());
            
        } catch (Exception e) {
            log.error("获取待办事项列表失败", e);
        }
        
        return todoList;
    }

    @Override
    public List<Map<String, Object>> getHotTestItems(int limit) {
        log.info("==> 获取热门检验项目排行，限制: {}", limit);
        
        List<Map<String, Object>> hotItems = new ArrayList<>();
        
        try {
            // 查询所有标本
            List<Sample> allSamples = this.list();
            
            // 统计每个检验项目的出现次数
            Map<String, Long> itemCountMap = new HashMap<>();
            for (Sample sample : allSamples) {
                if (sample.getTestItems() != null && !sample.getTestItems().trim().isEmpty()) {
                    // 检验项目可能是逗号分隔的多个项目
                    String[] items = sample.getTestItems().split("[,，、]");
                    for (String item : items) {
                        String trimmedItem = item.trim();
                        if (!trimmedItem.isEmpty()) {
                            itemCountMap.merge(trimmedItem, 1L, Long::sum);
                        }
                    }
                }
            }
            
            // 按出现次数排序并取前N个
            List<Map.Entry<String, Long>> sortedEntries = itemCountMap.entrySet().stream()
                .sorted(Map.Entry.<String, Long>comparingByValue().reversed())
                .limit(limit)
                .collect(Collectors.toList());
            
            // 构建结果列表
            int rank = 1;
            for (Map.Entry<String, Long> entry : sortedEntries) {
                Map<String, Object> item = new HashMap<>();
                item.put("rank", rank++);
                item.put("testItem", entry.getKey());
                item.put("count", entry.getValue());
                hotItems.add(item);
            }
            
            log.info("==> 热门检验项目排行: {}", hotItems);
            
        } catch (Exception e) {
            log.error("获取热门检验项目排行失败", e);
        }
        
        return hotItems;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    @CacheEvict(value = {"dashboard", "statistics"}, allEntries = true)
    public Result<String> batchUpdateStatus(List<Long> sampleIds, String status, Long operatorId, String operatorName) {
        log.info("==> 批量更新标本状态，标本数量: {}, 目标状态: {}, 操作人: {}", 
                sampleIds.size(), status, operatorName);
        
        if (sampleIds == null || sampleIds.isEmpty()) {
            return Result.error("标本ID列表不能为空");
        }
        
        if (status == null || status.trim().isEmpty()) {
            return Result.error("目标状态不能为空");
        }
        
        int successCount = 0;
        int failCount = 0;
        List<String> errorMessages = new ArrayList<>();
        
        try {
            for (Long sampleId : sampleIds) {
                try {
                    Sample sample = this.getById(sampleId);
                    if (sample == null) {
                        failCount++;
                        errorMessages.add("标本ID " + sampleId + " 不存在");
                        continue;
                    }
                    
                    String oldStatus = sample.getStatus();
                    sample.setStatus(status);
                    
                    // 根据状态更新时间字段
                    if ("RECEIVED".equals(status)) {
                        sample.setReceiveTime(LocalDateTime.now());
                    } else if ("COMPLETED".equals(status)) {
                        // 完成检验时更新时间（使用updateTime字段记录）
                        sample.setUpdateTime(LocalDateTime.now());
                    }
                    
                    boolean updated = this.updateById(sample);
                    if (updated) {
                        successCount++;
                        log.info("标本 {} 状态更新: {} -> {}", sampleId, oldStatus, status);
                    } else {
                        failCount++;
                        errorMessages.add("标本ID " + sampleId + " 更新失败");
                    }
                } catch (Exception e) {
                    failCount++;
                    errorMessages.add("标本ID " + sampleId + " 更新异常: " + e.getMessage());
                    log.error("更新标本{}状态失败", sampleId, e);
                }
            }
            
            log.info("==> 批量更新完成，成功: {}, 失败: {}", successCount, failCount);
            
            if (failCount > 0) {
                return Result.success("批量更新部分成功（成功" + successCount + "条，失败" + failCount + "条）");
            }
            
            return Result.success("批量更新成功，共" + successCount + "条");
            
        } catch (Exception e) {
            log.error("批量更新标本状态异常", e);
            return Result.error("批量更新失败: " + e.getMessage());
        }
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    @CacheEvict(value = {"dashboard", "statistics"}, allEntries = true)
    public Result<String> batchDelete(List<Long> sampleIds, Long operatorId, String operatorName) {
        log.info("==> 批量删除标本，标本数量: {}, 操作人: {}", sampleIds.size(), operatorName);
        
        if (sampleIds == null || sampleIds.isEmpty()) {
            return Result.error("标本ID列表不能为空");
        }
        
        int successCount = 0;
        int failCount = 0;
        
        try {
            for (Long sampleId : sampleIds) {
                try {
                    // 使用逻辑删除
                    boolean removed = this.removeById(sampleId);
                    if (removed) {
                        successCount++;
                        log.info("标本 {} 已删除", sampleId);
                    } else {
                        failCount++;
                        log.warn("标本 {} 删除失败（可能不存在）", sampleId);
                    }
                } catch (Exception e) {
                    failCount++;
                    log.error("删除标本{}失败", sampleId, e);
                }
            }
            
            log.info("==> 批量删除完成，成功: {}, 失败: {}", successCount, failCount);
            
            if (failCount > 0) {
                return Result.success("批量删除部分成功（成功" + successCount + "条，失败" + failCount + "条）");
            }
            
            return Result.success("批量删除成功，共" + successCount + "条");
            
        } catch (Exception e) {
            log.error("批量删除标本异常", e);
            return Result.error("批量删除失败: " + e.getMessage());
        }
    }

    @Override
    public byte[] exportSamplesToExcel(String keyword, String status, String sampleType, 
                                        LocalDate startDate, LocalDate endDate) {
        log.info("==> 导出标本数据到Excel，条件: keyword={}, status={}, sampleType={}", 
                keyword, status, sampleType);
        
        try {
            // 构建查询条件
            LambdaQueryWrapper<Sample> wrapper = buildQueryWrapper(keyword, status, sampleType, startDate, endDate);
            wrapper.orderByDesc(Sample::getCreateTime);
            
            // 查询数据
            List<Sample> samples = this.list(wrapper);
            
            log.info("==> 查询到{}条标本数据用于导出", samples.size());
            
            // TODO: 使用EasyExcel生成Excel文件
            // 这里简化处理：返回JSON格式的字节数据
            // 实际项目中应使用EasyExcel库生成真正的Excel文件
            StringBuilder sb = new StringBuilder();
            sb.append("标本编号,患者姓名,标本类型,检验项目,状态,采集时间\n");
            
            for (Sample sample : samples) {
                sb.append(sample.getSampleNo()).append(",");
                sb.append(sample.getPatientName()).append(",");
                sb.append(sample.getSampleType() != null ? sample.getSampleType() : "").append(",");
                sb.append(sample.getTestItems() != null ? sample.getTestItems() : "").append(",");
                sb.append(sample.getStatus() != null ? sample.getStatus() : "").append(",");
                sb.append(sample.getCollectTime() != null ? sample.getCollectTime().toString() : "").append("\n");
            }
            
            return sb.toString().getBytes("UTF-8");
            
        } catch (Exception e) {
            log.error("导出标本数据失败", e);
            return new byte[0];
        }
    }

    @Override
    public Result<String> importSamplesFromExcel(byte[] excelData, Long operatorId, String operatorName) {
        log.info("==> 从Excel导入标本数据，数据大小: {} bytes，操作人: {}", 
                excelData != null ? excelData.length : 0, operatorName);
        
        if (excelData == null || excelData.length == 0) {
            return Result.error("Excel数据不能为空");
        }
        
        int successCount = 0;
        int failCount = 0;
        
        try {
            String content = new String(excelData, "UTF-8");
            String[] lines = content.split("\n");
            
            // 跳过表头
            for (int i = 1; i < lines.length; i++) {
                String line = lines[i].trim();
                if (line.isEmpty()) continue;
                
                try {
                    String[] fields = line.split(",");
                    if (fields.length >= 3) {
                        Sample sample = new Sample();
                        sample.setPatientName(fields[1].trim());
                        
                        if (fields.length > 2 && !fields[2].trim().isEmpty()) {
                            sample.setSampleType(fields[2].trim());
                        }
                        if (fields.length > 3 && !fields[3].trim().isEmpty()) {
                            sample.setTestItems(fields[3].trim());
                        }
                        
                        // 生成标本编号
                        sample.setSampleNo(com.sunyaxin.common.utils.CodeGenerator.generateSampleNo());
                        sample.setStatus("COLLECTED");
                        sample.setCollectTime(LocalDateTime.now());
                        sample.setDoctorId(operatorId);
                        sample.setDoctorName(operatorName);
                        
                        this.save(sample);
                        successCount++;
                    }
                } catch (Exception e) {
                    failCount++;
                    log.error("解析第{}行数据失败: {}", i + 1, e.getMessage());
                }
            }
            
            log.info("==> Excel导入完成，成功: {}, 失败: {}", successCount, failCount);
            
            if (failCount > 0) {
                return Result.success("导入部分成功（成功" + successCount + "条，失败" + failCount + "条）");
            }
            
            return Result.success("导入成功，共" + successCount + "条数据");
            
        } catch (Exception e) {
            log.error("导入Excel数据异常", e);
            return Result.error("导入失败: " + e.getMessage());
        }
    }
    
    /**
     * 构建查询条件
     */
    private LambdaQueryWrapper<Sample> buildQueryWrapper(String keyword, String status, String sampleType,
                                                          LocalDate startDate, LocalDate endDate) {
        LambdaQueryWrapper<Sample> wrapper = new LambdaQueryWrapper<>();
        
        // 关键字搜索（标本编号或患者姓名）
        if (keyword != null && !keyword.trim().isEmpty()) {
            wrapper.and(w -> w.like(Sample::getSampleNo, keyword.trim())
                             .or()
                             .like(Sample::getPatientName, keyword.trim()));
        }
        
        // 状态过滤
        if (status != null && !status.trim().isEmpty()) {
            wrapper.eq(Sample::getStatus, status.trim());
        }
        
        // 标本类型过滤
        if (sampleType != null && !sampleType.trim().isEmpty()) {
            wrapper.eq(Sample::getSampleType, sampleType.trim());
        }
        
        // 开始日期
        if (startDate != null) {
            wrapper.ge(Sample::getCollectTime, startDate.atStartOfDay());
        }
        
        // 结束日期
        if (endDate != null) {
            wrapper.le(Sample::getCollectTime, endDate.atTime(LocalTime.MAX));
        }
        
        return wrapper;
    }
    
    /**
     * 获取优先级描述
     */
    private String getPriorityDesc(String status) {
        switch (status) {
            case "COLLECTED":
                return "高";
            case "IN_TRANSIT":
                return "高";
            case "RECEIVED":
                return "中";
            case "TESTING":
                return "中";
            default:
                return "低";
        }
    }
    
    /**
     * 获取操作建议
     */
    private String getActionSuggestion(String status) {
        switch (status) {
            case "COLLECTED":
                return "请尽快安排运输";
            case "IN_TRANSIT":
                return "关注运输进度";
            case "RECEIVED":
                return "请安排检验";
            case "TESTING":
                return "正在检验中";
            default:
                return "";
        }
    }
}
