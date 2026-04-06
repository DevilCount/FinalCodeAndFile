package com.sunyaxin.common.utils;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.core.script.DefaultRedisScript;
import org.springframework.stereotype.Component;

import java.util.*;
import java.util.concurrent.TimeUnit;

/**
 * Redis工具类
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class RedisUtils {

    private final RedisTemplate<String, Object> redisTemplate;

    // ==================== 常用操作 ====================

    /**
     * 设置缓存
     */
    public void set(String key, Object value) {
        redisTemplate.opsForValue().set(key, value);
    }

    /**
     * 设置缓存并设置过期时间
     */
    public void set(String key, Object value, long timeout, TimeUnit unit) {
        redisTemplate.opsForValue().set(key, value, timeout, unit);
    }

    /**
     * 设置缓存并设置过期时间（秒）
     */
    public void setEx(String key, Object value, long seconds) {
        set(key, value, seconds, TimeUnit.SECONDS);
    }

    /**
     * 获取缓存
     */
    @SuppressWarnings("unchecked")
    public <T> T get(String key) {
        return (T) redisTemplate.opsForValue().get(key);
    }

    /**
     * 删除缓存
     */
    public Boolean delete(String key) {
        return redisTemplate.delete(key);
    }

    /**
     * 批量删除缓存
     */
    public Long delete(Collection<String> keys) {
        return redisTemplate.delete(keys);
    }

    /**
     * 判断key是否存在
     */
    public Boolean hasKey(String key) {
        return redisTemplate.hasKey(key);
    }

    /**
     * 设置过期时间
     */
    public Boolean expire(String key, long timeout, TimeUnit unit) {
        return redisTemplate.expire(key, timeout, unit);
    }

    /**
     * 获取过期时间
     */
    public Long getExpire(String key) {
        return redisTemplate.getExpire(key);
    }

    // ==================== 自增/自减 ====================

    /**
     * 自增
     */
    public Long increment(String key) {
        return redisTemplate.opsForValue().increment(key);
    }

    /**
     * 自增指定值
     */
    public Long increment(String key, long delta) {
        return redisTemplate.opsForValue().increment(key, delta);
    }

    /**
     * 自减
     */
    public Long decrement(String key) {
        return redisTemplate.opsForValue().decrement(key);
    }

    /**
     * 自减指定值
     */
    public Long decrement(String key, long delta) {
        return redisTemplate.opsForValue().decrement(key, delta);
    }

    // ==================== Hash操作 ====================

    /**
     * 设置Hash值
     */
    public void hSet(String key, String field, Object value) {
        redisTemplate.opsForHash().put(key, field, value);
    }

    /**
     * 获取Hash值
     */
    public <T> T hGet(String key, String field) {
        return (T) redisTemplate.opsForHash().get(key, field);
    }

    /**
     * 获取所有Hash值
     */
    public Map<Object, Object> hGetAll(String key) {
        return redisTemplate.opsForHash().entries(key);
    }

    /**
     * 删除Hash字段
     */
    public Long hDelete(String key, Object... fields) {
        return redisTemplate.opsForHash().delete(key, fields);
    }

    /**
     * 判断Hash字段是否存在
     */
    public Boolean hHasKey(String key, String field) {
        return redisTemplate.opsForHash().hasKey(key, field);
    }

    // ==================== List操作 ====================

    /**
     * 左侧入队
     */
    public Long lLeftPush(String key, Object value) {
        return redisTemplate.opsForList().leftPush(key, value);
    }

    /**
     * 右侧入队
     */
    public Long lRightPush(String key, Object value) {
        return redisTemplate.opsForList().rightPush(key, value);
    }

    /**
     * 获取列表范围
     */
    public List<Object> lRange(String key, long start, long end) {
        return redisTemplate.opsForList().range(key, start, end);
    }

    /**
     * 获取列表长度
     */
    public Long lSize(String key) {
        return redisTemplate.opsForList().size(key);
    }

    // ==================== Set操作 ====================

    /**
     * 添加到Set
     */
    public Long sAdd(String key, Object... values) {
        return redisTemplate.opsForSet().add(key, values);
    }

    /**
     * 获取Set所有成员
     */
    public Set<Object> sMembers(String key) {
        return redisTemplate.opsForSet().members(key);
    }

    /**
     * 判断是否Set成员
     */
    public Boolean sIsMember(String key, Object value) {
        return redisTemplate.opsForSet().isMember(key, value);
    }

    // ==================== 分布式锁 ====================

    /**
     * 尝试获取分布式锁
     * @param lockKey 锁key
     * @param value 锁value（使用唯一标识）
     * @param timeout 超时时间（秒）
     * @return 是否成功获取锁
     */
    public Boolean tryLock(String lockKey, String value, long timeout) {
        return redisTemplate.opsForValue().setIfAbsent(lockKey, value, timeout, TimeUnit.SECONDS);
    }

    /**
     * 释放分布式锁
     * @param lockKey 锁key
     * @param value 锁value（只能释放自己的锁）
     * @return 是否成功释放
     */
    public Boolean unlock(String lockKey, String value) {
        String script = "if redis.call('get', KEYS[1]) == ARGV[1] then return redis.call('del', KEYS[1]) else return 0 end";
        DefaultRedisScript<Long> redisScript = new DefaultRedisScript<>(script, Long.class);
        Long result = redisTemplate.execute(redisScript, Collections.singletonList(lockKey), value);
        return result != null && result > 0;
    }

    // ==================== 缓存过期策略 ====================

    /**
     * 用户信息缓存（默认30分钟）
     */
    public static final long USER_CACHE_EXPIRE = 30 * 60;

    /**
     * 字典信息缓存（默认24小时）
     */
    public static final long DICT_CACHE_EXPIRE = 24 * 60 * 60;

    /**
     * 检验项目缓存（默认1小时）
     */
    public static final long ITEM_CACHE_EXPIRE = 60 * 60;

    /**
     * 接口限流缓存（默认1分钟）
     */
    public static final long RATE_LIMIT_EXPIRE = 60;

    // ==================== 限流操作 ====================

    /**
     * 固定窗口限流
     * @param key 限流key
     * @param maxRequests 最大请求数
     * @param windowSeconds 时间窗口（秒）
     * @return 是否允许通过
     */
    public boolean fixedWindowRateLimit(String key, int maxRequests, int windowSeconds) {
        String countKey = "rate_limit:fixed:" + key;
        Long count = increment(countKey);
        if (count == 1) {
            expire(countKey, windowSeconds, TimeUnit.SECONDS);
        }
        return count <= maxRequests;
    }

    /**
     * 滑动窗口限流
     * @param key 限流key
     * @param maxRequests 最大请求数
     * @param windowSeconds 时间窗口（秒）
     * @return 是否允许通过
     */
    public boolean slidingWindowRateLimit(String key, int maxRequests, int windowSeconds) {
        String listKey = "rate_limit:sliding:" + key;
        long now = System.currentTimeMillis();
        long windowStart = now - windowSeconds * 1000;

        // 移除窗口外的请求记录
        redisTemplate.opsForZSet().removeRangeByScore(listKey, 0, windowStart);

        // 获取当前请求数
        Long count = redisTemplate.opsForZSet().zCard(listKey);

        if (count != null && count >= maxRequests) {
            return false;
        }

        // 添加当前请求记录
        redisTemplate.opsForZSet().add(listKey, String.valueOf(now), now);
        // 设置过期时间
        expire(listKey, windowSeconds + 1, TimeUnit.SECONDS);

        return true;
    }
}
