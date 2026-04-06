package com.sunyaxin.gateway.filter;

import com.sunyaxin.common.utils.JwtUtil;
import com.sunyaxin.common.utils.SensitiveDataUtil;
import lombok.extern.slf4j.Slf4j;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.http.server.reactive.ServerHttpResponse;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

import java.nio.charset.StandardCharsets;
import java.util.List;

/**
 * 全局JWT认证过滤器（Iter2安全加固）
 *
 * 功能说明：
 * 1. 拦截所有经过Gateway的请求
 * 2. 白名单路径无需Token即可访问（登录、注册等）
 * 3. 其他路径必须携带有效的Bearer Token
 * 4. 无效或缺失Token返回401 Unauthorized
 * 5. 有效Token会将用户信息传递到下游服务
 *
 * 安全特性：
 * - Token从Authorization头提取，格式：Bearer <token>
 * - 使用与User Service相同的JwtUtil进行验证
 * - 支持通配符白名单路径匹配
 * - 记录详细的认证日志用于审计
 */
@Slf4j
@Component
public class JwtAuthGlobalFilter implements GlobalFilter, Ordered {

    private final JwtUtil jwtUtil;

    /**
     * 白名单路径（无需Token即可访问）
     * 包含：认证接口、健康检查、API文档等公开端点
     */
    private static final List<String> WHITE_LIST = List.of(
            "/api/auth/login",           // 用户登录
            "/api/auth/register",        // 用户注册
            "/actuator/**",              // 健康检查和监控端点
            "/swagger-ui/**",            // Swagger UI
            "/v3/api-docs/**"            // OpenAPI文档
    );

    public JwtAuthGlobalFilter(JwtUtil jwtUtil) {
        this.jwtUtil = jwtUtil;
    }

    /**
     * 过滤器核心逻辑
     */
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        ServerHttpRequest request = exchange.getRequest();
        String path = request.getPath().value();

        log.debug("Gateway JWT过滤器处理请求: {} {}", request.getMethod(), path);

        // 1. 检查是否在白名单中
        if (isWhiteListed(path)) {
            log.debug("路径 [{}] 在白名单中，跳过JWT验证", path);
            return chain.filter(exchange);
        }

        // 2. 从请求头提取Token
        String token = extractToken(request);
        if (!StringUtils.hasText(token)) {
            log.warn("请求 [{}] 未携带有效的Authorization头", path);
            return unauthorized(exchange, "Missing authentication token");
        }

        // 3. 验证Token有效性
        try {
            if (!jwtUtil.validateToken(token)) {
                log.warn("请求 [{}] 的Token无效或已过期, token: {}", path, SensitiveDataUtil.desensitizeToken(token));
                return unauthorized(exchange, "Invalid or expired token");
            }

            // 4. 提取用户信息并传递到下游服务
            String username = jwtUtil.getUsernameFromToken(token);
            Long userId = jwtUtil.getUserIdFromToken(token);
            String role = jwtUtil.getRoleFromToken(token);

            log.info("JWT验证成功 - 用户: {}, ID: {}, 角色: {}", username, userId, role);

            // 将用户信息添加到请求头，传递给下游微服务
            ServerHttpRequest mutatedRequest = request.mutate()
                    .header("X-User-Id", userId != null ? userId.toString() : "")
                    .header("X-User-Name", username != null ? username : "")
                    .header("X-User-Role", role != null ? role : "")
                    .build();

            // 使用修改后的请求继续过滤链
            return chain.filter(exchange.mutate().request(mutatedRequest).build());

        } catch (Exception e) {
            log.error("JWT验证过程中发生异常: {}", e.getMessage(), e);
            return unauthorized(exchange, "Token validation failed: " + e.getMessage());
        }
    }

    /**
     * 从请求头提取JWT Token
     * 支持格式：Authorization: Bearer <token>
     */
    private String extractToken(ServerHttpRequest request) {
        String authHeader = request.getHeaders().getFirst(HttpHeaders.AUTHORIZATION);

        if (StringUtils.hasText(authHeader) && authHeader.startsWith(jwtUtil.getPrefix())) {
            return authHeader.substring(jwtUtil.getPrefix().length()).trim();
        }

        return null;
    }

    /**
     * 检查路径是否在白名单中
     * 支持通配符匹配（如 /actuator/**）
     */
    private boolean isWhiteListed(String path) {
        return WHITE_LIST.stream().anyMatch(whitePath -> {
            if (whitePath.endsWith("/**")) {
                // 通配符匹配：去掉 /** 后检查前缀
                String prefix = whitePath.substring(0, whitePath.length() - 3);
                return path.startsWith(prefix);
            } else {
                // 精确匹配或前缀匹配
                return path.equals(whitePath) || path.startsWith(whitePath + "/");
            }
        });
    }

    /**
     * 返回401未授权响应
     * 返回JSON格式的错误信息，便于前端统一处理
     */
    private Mono<Void> unauthorized(ServerWebExchange exchange, String message) {
        ServerHttpResponse response = exchange.getResponse();
        response.setStatusCode(HttpStatus.UNAUTHORIZED);
        response.getHeaders().setContentType(MediaType.APPLICATION_JSON);

        String body = String.format(
                "{\"code\":401,\"message\":\"%s\",\"timestamp\":\"%s\"}",
                message,
                java.time.Instant.now().toString()
        );

        byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
        org.springframework.core.io.buffer.DataBuffer buffer = response.bufferFactory().wrap(bytes);
        return response.writeWith(Mono.just(buffer));
    }

    /**
     * 设置过滤器优先级
     * 值越小优先级越高，确保在路由之前执行认证
     */
    @Override
    public int getOrder() {
        // 设置较高的优先级，确保在路由转发之前执行
        return -100;
    }
}
