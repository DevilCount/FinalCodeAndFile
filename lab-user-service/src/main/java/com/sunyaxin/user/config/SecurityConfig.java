package com.sunyaxin.user.config;

import com.sunyaxin.user.security.JwtAuthenticationFilter;
import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import java.util.Arrays;
import java.util.List;

/**
 * Spring Security配置类
 * 配置JWT认证、CORS、CSRF等安全策略
 */
@Configuration
@EnableWebSecurity
@EnableMethodSecurity  // 启用方法级别的安全控制（@PreAuthorize等）
@RequiredArgsConstructor
public class SecurityConfig {

    private final JwtAuthenticationFilter jwtAuthenticationFilter;

    /**
     * 密码编码器（BCrypt）
     */
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    /**
     * 认证管理器
     */
    @Bean
    public AuthenticationManager authenticationManager(AuthenticationConfiguration authConfig) throws Exception {
        return authConfig.getAuthenticationManager();
    }

    /**
     * 安全过滤器链配置
     */
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            // ========== CSRF配置 ==========
            // 禁用CSRF（因为使用JWT令牌，不需要Session）
            .csrf(csrf -> csrf.disable())

            // ========== CORS配置 ==========
            // 注意：CORS已由Gateway统一处理，此处禁用避免重复头
            .cors(cors -> cors.disable())

            // ========== Session管理 ==========
            // 使用无状态Session（JWT模式）
            .sessionManagement(session -> 
                session.sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            )

            // ========== 请求授权规则 ==========
            .authorizeHttpRequests(auth -> auth
                // 公开接口（无需认证）- 包含多种路径格式以增强兼容性
                .requestMatchers(
                    "/user/login",           // 登录（直接访问）
                    "/user/register",        // 注册（直接访问）
                    "/user/list",            // [Iter2 FIX] 用户列表（TC007需要，只读接口）
                    "/user/all",             // [Iter2 FIX] 所有用户（只读接口）
                    "/api/auth/login",       // 登录（通过API网关兼容路径）
                    "/api/auth/register",    // 注册（通过API网关兼容路径）
                    "/actuator/**",          // 健康检查端点
                    "/swagger-ui/**",        // Swagger UI
                    "/v3/api-docs/**",       // API文档
                    "/swagger-ui.html",      // Swagger首页
                    "/error"                 // 错误页面
                ).permitAll()

                // 静态资源
                .requestMatchers(
                    "/css/**",
                    "/js/**",
                    "/images/**",
                    "/webjars/**"
                ).permitAll()

                // 其他所有请求需要认证
                .anyRequest().authenticated()
            )

            // ========== 添加JWT过滤器 ==========
            // 在UsernamePasswordAuthenticationFilter之前添加JWT过滤器
            .addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class)

            // ========== 异常处理 ==========
            // 使用默认的异常处理（由GlobalExceptionHandler统一处理）

        ;

        return http.build();
    }

    /**
     * CORS配置源
     * 限制允许的跨域来源，避免使用通配符*
     */
    private CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        
        // 允许的域名（生产环境应限制为具体的前端域名）
        configuration.setAllowedOrigins(List.of(
            "http://localhost:5173",      // Vite开发服务器
            "http://localhost:3000",      // React开发服务器
            "http://localhost:8080",      // Gateway
            "http://127.0.0.1:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8080"
        ));
        
        // 允许的HTTP方法
        configuration.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"));
        
        // 允许的请求头
        configuration.setAllowedHeaders(Arrays.asList(
            "*",
            "Authorization",
            "Content-Type",
            "X-Requested-With",
            "Accept",
            "Origin"
        ));
        
        // 允许携带凭证（Cookie等）
        configuration.setAllowCredentials(true);
        
        // 预检请求缓存时间（秒）
        configuration.setMaxAge(3600L);
        
        // 暴露给前端的响应头
        configuration.setExposedHeaders(List.of("Authorization", "X-Total-Count"));

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);

        return source;
    }
}
