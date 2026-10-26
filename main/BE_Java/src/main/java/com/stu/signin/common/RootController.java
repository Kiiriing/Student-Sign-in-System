package com.stu.signin.common;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Map;

@RestController
public class RootController {

    private final JdbcTemplate jdbcTemplate;

    public RootController(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    @GetMapping("/")
    public Map<String, Object> index() {
        return Api.body(
                "code", 200,
                "message", "学生签到系统后端运行正常",
                "service", "student-signin-backend"
        );
    }

    /**
     * 测试 MySQL 是否能够正常连接
     */
    @GetMapping("/api/test/mysql")
    public Map<String, Object> testMysql() {
        try {
            List<Map<String, Object>> rows = jdbcTemplate.queryForList("SELECT NOW() AS now_time");
            Object now = rows.isEmpty() ? null : rows.get(0).get("now_time");

            // Flask 的 jsonify 会把 datetime 序列化成 HTTP 日期格式，这里保持一致
            String formatted = now instanceof java.time.LocalDateTime local
                    ? DateTimeFormatter.RFC_1123_DATE_TIME.format(local.atOffset(ZoneOffset.UTC))
                    : String.valueOf(now);

            return Api.body(
                    "code", 200,
                    "message", "MySQL 连接成功",
                    "data", Map.of("now_time", formatted)
            );
        } catch (Exception e) {
            throw new ApiException(500, "MySQL 连接失败", String.valueOf(e.getMessage()));
        }
    }
}
