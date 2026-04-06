package com.sunyaxin.common.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.sunyaxin.common.entity.TestItem;
import com.sunyaxin.common.mapper.TestItemMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * 检验项目管理服务 - 带Redis缓存
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class TestItemService extends ServiceImpl<TestItemMapper, TestItem> {

    /**
     * 缓存名称
     */
    private static final String CACHE_NAME = "testItem";

    /**
     * 获取所有启用的检验项目（带缓存）
     */
    @Cacheable(value = CACHE_NAME, key = "'all_enabled'")
    public List<TestItem> getAllEnabledItems() {
        log.info("==> 从数据库加载检验项目字典");
        return this.list(new LambdaQueryWrapper<TestItem>()
                .eq(TestItem::getStatus, 1)
                .eq(TestItem::getDeleted, 0)
                .orderByAsc(TestItem::getCategory)
                .orderByAsc(TestItem::getItemCode));
    }

    /**
     * 根据类别获取检验项目
     */
    @Cacheable(value = CACHE_NAME, key = "'category_' + #category")
    public List<TestItem> getItemsByCategory(String category) {
        return this.list(new LambdaQueryWrapper<TestItem>()
                .eq(TestItem::getStatus, 1)
                .eq(TestItem::getDeleted, 0)
                .eq(TestItem::getCategory, category)
                .orderByAsc(TestItem::getItemCode));
    }

    /**
     * 根据项目编码获取项目
     */
    @Cacheable(value = CACHE_NAME, key = "'code_' + #itemCode")
    public TestItem getByItemCode(String itemCode) {
        return this.getOne(new LambdaQueryWrapper<TestItem>()
                .eq(TestItem::getItemCode, itemCode)
                .eq(TestItem::getStatus, 1));
    }

    /**
     * 清除所有缓存
     */
    @CacheEvict(value = CACHE_NAME, allEntries = true)
    public void clearCache() {
        log.info("==> 清除检验项目缓存");
    }

    /**
     * 更新项目后清除缓存
     */
    @CacheEvict(value = CACHE_NAME, allEntries = true)
    public boolean updateItem(TestItem item) {
        boolean result = this.updateById(item);
        if (result) {
            log.info("==> 更新检验项目成功, 清除缓存: {}", item.getItemCode());
        }
        return result;
    }
}
