package com.sunyaxin.common.utils;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Function;

/**
 * JWT工具类
 * 提供JWT令牌的生成、验证和解析功能
 *
 * [DEF-001 FIX] 兼容JJWT 0.12.x API变更：
 * - parserBuilder() -> parser()
 * - setSigningKey() -> verifyWith()
 * - setClaims/subject/issuedAt/expiration -> 链式调用
 */
@Component
public class JwtUtil {

    private static final Logger log = LoggerFactory.getLogger(JwtUtil.class);

    @Value("${jwt.secret:LabManagementSystemSecretKey2024!@#$%ForJWTTokenGeneration}")
    private String secret;

    @Value("${jwt.expiration:86400000}")
    private long expiration;  // 默认24小时（毫秒）

    @Value("${jwt.header:Authorization}")
    private String header;

    @Value("${jwt.prefix:Bearer }")
    private String prefix;

    /**
     * 生成密钥（基于配置的secret）
     */
    private SecretKey getSigningKey() {
        byte[] keyBytes = secret.getBytes(StandardCharsets.UTF_8);
        return Keys.hmacShaKeyFor(keyBytes);
    }

    /**
     * 从令牌中获取用户名
     */
    public String getUsernameFromToken(String token) {
        return getClaimFromToken(token, Claims::getSubject);
    }

    /**
     * 从令牌中获取过期时间
     */
    public Date getExpirationDateFromToken(String token) {
        return getClaimFromToken(token, Claims::getExpiration);
    }

    /**
     * 从令牌中获取特定声明
     */
    public <T> T getClaimFromToken(String token, Function<Claims, T> claimsResolver) {
        final Claims claims = getAllClaimsFromToken(token);
        return claimsResolver.apply(claims);
    }

    /**
     * 解析令牌获取所有声明
     * [FIX] 使用JJWT 0.12.x新API：parser().verifyWith()
     */
    private Claims getAllClaimsFromToken(String token) {
        try {
            return Jwts.parser()
                    .verifyWith(getSigningKey())
                    .build()
                    .parseSignedClaims(token)
                    .getPayload();
        } catch (Exception e) {
            log.warn("解析JWT令牌失败: {}", e.getMessage());
            throw new IllegalArgumentException("无效的JWT令牌");
        }
    }

    /**
     * 检查令牌是否过期
     */
    private Boolean isTokenExpired(String token) {
        final Date expiration = getExpirationDateFromToken(token);
        return expiration.before(new Date());
    }

    /**
     * 为用户生成JWT令牌
     */
    public String generateToken(String username, Long userId, String role) {
        Map<String, Object> claims = new HashMap<>();
        claims.put("userId", userId);
        claims.put("role", role);
        claims.put("created", new Date());

        return doGenerateToken(claims, username);
    }

    /**
     * 生成令牌的核心方法
     * [FIX] 使用JJWT 0.12.x新API链式调用
     */
    private String doGenerateToken(Map<String, Object> claims, String subject) {
        return Jwts.builder()
                .claims(claims)
                .subject(subject)
                .issuedAt(new Date())
                .expiration(new Date(System.currentTimeMillis() + expiration))
                .signWith(getSigningKey())
                .compact();
    }

    /**
     * 验证令牌是否有效
     */
    public Boolean validateToken(String token, String username) {
        try {
            final String tokenUsername = getUsernameFromToken(token);
            return (tokenUsername.equals(username) && !isTokenExpired(token));
        } catch (Exception e) {
            log.warn("验证JWT令牌失败: {}", e.getMessage());
            return false;
        }
    }

    /**
     * 验证令牌是否有效（不检查用户名）
     */
    public Boolean validateToken(String token) {
        try {
            return !isTokenExpired(token);
        } catch (Exception e) {
            log.warn("验证JWT令牌失败: {}", e.getMessage());
            return false;
        }
    }

    /**
     * 从请求头中提取令牌
     */
    public String extractTokenFromHeader(String authHeader) {
        if (authHeader != null && authHeader.startsWith(prefix)) {
            return authHeader.substring(prefix.length());
        }
        return null;
    }

    /**
     * 获取令牌中的用户ID
     */
    public Long getUserIdFromToken(String token) {
        Claims claims = getAllClaimsFromToken(token);
        return claims.get("userId", Long.class);
    }

    /**
     * 获取令牌中的用户角色
     */
    public String getRoleFromToken(String token) {
        Claims claims = getAllClaimsFromToken(token);
        return claims.get("role", String.class);
    }

    /**
     * 刷新令牌（延长有效期）
     */
    public String refreshToken(String oldToken) {
        try {
            final Claims claims = getAllClaimsFromToken(oldToken);
            String username = claims.getSubject();
            Long userId = claims.get("userId", Long.class);
            String role = claims.get("role", String.class);

            // 生成新令牌
            return generateToken(username, userId, role);
        } catch (Exception e) {
            log.error("刷新令牌失败", e);
            throw new IllegalArgumentException("无法刷新令牌");
        }
    }

    // Getter方法
    public String getHeader() {
        return header;
    }

    public String getPrefix() {
        return prefix;
    }
}
