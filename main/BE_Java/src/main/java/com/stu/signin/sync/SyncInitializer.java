package com.stu.signin.sync;

import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.stereotype.Component;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * 启动时的跨站同步初始化，对应 Python main.py 末尾的初始化段。
 *
 * 1. 幂等建 4 张同步表
 * 2. 退役指向快照式对端的历史待发行
 * 3. 启动按需触发的后台同步线程
 *
 * 同步属于增强能力，初始化失败只告警，不影响本站正常签到。
 */
@Component
public class SyncInitializer implements ApplicationRunner {

    private static final Logger log = LoggerFactory.getLogger(SyncInitializer.class);

    private final SyncStore store;
    private final SyncWorker worker;

    public SyncInitializer(SyncStore store, SyncWorker worker) {
        this.store = store;
        this.worker = worker;
    }

    @Override
    public void run(ApplicationArguments args) {
        try {
            store.ensureSyncTables();
            log.info("跨站同步表已就绪");

            int retired = store.retireOutboxForSnapshotPeers();
            if (retired > 0) {
                log.info("跨站同步已退役 {} 条指向快照式对端的待发行", retired);
            }
        } catch (Exception e) {
            log.error("跨站同步建表失败，跨站同步将不可用", e);
        }

        try {
            worker.start();
        } catch (Exception e) {
            log.error("跨站同步后台线程启动失败，跨站同步将不可用", e);
        }
    }
}
