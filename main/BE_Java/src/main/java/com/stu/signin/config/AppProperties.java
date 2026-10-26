package com.stu.signin.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "app")
public record AppProperties(Jwt jwt, Backup backup) {

    public record Jwt(String secret, long expiresSeconds) {
    }

    public record Backup(String dir, long idleSeconds, long pollSeconds) {
    }
}
