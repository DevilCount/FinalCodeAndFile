package com.sunyaxin.common.aspect;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.aspectj.lang.JoinPoint;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.*;
import org.aspectj.lang.reflect.MethodSignature;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

import jakarta.servlet.http.HttpServletRequest;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

/**
 * 请求日志AOP切面
 */
@Aspect
@Component
public class LogAspect {

    private static final Logger log = LoggerFactory.getLogger(LogAspect.class);
    private final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * 切入点：所有Controller包下的public方法
     */
    @Pointcut("execution(public com.sunyaxin.common.result.Result *(..))")
    public void controllerPointcut() {}

    /**
     * 环绕通知：记录请求和响应
     */
    @Around("controllerPointcut()")
    public Object around(ProceedingJoinPoint joinPoint) throws Throwable {
        long startTime = System.currentTimeMillis();
        
        ServletRequestAttributes attributes = (ServletRequestAttributes) RequestContextHolder.getRequestAttributes();
        HttpServletRequest request = attributes != null ? attributes.getRequest() : null;
        
        if (request == null) {
            return joinPoint.proceed();
        }

        String className = joinPoint.getTarget().getClass().getSimpleName();
        String methodName = joinPoint.getSignature().getName();
        String requestUri = request.getRequestURI();
        String httpMethod = request.getMethod();

        // 记录请求参数
        try {
            Map<String, Object> requestParams = getRequestParams(joinPoint);
            log.info("==> 请求开始: {} {} {}.{} | 参数: {}", 
                    httpMethod, requestUri, className, methodName, 
                    truncate(safeWriteValueAsString(requestParams)));
        } catch (Exception e) {
            log.info("==> 请求开始: {} {} {}.{} | 参数: (序列化失败)", 
                    httpMethod, requestUri, className, methodName);
        }

        Object result = null;
        try {
            result = joinPoint.proceed();
            long costTime = System.currentTimeMillis() - startTime;
            
            // 记录响应结果
            if (result != null) {
                try {
                    String resultStr = truncate(safeWriteValueAsString(result));
                    log.info("==> 请求完成: {} {} | 耗时: {}ms | 结果: {}", 
                            httpMethod, requestUri, costTime, resultStr);
                } catch (Exception e) {
                    log.info("==> 请求完成: {} {} | 耗时: {}ms | 结果: (序列化失败)", 
                            httpMethod, requestUri, costTime);
                }
            } else {
                log.info("==> 请求完成: {} {} | 耗时: {}ms", httpMethod, requestUri, costTime);
            }
            
            return result;
        } catch (Exception e) {
            long costTime = System.currentTimeMillis() - startTime;
            log.error("==> 请求异常: {} {} | 耗时: {}ms | 错误: {}", 
                    httpMethod, requestUri, costTime, e.getMessage());
            throw e;
        }
    }
    
    /**
     * 安全的JSON序列化
     */
    private String safeWriteValueAsString(Object obj) {
        try {
            return objectMapper.writeValueAsString(obj);
        } catch (Exception e) {
            return "(无法序列化: " + obj.getClass().getSimpleName() + ")";
        }
    }

    /**
     * 获取请求参数
     */
    private Map<String, Object> getRequestParams(JoinPoint joinPoint) {
        Map<String, Object> params = new HashMap<>();
        
        // 获取方法参数
        Object[] args = joinPoint.getArgs();
        MethodSignature signature = (MethodSignature) joinPoint.getSignature();
        String[] parameterNames = signature.getParameterNames();
        
        if (parameterNames != null && args != null) {
            for (int i = 0; i < parameterNames.length; i++) {
                // 排除文件上传和敏感参数
                if (args[i] != null && !args[i].toString().contains("MultipartFile")) {
                    params.put(parameterNames[i], args[i]);
                }
            }
        }
        
        // 尝试从request中获取更多参数
        try {
            ServletRequestAttributes attributes = (ServletRequestAttributes) RequestContextHolder.getRequestAttributes();
            if (attributes != null) {
                HttpServletRequest request = attributes.getRequest();
                // 添加URL参数
                Map<String, String[]> urlParams = request.getParameterMap();
                if (!urlParams.isEmpty()) {
                    params.put("_urlParams", urlParams);
                }
            }
        } catch (Exception ignored) {}
        
        return params;
    }

    /**
     * 截断过长字符串
     */
    private String truncate(String str) {
        if (str == null) return null;
        if (str.length() > 500) {
            return str.substring(0, 500) + "...(truncated)";
        }
        return str;
    }
}
