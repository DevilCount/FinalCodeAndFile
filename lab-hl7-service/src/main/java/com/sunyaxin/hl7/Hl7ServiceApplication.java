package com.sunyaxin.hl7;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;
import org.springframework.cloud.openfeign.EnableFeignClients;

/**
 * HL7服务启动类
 */
@SpringBootApplication
@EnableDiscoveryClient
@EnableFeignClients
public class Hl7ServiceApplication {

    public static void main(String[] args) {
        SpringApplication.run(Hl7ServiceApplication.class, args);
        System.out.println("=== HL7接口服务启动成功，端口：8084 ===");
    }
}
