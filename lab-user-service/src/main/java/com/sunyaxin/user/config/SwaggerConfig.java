package com.sunyaxin.user.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Swagger/OpenAPI 配置
 */
@Configuration
public class SwaggerConfig {

    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("实验室管理系统 API")
                        .version("1.0.0")
                        .description("实验室管理系统接口文档，包含用户管理、标本管理、报告管理等功能")
                        .contact(new Contact()
                                .name("孙亚鑫")
                                .email("sunyaxin@example.com")
                                .url("https://github.com/sunyaxin"))
                        .license(new License()
                                .name("Apache 2.0")
                                .url("https://www.apache.org/licenses/LICENSE-2.0")));
    }
}
