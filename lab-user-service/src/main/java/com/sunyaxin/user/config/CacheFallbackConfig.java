package com.sunyaxin.user.config;

import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.cache.CacheManager;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.cache.concurrent.ConcurrentMapCacheManager;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import org.springframework.data.redis.cache.RedisCacheManager;

/**
 * 缓存降级配置
 * 当Redis不可用时，使用内存缓存作为后备
 */
@Configuration
@EnableCaching
public class CacheFallbackConfig {

    /**
     * 主缓存管理器 - Redis
     * 由Spring Boot自动配置，如果Redis可用
     */
    
    /**
     * 后备缓存管理器 - 内存缓存
     * 当Redis不可用时使用
     */
    @Bean
    @ConditionalOnMissingBean(name = "cacheManager")
    public CacheManager memoryCacheManager() {
        return new ConcurrentMapCacheManager("user", "sample", "report", "ai");
    }
    
    /**
     * 缓存异常处理器，防止Redis异常影响业务
     */
    @Bean
    public CacheErrorHandler cacheErrorHandler() {
        return new CacheErrorHandler();
    }
    
    /**
     * 自定义缓存错误处理器
     */
    public static class CacheErrorHandler implements org.springframework.cache.interceptor.CacheErrorHandler {
        
        @Override
        public void handleCacheGetError(RuntimeException exception, org.springframework.cache.Cache cache, Object key) {
            // 缓存获取失败时，记录日志但不影响业务
            System.err.println("缓存获取失败，将直接查询数据库: " + exception.getMessage());
        }
        
        @Override
        public void handleCachePutError(RuntimeException exception, org.springframework.cache.Cache cache, Object key, Object value) {
            // 缓存写入失败时，记录日志但不影响业务
            System.err.println("缓存写入失败，业务继续执行: " + exception.getMessage());
        }
        
        @Override
        public void handleCacheEvictError(RuntimeException exception, org.springframework.cache.Cache cache, Object key) {
            // 缓存清除失败时，记录日志但不影响业务
            System.err.println("缓存清除失败: " + exception.getMessage());
        }
        
        @Override
        public void handleCacheClearError(RuntimeException exception, org.springframework.cache.Cache cache) {
            // 缓存清空失败时，记录日志但不影响业务
            System.err.println("缓存清空失败: " + exception.getMessage());
        }
    }
}