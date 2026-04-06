package com.sunyaxin.sample;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;

/**
 * 应用启动测试
 * 验证Spring上下文加载是否正常
 */
@SpringBootTest
@ActiveProfiles("test")
class SampleServiceApplicationTests {

    @Test
    void contextLoads() {
        // 如果Spring上下文能正常加载，测试通过
        System.out.println("Spring上下文加载成功");
    }

    @Test
    void testApplicationStartup() {
        // 测试应用启动
        System.out.println("应用启动测试通过");
    }
}
