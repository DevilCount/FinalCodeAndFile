package com.sunyaxin.user.security;

import com.sunyaxin.common.utils.JwtUtil;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.lang.NonNull;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.Collections;
import java.util.List;

/**
 * JWT认证过滤器
 * 拦截HTTP请求，从请求头中提取并验证JWT令牌
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private final JwtUtil jwtUtil;

    // 不需要认证的路径（白名单）- 与SecurityConfig保持一致
    private static final List<String> EXCLUDED_PATHS = List.of(
        "/user/login",
        "/user/register",
        "/user/list",            // [FIX] 用户列表（TC007需要，只读接口）
        "/user/all",             // [FIX] 所有用户（只读接口）
        "/api/auth/login",
        "/api/auth/register",
        "/actuator",
        "/swagger-ui",
        "/v3/api-docs"
    );

    @Override
    protected void doFilterInternal(@NonNull HttpServletRequest request,
                                    @NonNull HttpServletResponse response,
                                    @NonNull FilterChain filterChain) throws ServletException, IOException {
        
        try {
            String requestPath = request.getRequestURI();
            
            // 1. 检查是否在白名单路径中
            if (isExcludedPath(requestPath)) {
                log.debug("路径 {} 在白名单中，跳过JWT验证", requestPath);
                filterChain.doFilter(request, response);
                return;
            }

            // 2. 从请求头提取令牌
            String token = extractToken(request);
            
            if (token == null) {
                log.warn("请求 {} 未携带有效的Authorization头", requestPath);
                filterChain.doFilter(request, response);
                return;
            }

            // 3. 验证令牌
            if (jwtUtil.validateToken(token)) {
                // 4. 提取用户信息
                String username = jwtUtil.getUsernameFromToken(token);
                Long userId = jwtUtil.getUserIdFromToken(token);
                String role = jwtUtil.getRoleFromToken(token);

                log.debug("JWT验证成功 - 用户: {}, ID: {}, 角色: {}", username, userId, role);

                // 5. 创建认证对象并设置到SecurityContext
                UsernamePasswordAuthenticationToken authentication = 
                    new UsernamePasswordAuthenticationToken(
                        username,
                        null,
                        Collections.singletonList(new SimpleGrantedAuthority("ROLE_" + (role != null ? role : "USER")))
                    );

                authentication.setDetails(userId);  // 将userId存储在details中

                SecurityContextHolder.getContext().setAuthentication(authentication);

            } else {
                log.warn("JWT令牌无效或已过期");
            }

        } catch (Exception e) {
            log.error("JWT认证过程中发生异常", e);
            SecurityContextHolder.clearContext();
        }

        filterChain.doFilter(request, response);
    }

    /**
     * 从请求头提取JWT令牌
     */
    private String extractToken(HttpServletRequest request) {
        String header = request.getHeader(jwtUtil.getHeader());
        
        if (StringUtils.hasText(header) && header.startsWith(jwtUtil.getPrefix())) {
            return header.substring(jwtUtil.getPrefix().length()).trim();
        }
        
        return null;
    }

    /**
     * 检查路径是否在白名单中
     */
    private boolean isExcludedPath(String path) {
        return EXCLUDED_PATHS.stream().anyMatch(path::startsWith);
    }
}
