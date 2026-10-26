package com.stu.signin.config;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Spring Boot 4 使用 Jackson 3 处理 HTTP 报文，
 * 这里单独提供一个 Jackson 2 的 ObjectMapper 给日志/令牌等工具类复用。
 */
@Configuration
public class JacksonConfig {

    @Bean
    public ObjectMapper objectMapper() {
        return new ObjectMapper();
    }
}
