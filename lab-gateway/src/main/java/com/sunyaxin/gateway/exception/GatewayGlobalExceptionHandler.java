package com.sunyaxin.gateway.exception;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.web.reactive.error.ErrorWebExceptionHandler;
import org.springframework.cloud.gateway.support.NotFoundException;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.annotation.Order;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.web.server.ResponseStatusException;
import reactor.core.publisher.Mono;

import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;

@Slf4j
@Order(-1)
@Configuration
public class GatewayGlobalExceptionHandler implements ErrorWebExceptionHandler {

    private final ObjectMapper objectMapper;

    public GatewayGlobalExceptionHandler(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }

    @Override
    public Mono<Void> handle(org.springframework.web.server.ServerWebExchange exchange, Throwable ex) {
        log.error("[Gateway] 异常处理 - 路径: {}, 类型: {}, 消息: {}",
                exchange.getRequest().getPath(), ex.getClass().getName(), ex.getMessage());

        Map<String, Object> errorResponse = new HashMap<>();
        HttpStatusCode status;

        if (ex instanceof NotFoundException) {
            status = HttpStatus.NOT_FOUND;
            errorResponse.put("code", 404);
            errorResponse.put("message", "服务或路由不存在: " + ex.getMessage());
        } else if (ex instanceof ResponseStatusException) {
            ResponseStatusException rse = (ResponseStatusException) ex;
            status = rse.getStatusCode();
            errorResponse.put("code", status.value());
            errorResponse.put("message", rse.getReason());
        } else if (isConnectionError(ex)) {
            status = HttpStatus.BAD_GATEWAY;
            errorResponse.put("code", 502);
            errorResponse.put("message", "目标服务暂时不可用，请稍后重试");
        } else if (isTimeoutError(ex)) {
            status = HttpStatus.GATEWAY_TIMEOUT;
            errorResponse.put("code", 504);
            errorResponse.put("message", "服务响应超时，请稍后重试");
        } else {
            status = HttpStatus.INTERNAL_SERVER_ERROR;
            errorResponse.put("code", 500);
            errorResponse.put("message", "网关内部错误");
        }

        errorResponse.put("timestamp", System.currentTimeMillis());
        errorResponse.put("path", exchange.getRequest().getPath().value());

        String body;
        try {
            body = objectMapper.writeValueAsString(errorResponse);
        } catch (JsonProcessingException e) {
            body = "{\"code\":" + status.value() + ",\"message\":\"内部错误\"}";
        }

        byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
        exchange.getResponse().setStatusCode(status);
        exchange.getResponse().getHeaders().setContentType(MediaType.APPLICATION_JSON);
        return exchange.getResponse().writeWith(
                Mono.just(exchange.getResponse().bufferFactory().wrap(bytes))
        );
    }

    private boolean isConnectionError(Throwable ex) {
        String msg = ex.getMessage();
        if (msg == null) return false;
        return msg.contains("Connection refused") ||
               msg.contains("Connection reset") ||
               msg.contains("Unable to connect") ||
               ex instanceof java.net.ConnectException ||
               ex instanceof java.io.IOException;
    }

    private boolean isTimeoutError(Throwable ex) {
        String msg = ex.getMessage();
        if (msg == null) return false;
        return msg.contains("timeout") || msg.contains("Timeout") || msg.contains("timed out");
    }
}
