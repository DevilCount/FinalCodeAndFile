package com.sunyaxin.common.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.sunyaxin.common.entity.SampleType;
import com.sunyaxin.common.mapper.SampleTypeMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * 标本类型服务 - 带Redis缓存
 */
@Service
public class SampleTypeService extends ServiceImpl<SampleTypeMapper, SampleType> {

    private static final Logger log = LoggerFactory.getLogger(SampleTypeService.class);
    private static final String CACHE_NAME = "sampleType";

    /**
     * 获取所有启用的标本类型（带缓存）
     */
    @Cacheable(value = CACHE_NAME, key = "'all'")
    public List<SampleType> getAllEnabled() {
        log.info("==> 从数据库加载标本类型字典");
        return this.list(new LambdaQueryWrapper<SampleType>()
                .eq(SampleType::getStatus, 1)
                .orderByAsc(SampleType::getSortOrder));
    }

    /**
     * 根据编码获取标本类型
     */
    @Cacheable(value = CACHE_NAME, key = "'code_' + #typeCode")
    public SampleType getByTypeCode(String typeCode) {
        return this.getOne(new LambdaQueryWrapper<SampleType>()
                .eq(SampleType::getTypeCode, typeCode)
                .eq(SampleType::getStatus, 1));
    }

    /**
     * 清除缓存
     */
    @CacheEvict(value = CACHE_NAME, allEntries = true)
    public void clearCache() {
        log.info("==> 清除标本类型缓存");
    }
}
