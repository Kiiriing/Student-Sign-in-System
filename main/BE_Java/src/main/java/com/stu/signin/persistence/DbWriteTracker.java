package com.stu.signin.persistence;

import org.springframework.stereotype.Component;

import java.util.concurrent.atomic.AtomicLong;

/**
 * 记录「最后一次真正改动数据」的时间，供空闲自动备份判断是否需要导出。
 *
 * 对应 Python core/database.py 的 mark_db_write / get_last_write_at：
 * 只认影响行数大于 0 的 INSERT / UPDATE / DELETE / REPLACE。
 */
@Component
public class DbWriteTracker {

    private final AtomicLong lastWriteAt = new AtomicLong(0L);

    public void mark() {
        lastWriteAt.set(System.currentTimeMillis());
    }

    /** 本进程内还没有改动过数据时返回 null */
    public Long lastWriteAt() {
        long value = lastWriteAt.get();
        return value == 0L ? null : value;
    }
}
