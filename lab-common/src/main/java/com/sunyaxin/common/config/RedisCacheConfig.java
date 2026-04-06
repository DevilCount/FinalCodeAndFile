package com.sunyaxin.common.config;

import com.fasterxml.jackson.annotation.JsonTypeInfo;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import org.springframework.cache.CacheManager;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.cache.RedisCacheConfiguration;
import org.springframework.data.redis.cache.RedisCacheManager;
import org.springframework.data.redis.cache.RedisCacheWriter;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.serializer.GenericJackson2JsonRedisSerializer;
import org.springframework.data.redis.serializer.RedisSerializationContext;
import org.springframework.data.redis.serializer.StringRedisSerializer;

import java.time.Duration;
import java.util.HashMap;
import java.util.Map;

/**
 * Redis缓存配置类（性能优化版）
 * 启用Spring Cache注解支持，配置多级缓存策略
 */
@Configuration
@EnableCaching
public class RedisCacheConfig {

    /**
     * 配置RedisTemplate - 优化版
     */
    @Bean
    public RedisTemplate<String, Object> redisTemplate(RedisConnectionFactory connectionFactory) {
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(connectionFactory);

        // 使用String序列化器作为key的序列化器
        StringRedisSerializer stringSerializer = new StringRedisSerializer();
        template.setKeySerializer(stringSerializer);
        template.setHashKeySerializer(stringSerializer);

        // 使用JSON序列化器作为value的序列化器
        GenericJackson2JsonRedisSerializer jsonSerializer = new GenericJackson2JsonRedisSerializer(objectMapper());
        template.setValueSerializer(jsonSerializer);
        template.setHashValueSerializer(jsonSerializer);

        // 启用事务支持
        template.setEnableTransactionSupport(true);
        
        template.afterPropertiesSet();
        return template;
    }

    /**
     * 配置CacheManager - 性能优化版
     */
    @Bean
    public CacheManager cacheManager(RedisConnectionFactory connectionFactory) {
        // 配置序列化
        GenericJackson2JsonRedisSerializer jsonSerializer = new GenericJackson2JsonRedisSerializer(objectMapper());
        StringRedisSerializer stringSerializer = new StringRedisSerializer();

        RedisCacheConfiguration defaultConfig = RedisCacheConfiguration.defaultCacheConfig()
                // 默认缓存有效期为30分钟
                .entryTtl(Duration.ofMinutes(30))
                // 使用String序列化器作为key
                .serializeKeysWith(RedisSerializationContext.SerializationPair.fromSerializer(stringSerializer))
                // 使用JSON序列化器作为value
                .serializeValuesWith(RedisSerializationContext.SerializationPair.fromSerializer(jsonSerializer))
                // 不缓存null值
                .disableCachingNullValues()
                // 允许缓存值前缀，便于管理
                .computePrefixWith(cacheName -> cacheName + ":");

        // 为不同缓存区域配置不同的过期时间（更精细的策略）
        Map<String, RedisCacheConfiguration> cacheConfigurations = new HashMap<>();
        
        // 标本相关缓存
        cacheConfigurations.put("sample", defaultConfig.entryTtl(Duration.ofMinutes(20)));
        cacheConfigurations.put("sample:detail", defaultConfig.entryTtl(Duration.ofMinutes(30)));
        cacheConfigurations.put("sample:list", defaultConfig.entryTtl(Duration.ofMinutes(10)));
        
        // 报告相关缓存
        cacheConfigurations.put("report", defaultConfig.entryTtl(Duration.ofMinutes(20)));
        cacheConfigurations.put("report:detail", defaultConfig.entryTtl(Duration.ofMinutes(30)));
        cacheConfigurations.put("report:list", defaultConfig.entryTtl(Duration.ofMinutes(10)));
        
        // 仪表盘数据（更新频繁，缓存时间短）
        cacheConfigurations.put("dashboard", defaultConfig.entryTtl(Duration.ofMinutes(3)));
        cacheConfigurations.put("dashboard:stats", defaultConfig.entryTtl(Duration.ofMinutes(2)));
        
        // 统计数据
        cacheConfigurations.put("statistics", defaultConfig.entryTtl(Duration.ofMinutes(15)));
        cacheConfigurations.put("statistics:hot", defaultConfig.entryTtl(Duration.ofMinutes(10)));
        
        // 用户相关缓存
        cacheConfigurations.put("user", defaultConfig.entryTtl(Duration.ofMinutes(30)));
        cacheConfigurations.put("user:login", defaultConfig.entryTtl(Duration.ofHours(2)));
        cacheConfigurations.put("user:list", defaultConfig.entryTtl(Duration.ofMinutes(15)));
        
        // 字典和配置类数据（长时间缓存）
        cacheConfigurations.put("dict", defaultConfig.entryTtl(Duration.ofHours(12)));
        cacheConfigurations.put("config", defaultConfig.entryTtl(Duration.ofHours(24)));

        return RedisCacheManager.builder(RedisCacheWriter.nonLockingRedisCacheWriter(connectionFactory))
                .cacheDefaults(defaultConfig)
                .withInitialCacheConfigurations(cacheConfigurations)
                .transactionAware()
                .build();
    }

    /**
     * 配置ObjectMapper，支持Java 8日期时间类型
     */
    private ObjectMapper objectMapper() {
        ObjectMapper mapper = new ObjectMapper();
        mapper.registerModule(new JavaTimeModule());
        mapper.disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);
        // 启用类型信息，用于反序列化
        mapper.activateDefaultTyping(
                mapper.getPolymorphicTypeValidator(),
                ObjectMapper.DefaultTyping.NON_FINAL,
                JsonTypeInfo.As.PROPERTY
        );
        return mapper;
    }
}
