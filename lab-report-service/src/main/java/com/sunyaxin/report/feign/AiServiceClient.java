package com.sunyaxin.report.feign;

import com.sunyaxin.common.config.FeignConfig;
import com.sunyaxin.common.result.Result;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;

import java.util.Map;

/**
 * AI服务客户端（性能优化版）
 * 配置超时和重试策略
 */
@FeignClient(name = "ai-service", configuration = FeignConfig.class, fallback = AiServiceClientFallback.class)
public interface AiServiceClient {

    /**
     * 调用AI辅助诊断
     * 
     * @param requestData 诊断请求数据，包含报告信息、检验结果等
     * @return AI诊断结果
     */
    @PostMapping("/api/ai/diagnose")
    Result<String> diagnose(@RequestBody Map<String, Object> requestData);
}
