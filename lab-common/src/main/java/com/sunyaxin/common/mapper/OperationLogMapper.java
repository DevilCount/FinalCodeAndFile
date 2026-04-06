package com.sunyaxin.common.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.sunyaxin.common.entity.OperationLog;
import org.apache.ibatis.annotations.Mapper;

/**
 * 操作日志Mapper
 */
@Mapper
public interface OperationLogMapper extends BaseMapper<OperationLog> {
}
