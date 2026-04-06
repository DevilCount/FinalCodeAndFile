package com.sunyaxin.common.annotation;

import java.lang.annotation.*;

/**
 * 接口限流注解
 */
@Target({ElementType.METHOD, ElementType.TYPE})
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface RateLimit {

    /**
     * 限流key前缀
     */
    String key() default "rateLimit";

    /**
     * 最大请求数
     */
    int maxRequests() default 100;

    /**
     * 时间窗口（秒）
     */
    int windowSeconds() default 60;

    /**
     * 限流类型：SLIDING-滑动窗口，FIXED-固定窗口
     */
    String type() default "SLIDING";

    /**
     * 超出限流后的提示消息
     */
    String message() default "请求过于频繁，请稍后重试";
}
