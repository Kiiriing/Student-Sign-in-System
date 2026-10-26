package com.stu.signin.persistence;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

import java.util.Locale;

/**
 * 写操作统一入口：执行 DML 后按影响行数打「数据改动」时间戳。
 *
 * 读操作仍可直接使用 JdbcTemplate；所有写操作走这里，
 * 避免每个业务点各自判断是否要通知自动备份。
 */
@Component
public class DbWriter {

    private final JdbcTemplate jdbcTemplate;
    private final DbWriteTracker tracker;

    public DbWriter(JdbcTemplate jdbcTemplate, DbWriteTracker tracker) {
        this.jdbcTemplate = jdbcTemplate;
        this.tracker = tracker;
    }

    public int update(String sql, Object... args) {
        int affected = jdbcTemplate.update(sql, args);
        if (affected > 0 && isDml(sql)) {
            tracker.mark();
        }
        return affected;
    }

    private static boolean isDml(String sql) {
        String text = sql.stripLeading().toLowerCase(Locale.ROOT);
        return text.startsWith("insert") || text.startsWith("update")
                || text.startsWith("delete") || text.startsWith("replace");
    }
}
