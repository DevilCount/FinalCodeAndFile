package com.sunyaxin.user;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.FilterType;

/**
 * 用户服务启动类
 *
 * [DEF-001 FIX] 添加@ComponentScan扫描common.utils包（仅导入JwtUtil），
 * 排除common.config避免RedisConfig等Bean名称冲突
 */
@SpringBootApplication
@EnableDiscoveryClient
@MapperScan("com.sunyaxin.user.mapper")
@ComponentScan(basePackages = {
    "com.sunyaxin.user",
    "com.sunyaxin.common.utils"  // 只扫描utils包获取JwtUtil
})
public class UserServiceApplication {

    public static void main(String[] args) {
        SpringApplication.run(UserServiceApplication.class, args);
        System.out.println("=== 用户服务启动成功，端口：8081 ===");
    }
}