package com.sunyaxin.common.config;

import feign.Logger;
import feign.Request;
import feign.Retryer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.concurrent.TimeUnit;

/**
 * Feign客户端配置类（性能优化版）
 * 配置连接超时、读取超时、重试策略等
 */
@Configuration
public class FeignConfig {

    /**
     * 配置Feign日志级别
     * NONE: 不记录日志（默认）
     * BASIC: 仅记录请求方法和URL以及响应状态码和执行时间
     * HEADERS: 记录基本信息以及请求和响应的头信息
     * FULL: 记录请求和响应的头信息、正文和元数据
     */
    @Bean
    Logger.Level feignLoggerLevel() {
        return Logger.Level.BASIC;
    }

    /**
     * 配置请求超时时间
     * connectTimeout: 连接超时时间（毫秒）
     * readTimeout: 读取超时时间（毫秒）
     */
    @Bean
    public Request.Options feignOptions() {
        return new Request.Options(
                5, TimeUnit.SECONDS,      // 连接超时5秒
                10, TimeUnit.SECONDS,     // 读取超时10秒
                true                       // 跟随重定向
        );
    }

    /**
     * 配置重试策略
     * period: 初始重试间隔时间（毫秒）
     * maxPeriod: 最大重试间隔时间（毫秒）
     * maxAttempts: 最大重试次数
     * 
     * 注意：对于非幂等性请求（如POST），请谨慎使用重试
     */
    @Bean
    public Retryer feignRetryer() {
        return new Retryer.Default(
                100,        // 初始间隔100ms
                1000,       // 最大间隔1s
                3           // 最多重试3次（包括第一次）
        );
    }
}
