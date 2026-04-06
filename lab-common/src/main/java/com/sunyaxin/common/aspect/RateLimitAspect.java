package com.sunyaxin.common.aspect;

import com.sunyaxin.common.annotation.RateLimit;
import com.sunyaxin.common.exception.BusinessException;
import com.sunyaxin.common.result.ResultCode;
import com.sunyaxin.common.utils.RedisUtils;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.reflect.MethodSignature;
import org.springframework.stereotype.Component;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

/**
 * 接口限流切面
 */
@Slf4j
@Aspect
@Component
@RequiredArgsConstructor
public class RateLimitAspect {

    private final RedisUtils redisUtils;

    @Around("@annotation(com.sunyaxin.common.annotation.RateLimit)")
    public Object around(ProceedingJoinPoint joinPoint) throws Throwable {
        MethodSignature signature = (MethodSignature) joinPoint.getSignature();
        RateLimit rateLimit = signature.getMethod().getAnnotation(RateLimit.class);

        // 获取请求信息用于生成唯一key
        ServletRequestAttributes attributes = (ServletRequestAttributes) RequestContextHolder.getRequestAttributes();
        HttpServletRequest request = attributes != null ? attributes.getRequest() : null;

        String ip = getClientIp(request);
        String method = request != null ? request.getRequestURI() : signature.getName();
        String rateLimitKey = rateLimit.key() + ":" + ip + ":" + method;

        boolean allowed;
        if ("FIXED".equalsIgnoreCase(rateLimit.type())) {
            allowed = redisUtils.fixedWindowRateLimit(rateLimitKey, rateLimit.maxRequests(), rateLimit.windowSeconds());
        } else {
            allowed = redisUtils.slidingWindowRateLimit(rateLimitKey, rateLimit.maxRequests(), rateLimit.windowSeconds());
        }

        if (!allowed) {
            log.warn("接口限流触发: {}, 最大请求数: {}, 时间窗口: {}秒",
                    rateLimitKey, rateLimit.maxRequests(), rateLimit.windowSeconds());
            throw new BusinessException("请求过于频繁，请稍后重试");
        }

        return joinPoint.proceed();
    }

    /**
     * 获取客户端IP地址
     */
    private String getClientIp(HttpServletRequest request) {
        if (request == null) {
            return "unknown";
        }
        String ip = request.getHeader("X-Forwarded-For");
        if (ip == null || ip.isEmpty() || "unknown".equalsIgnoreCase(ip)) {
            ip = request.getHeader("X-Real-IP");
        }
        if (ip == null || ip.isEmpty() || "unknown".equalsIgnoreCase(ip)) {
            ip = request.getRemoteAddr();
        }
        if (ip != null && ip.contains(",")) {
            ip = ip.split(",")[0].trim();
        }
        return ip;
    }
}
