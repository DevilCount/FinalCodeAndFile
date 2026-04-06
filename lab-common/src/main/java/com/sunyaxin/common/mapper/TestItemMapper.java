package com.sunyaxin.common.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.sunyaxin.common.entity.TestItem;
import org.apache.ibatis.annotations.Mapper;

/**
 * 检验项目Mapper
 */
@Mapper
public interface TestItemMapper extends BaseMapper<TestItem> {
}
