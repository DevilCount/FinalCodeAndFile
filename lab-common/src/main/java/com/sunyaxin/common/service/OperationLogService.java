package com.sunyaxin.common.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.sunyaxin.common.entity.OperationLog;
import com.sunyaxin.common.mapper.OperationLogMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;

/**
 * 操作日志服务
 */
@Service
public class OperationLogService extends ServiceImpl<OperationLogMapper, OperationLog> {

    private static final Logger log = LoggerFactory.getLogger(OperationLogService.class);

    /**
     * 记录操作日志
     */
    @Async
    public void recordLog(OperationLog logEntry) {
        try {
            this.save(logEntry);
            log.info("==> 操作日志记录成功: {} - {}", logEntry.getModule(), logEntry.getOperationType());
        } catch (Exception e) {
            log.error("==> 操作日志记录失败: {}", e.getMessage(), e);
        }
    }

    /**
     * 记录业务操作（快捷方法）
     */
    @Async
    public void recordOperation(String module, String operationType, String operationDesc,
                               String targetType, Long targetId, String targetNo,
                               Long userId, String username, String realName) {
        OperationLog logEntry = new OperationLog();
        logEntry.setModule(module);
        logEntry.setOperationType(operationType);
        logEntry.setOperationDesc(operationDesc);
        logEntry.setTargetType(targetType);
        logEntry.setTargetId(targetId);
        logEntry.setTargetNo(targetNo);
        logEntry.setUserId(userId);
        logEntry.setUsername(username);
        logEntry.setRealName(realName);
        logEntry.setStatus("SUCCESS");
        logEntry.setCreateTime(LocalDateTime.now());
        
        this.recordLog(logEntry);
    }

    /**
     * 根据模块查询操作日志
     */
    public List<OperationLog> getLogsByModule(String module) {
        return this.list(new LambdaQueryWrapper<OperationLog>()
                .eq(OperationLog::getModule, module)
                .orderByDesc(OperationLog::getCreateTime));
    }

    /**
     * 根据对象查询操作日志
     */
    public List<OperationLog> getLogsByTarget(String targetType, Long targetId) {
        return this.list(new LambdaQueryWrapper<OperationLog>()
                .eq(OperationLog::getTargetType, targetType)
                .eq(OperationLog::getTargetId, targetId)
                .orderByDesc(OperationLog::getCreateTime));
    }

    /**
     * 根据对象编号查询操作日志
     */
    public List<OperationLog> getLogsByTargetNo(String targetNo) {
        return this.list(new LambdaQueryWrapper<OperationLog>()
                .eq(OperationLog::getTargetNo, targetNo)
                .orderByDesc(OperationLog::getCreateTime));
    }

    /**
     * 根据用户查询操作日志
     */
    public List<OperationLog> getLogsByUser(Long userId) {
        return this.list(new LambdaQueryWrapper<OperationLog>()
                .eq(OperationLog::getUserId, userId)
                .orderByDesc(OperationLog::getCreateTime));
    }

    /**
     * 查询时间范围内的操作日志
     */
    public List<OperationLog> getLogsByTimeRange(LocalDateTime startTime, LocalDateTime endTime) {
        return this.list(new LambdaQueryWrapper<OperationLog>()
                .between(OperationLog::getCreateTime, startTime, endTime)
                .orderByDesc(OperationLog::getCreateTime));
    }
}
