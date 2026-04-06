package com.sunyaxin.sample.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.sunyaxin.common.constant.OperationTypeConstant;
import com.sunyaxin.common.constant.SampleStatusConstant;
import com.sunyaxin.common.entity.OperationLog;
import com.sunyaxin.common.entity.Sample;
import com.sunyaxin.common.entity.SampleTrace;
import com.sunyaxin.common.result.Result;
import com.sunyaxin.common.service.OperationLogService;
import com.sunyaxin.common.utils.CodeGenerator;
import com.sunyaxin.sample.dto.DashboardStatsDTO;
import com.sunyaxin.sample.dto.SampleStatusStatsDTO;
import com.sunyaxin.sample.mapper.SampleMapper;
import com.sunyaxin.sample.mapper.SampleTraceMapper;
import com.sunyaxin.sample.service.SampleService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.CacheConfig;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 标本Service实现类
 */
@Slf4j
@Service
@RequiredArgsConstructor
@CacheConfig(cacheNames = "sample")
public class SampleServiceImpl extends ServiceImpl<SampleMapper, Sample> implements SampleService {

    private final SampleTraceMapper traceMapper;
    private final OperationLogService operationLogService;

    @Override
    @Transactional(rollbackFor = Exception.class)
    @CacheEvict(allEntries = true)
    public Result<Sample> createSample(Sample sample) {
        log.info("==> 开始创建标本，患者: {}", sample.getPatientName());

        // ========== 参数校验（对应数据库 NOT NULL 约束） ==========
        if (sample.getPatientName() == null || sample.getPatientName().trim().isEmpty()) {
            log.warn("创建标本失败：患者姓名为空");
            return Result.badRequest("患者姓名不能为空");
        }
        if (sample.getTestItems() == null || sample.getTestItems().trim().isEmpty()) {
            log.warn("创建标本失败：检验项目为空");
            return Result.badRequest("检验项目不能为空");
        }

        try {
            // 生成标本编号
            sample.setSampleNo(CodeGenerator.generateSampleNo());
            sample.setStatus(SampleStatusConstant.COLLECTED);
            sample.setCollectTime(LocalDateTime.now());

            log.info("==> 保存标本信息, 编号: {}", sample.getSampleNo());
            this.save(sample);

            if (sample.getId() == null) {
                log.error("标本保存后ID为空");
                throw new RuntimeException("标本保存失败：未获取到标本ID");
            }

            log.info("==> 标本保存成功, ID: {}, 编号: {}", sample.getId(), sample.getSampleNo());

            // 创建追踪记录
            SampleTrace trace = new SampleTrace();
            trace.setSampleId(sample.getId());
            trace.setSampleNo(sample.getSampleNo());
            trace.setOperationType("COLLECT");
            trace.setOperationDesc("标本采集");
            trace.setOperatorId(sample.getDoctorId());
            trace.setOperatorName(sample.getDoctorName());
            trace.setLocation(sample.getCollectLocation());
            traceMapper.insert(trace);

            log.info("==> 追踪记录创建成功");

            // 记录操作日志
            operationLogService.recordOperation(
                    OperationTypeConstant.MODULE_SAMPLE,
                    OperationTypeConstant.SAMPLE_CREATE,
                    "创建标本: " + sample.getSampleNo(),
                    "Sample",
                    sample.getId(),
                    sample.getSampleNo(),
                    sample.getDoctorId(),
                    sample.getDoctorName(),
                    null
            );

            log.info("==> 创建标本成功: {} | 患者: {}", sample.getSampleNo(), sample.getPatientName());
            return Result.success("创建成功", sample);

        } catch (Exception e) {
            log.error("创建标本异常: {}", e.getMessage(), e);
            // 返回错误信息而非抛出异常，避免500错误
            return Result.error("创建标本失败: " + e.getMessage());
        }
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    @CacheEvict(allEntries = true)
    public Result<Sample> updateStatus(Long sampleId, String status, Long operatorId, String operatorName, String location) {
        Sample sample = this.getById(sampleId);
        if (sample == null) {
            return Result.error("标本不存在");
        }

        String oldStatus = sample.getStatus();
        sample.setStatus(status);

        // 根据不同状态更新相应字段
        if (SampleStatusConstant.RECEIVED.equals(status)) {
            sample.setReceiveTime(LocalDateTime.now());
            sample.setTechnicianId(operatorId);
            sample.setTechnicianName(operatorName);
        }

        this.updateById(sample);

        // 创建追踪记录
        SampleTrace trace = new SampleTrace();
        trace.setSampleId(sampleId);
        trace.setSampleNo(sample.getSampleNo());
        trace.setOperationType(status);
        trace.setOperationDesc(getStatusDesc(status));
        trace.setOperatorId(operatorId);
        trace.setOperatorName(operatorName);
        trace.setLocation(location);
        traceMapper.insert(trace);

        // 记录操作日志
        String operationType = getOperationType(status);
        String operationDesc = getStatusDesc(status) + " [" + sample.getSampleNo() + "]";
        operationLogService.recordOperation(
                OperationTypeConstant.MODULE_SAMPLE,
                operationType,
                operationDesc,
                "Sample",
                sampleId,
                sample.getSampleNo(),
                operatorId,
                operatorName,
                "状态变更: " + oldStatus + " -> " + status
        );

        log.info("==> 标本状态更新: {} | {} -> {} | 操作人: {}", 
                sample.getSampleNo(), oldStatus, status, operatorName);
        return Result.success("状态更新成功", sample);
    }

    @Override
    @Cacheable(key = "'trace:' + #sampleId")
    public Result<List<SampleTrace>> getTraceRecords(Long sampleId) {
        List<SampleTrace> traces = traceMapper.selectBySampleId(sampleId);
        return Result.success(traces);
    }

    @Override
    @Cacheable(key = "'scan:' + #sampleNo")
    public Result<Sample> scanSample(String sampleNo) {
        Sample sample = baseMapper.selectBySampleNo(sampleNo);
        if (sample == null) {
            return Result.error("标本不存在");
        }
        return Result.success(sample);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public Result<Sample> receiveSample(Long sampleId, Long technicianId, String technicianName) {
        return updateStatus(sampleId, SampleStatusConstant.RECEIVED, technicianId, technicianName, "检验科");
    }

    /**
     * 获取状态对应的操作类型
     */
    private String getOperationType(String status) {
        Map<String, String> opMap = new HashMap<>();
        opMap.put(SampleStatusConstant.COLLECTED, OperationTypeConstant.SAMPLE_CREATE);
        opMap.put(SampleStatusConstant.RECEIVED, OperationTypeConstant.SAMPLE_RECEIVE);
        opMap.put(SampleStatusConstant.TESTING, OperationTypeConstant.SAMPLE_START_TEST);
        opMap.put(SampleStatusConstant.COMPLETED, OperationTypeConstant.SAMPLE_COMPLETE);
        opMap.put(SampleStatusConstant.ARCHIVED, OperationTypeConstant.SAMPLE_ARCHIVE);
        opMap.put(SampleStatusConstant.ABNORMAL, OperationTypeConstant.SAMPLE_ABNORMAL);
        return opMap.getOrDefault(status, "UPDATE_STATUS");
    }

    /**
     * 获取状态描述
     */
    private String getStatusDesc(String status) {
        Map<String, String> descMap = new HashMap<>();
        descMap.put(SampleStatusConstant.COLLECTED, "标本采集");
        descMap.put(SampleStatusConstant.IN_TRANSIT, "标本运输");
        descMap.put(SampleStatusConstant.RECEIVED, "标本签收");
        descMap.put(SampleStatusConstant.TESTING, "开始检验");
        descMap.put(SampleStatusConstant.COMPLETED, "检验完成");
        descMap.put(SampleStatusConstant.ARCHIVED, "标本归档");
        descMap.put(SampleStatusConstant.ABNORMAL, "标本异常");
        return descMap.getOrDefault(status, "未知操作");
    }
    
    @Override
    @Cacheable(key = "'search:' + #keyword + ':' + #status + ':' + #sampleType + ':' + #startDate + ':' + #endDate")
    public Result<List<Sample>> searchSamples(String keyword, String status, String sampleType,
                                               LocalDate startDate, LocalDate endDate) {
        log.info("==> 条件查询标本，关键字: {}, 状态: {}, 标本类型: {}, 开始日期: {}, 结束日期: {}", 
                keyword, status, sampleType, startDate, endDate);
        
        // 构建查询条件
        Map<String, Object> params = new HashMap<>();
        if (keyword != null && !keyword.trim().isEmpty()) {
            params.put("keyword", keyword);
        }
        if (status != null && !status.trim().isEmpty()) {
            params.put("status", status);
        }
        if (sampleType != null && !sampleType.trim().isEmpty()) {
            params.put("sampleType", sampleType);
        }
        if (startDate != null) {
            params.put("startDate", startDate);
        }
        if (endDate != null) {
            params.put("endDate", endDate);
        }
        
        // 简化实现：直接查询所有标本，然后在内存中过滤（实际项目应使用数据库查询）
        List<Sample> allSamples = this.list();
        List<Sample> filteredSamples = new ArrayList<>();
        
        for (Sample sample : allSamples) {
            boolean match = true;
            
            // 关键字匹配（标本编号或患者姓名）
            if (keyword != null && !keyword.trim().isEmpty()) {
                String kw = keyword.toLowerCase();
                if (!sample.getSampleNo().toLowerCase().contains(kw) && 
                    !sample.getPatientName().toLowerCase().contains(kw)) {
                    match = false;
                }
            }
            
            // 状态匹配
            if (status != null && !status.trim().isEmpty() && !status.equals(sample.getStatus())) {
                match = false;
            }
            
            // 标本类型匹配
            if (sampleType != null && !sampleType.trim().isEmpty() && !sampleType.equals(sample.getSampleType())) {
                match = false;
            }
            
            // 时间范围匹配
            if (startDate != null && sample.getCollectTime() != null && 
                sample.getCollectTime().toLocalDate().isBefore(startDate)) {
                match = false;
            }
            if (endDate != null && sample.getCollectTime() != null && 
                sample.getCollectTime().toLocalDate().isAfter(endDate)) {
                match = false;
            }
            
            if (match) {
                filteredSamples.add(sample);
            }
        }
        
        return Result.success(filteredSamples);
    }
    
    @Override
    @Cacheable(key = "'abnormal'")
    public Result<List<Sample>> getAbnormalSamples() {
        log.info("==> 获取异常标本列表");
        // 简化实现：查询状态为异常的标本
        List<Sample> abnormalSamples = this.lambdaQuery()
                .eq(Sample::getStatus, SampleStatusConstant.ABNORMAL)
                .orderByDesc(Sample::getCreateTime)
                .list();
        return Result.success(abnormalSamples);
    }
    
    @Override
    @Cacheable(key = "'pending'")
    public Result<List<Sample>> getPendingSamples() {
        log.info("==> 获取待处理标本列表");
        // 待处理状态：已采集、运输中、已接收
        List<Sample> pendingSamples = this.lambdaQuery()
                .in(Sample::getStatus, Arrays.asList(
                        SampleStatusConstant.COLLECTED,
                        SampleStatusConstant.IN_TRANSIT,
                        SampleStatusConstant.RECEIVED
                ))
                .orderByDesc(Sample::getCreateTime)
                .list();
        return Result.success(pendingSamples);
    }
    
    @Override
    @Cacheable(key = "'dashboard'")
    public Result<DashboardStatsDTO> getDashboardStats() {
        log.info("==> 获取仪表盘统计数据");
        // 简化实现：返回空数据
        DashboardStatsDTO stats = new DashboardStatsDTO();
        stats.setTodaySampleCount(0L);
        stats.setTodayReportCount(0L);
        stats.setPendingSampleCount(0L);
        stats.setAbnormalReportCount(0L);
        return Result.success(stats);
    }
    
    @Override
    @Cacheable(key = "'statusStats'")
    public Result<List<SampleStatusStatsDTO>> getStatusStats() {
        log.info("==> 获取标本状态分布统计");
        // 简化实现：返回空列表
        return Result.success(new ArrayList<>());
    }
    
    @Override
    @Cacheable(key = "'weeklyTrend'")
    public Result<Map<String, Long>> getWeeklyTrend() {
        log.info("==> 获取近7天标本趋势");
        // 简化实现：返回空映射
        return Result.success(new HashMap<>());
    }
    
    @Override
    @Cacheable(key = "'hotItems'")
    public Result<List<Map<String, Object>>> getHotTestItems() {
        log.info("==> 获取热门检验项目排行");
        // 简化实现：返回空列表
        return Result.success(new ArrayList<>());
    }
    
    @Override
    @Transactional(rollbackFor = Exception.class)
    @CacheEvict(allEntries = true)
    public Result<Sample> markAbnormal(Long sampleId, Long operatorId, String operatorName, String reason) {
        // 更新状态为异常
        Result<Sample> result = updateStatus(sampleId, SampleStatusConstant.ABNORMAL, operatorId, operatorName, "检验科");
        if (result.getCode() == 200) {
            Sample sample = result.getData();
            log.info("==> 标记标本异常: {} | 原因: {} | 操作人: {}", 
                    sample.getSampleNo(), reason, operatorName);
            
            // 可以在这里添加额外的异常处理逻辑，比如发送通知等
            
            return Result.success("标记异常成功", sample);
        }
        return result;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    @CacheEvict(allEntries = true)
    public Result<Integer> batchUpdateStatus(List<Long> sampleIds, String status, Long operatorId, String operatorName) {
        log.info("==> 批量更新标本状态，标本数量: {}, 目标状态: {}", sampleIds.size(), status);
        
        if (sampleIds == null || sampleIds.isEmpty()) {
            return Result.error("标本ID列表不能为空");
        }
        
        // 验证状态有效性
        if (!SampleStatusConstant.isValidStatus(status)) {
            return Result.error("无效的状态: " + status);
        }
        
        int successCount = 0;
        int failCount = 0;
        List<String> errorMessages = new ArrayList<>();
        
        for (Long sampleId : sampleIds) {
            try {
                // 调用现有的updateStatus方法，使用"批量操作"作为location
                Result<Sample> result = updateStatus(sampleId, status, operatorId, operatorName, "批量操作");
                if (result.getCode() == 200) {
                    successCount++;
                } else {
                    failCount++;
                    errorMessages.add("标本ID " + sampleId + " 更新失败: " + result.getMessage());
                }
            } catch (Exception e) {
                failCount++;
                errorMessages.add("标本ID " + sampleId + " 更新失败: " + e.getMessage());
                log.error("批量更新标本状态失败，标本ID: {}", sampleId, e);
            }
        }
        
        // 记录操作日志
        String operationDesc = "批量更新标本状态，成功: " + successCount + "，失败: " + failCount;
        operationLogService.recordOperation(
                OperationTypeConstant.MODULE_SAMPLE,
                OperationTypeConstant.BATCH_OPERATION,
                operationDesc,
                "Sample",
                null,
                null,
                operatorId,
                operatorName,
                "目标状态: " + status + "，处理数量: " + sampleIds.size()
        );
        
        log.info("==> 批量更新完成，成功: {}, 失败: {}", successCount, failCount);
        
        if (failCount > 0) {
            return Result.success("批量更新部分成功，成功" + successCount + "条，失败" + failCount + "条", successCount);
        }
        
        return Result.success("批量更新成功", successCount);
    }
    
    @Override
    public Result<List<Sample>> listByStatus(String status) {
        log.info("==> 根据状态查询标本列表，status: {}", status);
        
        try {
            // 获取所有标本
            List<Sample> allSamples = this.list();
            List<Sample> filteredSamples = new ArrayList<>();
            
            // 在内存中过滤
            String targetStatus = (status != null) ? status.trim() : null;
            for (Sample sample : allSamples) {
                if (targetStatus != null && targetStatus.equals(sample.getStatus())) {
                    filteredSamples.add(sample);
                }
            }
            
            log.info("==> 按状态查询标本成功，status: {}, 数量: {}", targetStatus, filteredSamples.size());
            return Result.success(filteredSamples);
        } catch (Exception e) {
            log.error("按状态查询标本异常: {}", e.getMessage(), e);
            return Result.success(new ArrayList<>());
        }
    }
}
