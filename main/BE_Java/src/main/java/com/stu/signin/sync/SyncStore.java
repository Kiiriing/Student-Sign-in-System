package com.stu.signin.sync;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.stu.signin.common.DbValues;
import com.stu.signin.persistence.DbWriter;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import java.sql.Timestamp;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/**
 * 跨站同步数据访问层，对应 Python sync/store.py。
 *
 * 负责 4 张同步表（cross_site_record / sync_cursor / sync_outbox /
 * cross_site_conflict）的建表与读写；本地考勤表只读不写。
 */
@Repository
public class SyncStore {

    public static final int RESOLVE_PENDING = 0;
    public static final int RESOLVE_VALID = 1;
    public static final int RESOLVE_VOID = 2;

    public static final int OUTBOX_PENDING = 0;
    public static final int OUTBOX_SENT = 1;
    public static final int OUTBOX_FAILED = 2;

    public static final int CONFLICT_PENDING = 0;
    public static final int CONFLICT_RESOLVED = 1;
    public static final int CONFLICT_IGNORED = 2;

    // 前置空格：多处与文本块拼接，文本块行尾空格会被 Java 自动去掉
    private static final String VALID_CROSS_CONDITION = " resolve_state = 1 AND is_duplicate = 0";

    private static final List<String> CREATE_STATEMENTS = List.of(
            """
            CREATE TABLE IF NOT EXISTS `cross_site_record` (
              `id` char(36) NOT NULL COMMENT '本站记录ID',
              `origin_site` varchar(32) NOT NULL COMMENT '来源站点标识',
              `origin_record_id` varchar(64) NOT NULL COMMENT '来源站点的签到记录ID',
              `origin_task_id` varchar(64) DEFAULT NULL COMMENT '来源站点的签到任务ID',
              `student_no` varchar(32) NOT NULL COMMENT '学号',
              `student_name` varchar(50) DEFAULT NULL COMMENT '学生姓名',
              `class_name` varchar(50) DEFAULT NULL COMMENT '班级名',
              `course_name` varchar(100) DEFAULT NULL COMMENT '课程名',
              `course_date` date DEFAULT NULL COMMENT '课程日期',
              `period` varchar(20) DEFAULT NULL COMMENT '时段档 morning/afternoon（对齐键组成部分）',
              `time_slot` varchar(50) DEFAULT NULL COMMENT '时间段（精确时分，可能为空）',
              `align_key` varchar(255) DEFAULT NULL COMMENT '归一化对齐键 学号|班级键|日期|时段档',
              `attendance_status` tinyint DEFAULT NULL COMMENT '签到状态 1正常 2迟到 3旷课 4早退 5病假 6事假',
              `sign_time` datetime DEFAULT NULL COMMENT '异地签到时间',
              `device_id` varchar(255) DEFAULT NULL COMMENT '签到设备ID',
              `ip` varchar(45) DEFAULT NULL COMMENT '签到IP',
              `location` varchar(255) DEFAULT NULL COMMENT '签到位置',
              `is_script` tinyint NOT NULL DEFAULT 0 COMMENT '是否脚本签到',
              `task_start_time` datetime DEFAULT NULL COMMENT '来源站点任务开始时间',
              `task_end_time` datetime DEFAULT NULL COMMENT '来源站点任务结束时间',
              `raw_json` json DEFAULT NULL COMMENT '原始事件留档',
              `resolve_state` tinyint NOT NULL DEFAULT 1 COMMENT '0待裁决 1有效 2作废',
              `is_duplicate` tinyint NOT NULL DEFAULT 0 COMMENT '是否被判为重复',
              `duplicate_of` char(36) DEFAULT NULL COMMENT '重复指向的有效记录ID',
              `ingest_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '入库时间',
              PRIMARY KEY (`id`),
              UNIQUE KEY `uk_cross_origin` (`origin_site`, `origin_record_id`),
              KEY `idx_cross_align` (`student_no`, `class_name`, `course_name`, `course_date`, `time_slot`),
              KEY `idx_cross_sign_time` (`sign_time`),
              KEY `idx_cross_state` (`resolve_state`)
            ) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '跨站签到同步表'
            """,
            """
            CREATE TABLE IF NOT EXISTS `sync_cursor` (
              `peer_code` varchar(32) NOT NULL COMMENT '对端站点标识',
              `last_seq` bigint NOT NULL DEFAULT 0 COMMENT '已拉取到的对端 outbox 序号',
              `last_pull_at` datetime DEFAULT NULL COMMENT '最近一次拉取时间',
              `last_success_at` datetime DEFAULT NULL COMMENT '最近一次拉取成功时间',
              `fail_count` int NOT NULL DEFAULT 0 COMMENT '连续失败次数',
              `last_error` varchar(500) DEFAULT NULL COMMENT '最近一次错误',
              `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
              PRIMARY KEY (`peer_code`)
            ) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '跨站同步游标表'
            """,
            """
            CREATE TABLE IF NOT EXISTS `sync_outbox` (
              `id` bigint NOT NULL AUTO_INCREMENT COMMENT '队列序号（同时作为 pull 游标）',
              `target_peer` varchar(32) NOT NULL COMMENT '目标站点标识',
              `event_id` char(36) NOT NULL COMMENT '事件ID',
              `event_type` varchar(32) NOT NULL COMMENT '事件类型',
              `payload` json NOT NULL COMMENT '完整事件信封',
              `status` tinyint NOT NULL DEFAULT 0 COMMENT '0待发 1已发 2失败',
              `retry_count` int NOT NULL DEFAULT 0 COMMENT '已重试次数',
              `next_retry_at` datetime DEFAULT NULL COMMENT '下次重试时间',
              `last_error` varchar(500) DEFAULT NULL COMMENT '最近一次错误',
              `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '入队时间',
              `sent_at` datetime DEFAULT NULL COMMENT '发送成功时间',
              PRIMARY KEY (`id`),
              UNIQUE KEY `uk_outbox_event` (`target_peer`, `event_id`),
              KEY `idx_outbox_pending` (`status`, `next_retry_at`)
            ) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '跨站同步发送队列表'
            """,
            """
            CREATE TABLE IF NOT EXISTS `cross_site_conflict` (
              `id` char(36) NOT NULL COMMENT '冲突ID',
              `align_key` varchar(255) NOT NULL COMMENT '归一化对齐键',
              `winner_record_id` varchar(64) DEFAULT NULL COMMENT '胜出记录ID',
              `winner_site` varchar(32) DEFAULT NULL COMMENT '胜出记录来源站点',
              `loser_json` json DEFAULT NULL COMMENT '落败记录（本站记录不会被改动，只在此登记）',
              `state` tinyint NOT NULL DEFAULT 0 COMMENT '0待处理 1已裁决 2忽略',
              `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
              `handled_by` char(36) DEFAULT NULL COMMENT '处理人用户ID',
              `handled_at` datetime DEFAULT NULL COMMENT '处理时间',
              PRIMARY KEY (`id`),
              KEY `idx_conflict_align` (`align_key`),
              KEY `idx_conflict_state` (`state`)
            ) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '跨站签到冲突登记表'
            """
    );

    private static final String INGEST_SQL = """
            INSERT IGNORE INTO `cross_site_record`
            (
                id, origin_site, origin_record_id, origin_task_id, student_no,
                student_name, class_name, course_name, course_date, period,
                time_slot, align_key, attendance_status, sign_time, device_id,
                ip, location, is_script, task_start_time, task_end_time,
                raw_json, resolve_state
            )
            VALUES
            (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """;

    private static final String ECHO_CHECK_SQL = """
            SELECT ar.id
            FROM attendance_record ar
            JOIN `students` s ON s.id = ar.student_id
            WHERE s.student_no = ?
              AND ar.sign_time = ?
            LIMIT 1
            """;

    public record CrossSign(String originSite, LocalDateTime signTime, String studentNo,
                            Integer attendanceStatus) {
    }

    public record OutboundBatch(List<Map<String, Object>> events, long nextCursor) {
    }

    public record IngestResult(List<Map<String, Object>> accepted,
                               List<Map<String, Object>> duplicated,
                               List<Map<String, Object>> rejected) {
        public Map<String, Object> toMap() {
            Map<String, Object> map = new LinkedHashMap<>();
            map.put("accepted", accepted);
            map.put("duplicated", duplicated);
            map.put("rejected", rejected);
            return map;
        }
    }

    public record TaskContext(String taskId, String classId, LocalDateTime courseDate, String period) {
    }

    public record TaskStat(int signedCount, int[] counts) {
        public int count(int status) {
            return status >= 1 && status <= 6 ? counts[status] : 0;
        }
    }

    private final JdbcTemplate jdbc;
    private final DbWriter writer;
    private final ObjectMapper mapper;
    private final SyncConfig config;

    public SyncStore(JdbcTemplate jdbc, DbWriter writer, ObjectMapper mapper, SyncConfig config) {
        this.jdbc = jdbc;
        this.writer = writer;
        this.mapper = mapper;
        this.config = config;
    }

    // ============================================================
    // 建表
    // ============================================================

    public void ensureSyncTables() {
        for (String statement : CREATE_STATEMENTS) {
            jdbc.execute(statement);
        }

        if (!columnExists("cross_site_record", "period")) {
            jdbc.execute("ALTER TABLE `cross_site_record` ADD COLUMN "
                    + "`period` varchar(20) DEFAULT NULL COMMENT '时段档 morning/afternoon（对齐键组成部分）' "
                    + "AFTER `course_date`");
        }
    }

    private boolean columnExists(String table, String column) {
        Integer total = jdbc.queryForObject("""
                SELECT COUNT(*) AS total
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = ?
                  AND COLUMN_NAME = ?
                """, Integer.class, table, column);
        return total != null && total > 0;
    }

    // ============================================================
    // 入站
    // ============================================================

    private record LocalCourse(String className, String courseName) {
    }

    private LocalCourse resolveLocalCourse(String className, Object courseDate, String period) {
        String dateText = SyncContract.normalizeDate(courseDate);
        String periodKey = SyncContract.normalizePeriod(period);
        String classKey = SyncContract.normalizeClassKey(className);

        if (dateText.isEmpty() || periodKey.isEmpty() || classKey.isEmpty()) {
            return null;
        }

        List<Map<String, Object>> rows = jdbc.queryForList("""
                SELECT cl.name AS class_name, c.name AS course_name, c.time AS course_time
                FROM courses c
                LEFT JOIN classes cl ON cl.id = c.class_id
                WHERE c.course_date = ?
                ORDER BY c.time ASC
                """, dateText);

        for (Map<String, Object> row : rows) {
            if (!SyncContract.normalizeClassKey(row.get("class_name")).equals(classKey)) {
                continue;
            }
            if (!SyncContract.normalizePeriod(row.get("course_time")).equals(periodKey)) {
                continue;
            }
            return new LocalCourse(
                    DbValues.text(row.get("class_name")),
                    DbValues.text(row.get("course_name")));
        }
        return null;
    }

    @SuppressWarnings("unchecked")
    public IngestResult ingestEvents(List<Map<String, Object>> events) {
        List<Map<String, Object>> accepted = new ArrayList<>();
        List<Map<String, Object>> duplicated = new ArrayList<>();
        List<Map<String, Object>> rejected = new ArrayList<>();

        if (events == null || events.isEmpty()) {
            return new IngestResult(accepted, duplicated, rejected);
        }

        for (Map<String, Object> event : events) {
            SyncContract.ValidationResult validation = SyncContract.validateEvent(event);
            if (!validation.valid()) {
                rejected.add(rejectedItem(event, validation.reason()));
                continue;
            }

            String originSite = SyncContract.normalizeText(event.get("origin_site"));
            if (originSite.equals(config.siteCode())) {
                rejected.add(rejectedItem(event, "origin_site 与本站相同"));
                continue;
            }

            Map<String, Object> payload = event.get("payload") instanceof Map<?, ?> map
                    ? (Map<String, Object>) map : Map.of();

            String recordId = UUID.randomUUID().toString();
            String studentNo = truncate(SyncContract.normalizeText(payload.get("student_no")), 32);
            LocalDateTime signTime = SyncContract.toDbDateTime(payload.get("sign_time"));

            String echoOf = null;
            if (!studentNo.isEmpty() && signTime != null) {
                List<Map<String, Object>> hits = jdbc.queryForList(ECHO_CHECK_SQL, studentNo,
                        Timestamp.valueOf(signTime));
                if (!hits.isEmpty()) {
                    echoOf = DbValues.text(hits.get(0).get("id"));
                }
            }

            String period = SyncContract.normalizePeriod(payload.get("period"));
            if (period.isEmpty()) {
                period = SyncContract.normalizePeriod(payload.get("time_slot"));
            }

            LocalCourse local = resolveLocalCourse(
                    SyncContract.normalizeText(payload.get("class_name")),
                    payload.get("course_date"), period);

            String className = local != null ? local.className()
                    : SyncContract.normalizeText(payload.get("class_name"));
            String courseName = local != null ? local.courseName()
                    : SyncContract.normalizeText(payload.get("course_name"));

            String originTaskId = SyncContract.normalizeText(event.get("origin_task_id"));
            String rawJson;
            try {
                rawJson = mapper.writeValueAsString(event);
            } catch (Exception e) {
                rawJson = "{}";
            }

            LocalDateTime taskStart = SyncContract.toDbDateTime(payload.get("task_start_time"));
            LocalDateTime taskEnd = SyncContract.toDbDateTime(payload.get("task_end_time"));

            int affected = writer.update(INGEST_SQL,
                    recordId,
                    originSite,
                    truncate(SyncContract.normalizeText(event.get("origin_record_id")), 64),
                    originTaskId.isEmpty() ? null : truncate(originTaskId, 64),
                    studentNo,
                    nullIfEmpty(truncate(SyncContract.normalizeText(payload.get("student_name")), 50)),
                    truncate(className, 50),
                    truncate(courseName, 100),
                    emptyToNull(SyncContract.normalizeDate(payload.get("course_date"))),
                    truncate(period, 20),
                    truncate(SyncContract.normalizeTimeSlot(payload.get("time_slot")), 50),
                    truncate(SyncContract.alignKeyOfPayload(payload), 255),
                    SyncContract.normalizeAttendanceStatus(payload.get("attendance_status")),
                    signTime,
                    nullIfEmpty(truncate(SyncContract.normalizeText(payload.get("device_id")), 255)),
                    nullIfEmpty(truncate(SyncContract.normalizeText(payload.get("ip")), 45)),
                    nullIfEmpty(truncate(SyncContract.normalizeText(payload.get("location")), 255)),
                    toInt(payload.get("is_script")) == 1 ? 1 : 0,
                    taskStart,
                    taskEnd,
                    rawJson,
                    echoOf != null ? RESOLVE_VOID : RESOLVE_VALID);

            if (affected == 1) {
                if (echoOf != null) {
                    writer.update("""
                            UPDATE `cross_site_record`
                            SET `is_duplicate` = 1, `duplicate_of` = ?
                            WHERE `id` = ?
                            """, echoOf, recordId);
                    duplicated.add(Map.of("event_id", event.get("event_id")));
                } else {
                    Map<String, Object> item = new LinkedHashMap<>();
                    item.put("event_id", event.get("event_id"));
                    item.put("record_id", recordId);
                    accepted.add(item);
                }
            } else {
                duplicated.add(Map.of("event_id", event.get("event_id")));
            }
        }

        return new IngestResult(accepted, duplicated, rejected);
    }

    private static Map<String, Object> rejectedItem(Map<String, Object> event, String reason) {
        Map<String, Object> item = new LinkedHashMap<>();
        item.put("event_id", event == null ? null : event.get("event_id"));
        item.put("reason", reason);
        return item;
    }

    // ============================================================
    // 出站
    // ============================================================

    public Map<String, Object> buildLocalSigninEvent(
            String recordId, String taskId, Object studentNo, Object studentName, Object className,
            Object courseDate, String period, Object attendanceStatus, Object signTime,
            Object courseName, Object timeSlot, Object deviceId, Object ip, Object location,
            Object isScript, Object taskStartTime, Object taskEndTime) {

        return SyncContract.buildEvent(
                SyncContract.EVENT_SIGNIN,
                config.siteCode(),
                recordId,
                studentNo, className, courseDate, period, attendanceStatus, signTime,
                courseName, timeSlot, studentName, deviceId, ip, location, isScript,
                taskStartTime, taskEndTime, taskId);
    }

    public int enqueueEventToPeers(Map<String, Object> event) {
        if (config.peers().isEmpty() || event == null) {
            return 0;
        }

        String payloadJson;
        try {
            payloadJson = mapper.writeValueAsString(event);
        } catch (Exception e) {
            throw new IllegalStateException("事件序列化失败", e);
        }

        int queued = 0;
        for (SyncConfig.SyncPeer peer : config.peers()) {
            if (!SyncConfig.PROTOCOL_CONTRACT.equals(config.peerProtocol(peer))) {
                continue;
            }
            queued += writer.update("""
                    INSERT IGNORE INTO `sync_outbox`
                    (`target_peer`, `event_id`, `event_type`, `payload`)
                    VALUES (?, ?, ?, ?)
                    """, peer.code(), event.get("event_id"), event.get("event_type"), payloadJson);
        }
        return queued;
    }

    public int retireOutboxForSnapshotPeers() {
        List<String> codes = config.snapshotPeers().stream().map(SyncConfig.SyncPeer::code).toList();
        if (codes.isEmpty()) {
            return 0;
        }

        String placeholders = String.join(",", java.util.Collections.nCopies(codes.size(), "?"));
        List<Object> args = new ArrayList<>();
        args.add(OUTBOX_FAILED);
        args.add("目标站点已切换为快照式协议");
        args.add(OUTBOX_PENDING);
        args.addAll(codes);

        return writer.update("""
                UPDATE `sync_outbox`
                SET status = ?, last_error = ?, next_retry_at = NULL
                WHERE status = ? AND target_peer IN (%s)
                """.formatted(placeholders), args.toArray());
    }

    public List<Map<String, Object>> pendingOutbox(int limit) {
        return jdbc.queryForList("""
                SELECT id, target_peer, event_id, event_type, payload, retry_count
                FROM `sync_outbox`
                WHERE status = ?
                  AND (next_retry_at IS NULL OR next_retry_at <= NOW())
                ORDER BY id ASC
                LIMIT ?
                """, OUTBOX_PENDING, limit);
    }

    public void markOutboxSent(long outboxId) {
        writer.update("""
                UPDATE `sync_outbox`
                SET status = ?, sent_at = NOW(), last_error = NULL
                WHERE id = ?
                """, OUTBOX_SENT, outboxId);
    }

    public void markOutboxRejected(long outboxId, String error) {
        writer.update("""
                UPDATE `sync_outbox`
                SET status = ?, last_error = ?
                WHERE id = ?
                """, OUTBOX_FAILED, truncate(error == null ? "" : error, 500), outboxId);
    }

    public void markOutboxFailed(long outboxId, int retryCount, String error) {
        int nextCount = retryCount + 1;
        if (nextCount >= SyncConfig.MAX_RETRY) {
            writer.update("""
                    UPDATE `sync_outbox`
                    SET status = ?, retry_count = ?, last_error = ?
                    WHERE id = ?
                    """, OUTBOX_FAILED, nextCount, truncate(error, 500), outboxId);
        } else {
            int delay = Math.min(1 << nextCount, 300);
            writer.update("""
                    UPDATE `sync_outbox`
                    SET status = ?, retry_count = ?, last_error = ?,
                        next_retry_at = DATE_ADD(NOW(), INTERVAL ? SECOND)
                    WHERE id = ?
                    """, OUTBOX_PENDING, nextCount, truncate(error, 500), delay, outboxId);
        }
    }

    public OutboundBatch fetchOutboundBatch(String peerCode, long sinceId, int limit) {
        List<Map<String, Object>> rows = jdbc.queryForList("""
                SELECT id, payload
                FROM `sync_outbox`
                WHERE target_peer = ? AND id > ?
                ORDER BY id ASC
                LIMIT ?
                """, peerCode, sinceId, limit);

        List<Map<String, Object>> events = new ArrayList<>();
        long nextCursor = sinceId;

        for (Map<String, Object> row : rows) {
            Object payload = row.get("payload");
            Map<String, Object> parsed = null;
            if (payload instanceof String text) {
                try {
                    parsed = mapper.readValue(text, Map.class);
                } catch (Exception ignored) {
                    continue;
                }
            } else if (payload instanceof Map<?, ?> map) {
                @SuppressWarnings("unchecked")
                Map<String, Object> cast = (Map<String, Object>) map;
                parsed = cast;
            }
            if (parsed != null) {
                events.add(parsed);
                nextCursor = DbValues.longValue(row.get("id"));
            }
        }

        return new OutboundBatch(events, nextCursor);
    }

    // ============================================================
    // 游标
    // ============================================================

    public long getCursor(String peerCode) {
        List<Map<String, Object>> rows = jdbc.queryForList(
                "SELECT last_seq FROM `sync_cursor` WHERE peer_code = ?", peerCode);
        return rows.isEmpty() ? 0L : DbValues.longValue(rows.get(0).get("last_seq"));
    }

    public void saveCursor(String peerCode, long lastSeq, boolean success, String error) {
        if (success) {
            writer.update("""
                    INSERT INTO `sync_cursor`
                        (peer_code, last_seq, last_pull_at, last_success_at, fail_count, last_error)
                    VALUES (?, ?, NOW(), NOW(), 0, NULL)
                    ON DUPLICATE KEY UPDATE
                        last_seq = VALUES(last_seq),
                        last_pull_at = NOW(),
                        last_success_at = NOW(),
                        fail_count = 0,
                        last_error = NULL
                    """, peerCode, lastSeq);
        } else {
            writer.update("""
                    INSERT INTO `sync_cursor`
                        (peer_code, last_seq, last_pull_at, fail_count, last_error)
                    VALUES (?, ?, NOW(), 1, ?)
                    ON DUPLICATE KEY UPDATE
                        last_pull_at = NOW(),
                        fail_count = fail_count + 1,
                        last_error = VALUES(last_error)
                    """, peerCode, lastSeq, truncate(error, 500));
        }
    }

    public Map<String, Map<String, Object>> cursorSnapshot() {
        Map<String, Map<String, Object>> result = new LinkedHashMap<>();
        for (Map<String, Object> row : jdbc.queryForList("""
                SELECT peer_code, last_seq, last_pull_at, last_success_at, fail_count, last_error
                FROM `sync_cursor`
                """)) {
            result.put(DbValues.text(row.get("peer_code")), row);
        }
        return result;
    }

    // ============================================================
    // 查重
    // ============================================================

    public Map<String, Object> findLocalDuplicate(String studentNo, String alignKey) {
        if (studentNo == null || studentNo.isEmpty() || alignKey == null || alignKey.isEmpty()) {
            return null;
        }

        List<Map<String, Object>> rows = jdbc.queryForList("""
                SELECT
                    ar.id AS record_id,
                    ar.sign_time,
                    ar.status AS attendance_status,
                    s.student_no,
                    s.name AS student_name,
                    cl.name AS class_name,
                    c.name AS course_name,
                    c.course_date,
                    c.time AS time_raw
                FROM attendance_record ar
                JOIN students s ON s.id = ar.student_id
                JOIN attendance_task at ON at.id = ar.task_id
                JOIN courses c ON c.id = at.course_id
                LEFT JOIN classes cl ON cl.id = s.class_id
                WHERE s.student_no = ?
                """, truncate(SyncContract.normalizeText(studentNo), 32));

        Map<String, Object> best = null;
        LocalDateTime bestTime = null;

        for (Map<String, Object> row : rows) {
            String rowKey = SyncContract.buildAlignKey(
                    row.get("student_no"), row.get("class_name"),
                    row.get("course_date"), row.get("time_raw"));
            if (!rowKey.equals(alignKey)) {
                continue;
            }
            LocalDateTime signTime = DbValues.localDateTime(row.get("sign_time"));
            if (best == null || compareNullLast(signTime, bestTime) < 0) {
                best = new LinkedHashMap<>();
                best.put("record_id", row.get("record_id"));
                best.put("sign_time", signTime);
                best.put("attendance_status", row.get("attendance_status"));
                best.put("student_name", row.get("student_name"));
                best.put("course_name", row.get("course_name"));
                bestTime = signTime;
            }
        }
        return best;
    }

    public Map<String, Object> findCrossDuplicate(String studentNo, String alignKey) {
        if (studentNo == null || studentNo.isEmpty() || alignKey == null || alignKey.isEmpty()) {
            return null;
        }
        List<Map<String, Object>> rows = jdbc.queryForList("""
                SELECT
                    origin_site, origin_record_id, course_name, course_date,
                    period, time_slot, attendance_status, sign_time
                FROM `cross_site_record`
                WHERE student_no = ?
                  AND align_key = ?
                  AND resolve_state <> ?
                ORDER BY sign_time ASC
                LIMIT 1
                """, truncate(SyncContract.normalizeText(studentNo), 32),
                truncate(alignKey, 255), RESOLVE_VOID);
        return rows.isEmpty() ? null : rows.get(0);
    }

    public Map<String, CrossSign> crossSignsForStudent(String studentNo, String courseDate) {
        Map<String, CrossSign> result = new LinkedHashMap<>();
        if (studentNo == null || studentNo.isEmpty()) {
            return result;
        }

        String sql = """
                SELECT align_key, origin_site, sign_time
                FROM `cross_site_record`
                WHERE student_no = ?
                """ + (courseDate != null && !courseDate.isEmpty() ? " AND course_date = ?" : "")
                + " AND " + VALID_CROSS_CONDITION;

        List<Object> args = new ArrayList<>();
        args.add(truncate(SyncContract.normalizeText(studentNo), 32));
        if (courseDate != null && !courseDate.isEmpty()) {
            args.add(courseDate);
        }

        for (Map<String, Object> row : jdbc.queryForList(sql, args.toArray())) {
            String key = DbValues.text(row.get("align_key"));
            if (key == null || key.isEmpty()) {
                continue;
            }
            LocalDateTime signTime = DbValues.localDateTime(row.get("sign_time"));
            CrossSign prev = result.get(key);
            if (prev == null || compareNullLast(signTime, prev.signTime()) < 0) {
                result.put(key, new CrossSign(DbValues.text(row.get("origin_site")), signTime, null, null));
            }
        }
        return result;
    }

    public Map<String, CrossSign> crossSignsForCourse(Object courseDate) {
        Map<String, CrossSign> result = new LinkedHashMap<>();
        String dateText = SyncContract.normalizeDate(courseDate);
        if (dateText.isEmpty()) {
            return result;
        }

        for (Map<String, Object> row : jdbc.queryForList("""
                SELECT align_key, student_no, origin_site, sign_time, attendance_status,
                       student_name, class_name, period, course_name, course_date
                FROM `cross_site_record`
                WHERE course_date = ?
                  AND """ + VALID_CROSS_CONDITION, dateText)) {

            String key = DbValues.text(row.get("align_key"));
            if (key == null || key.isEmpty()) {
                key = SyncContract.buildAlignKey(row.get("student_no"), row.get("class_name"),
                        row.get("course_date"), row.get("period"));
            }
            if (key.isEmpty()) {
                continue;
            }

            LocalDateTime signTime = DbValues.localDateTime(row.get("sign_time"));
            CrossSign prev = result.get(key);
            if (prev == null || compareNullLast(signTime, prev.signTime()) < 0) {
                result.put(key, new CrossSign(
                        DbValues.text(row.get("origin_site")),
                        signTime,
                        DbValues.text(row.get("student_no")),
                        DbValues.nullableInt(row.get("attendance_status"))));
            }
        }
        return result;
    }

    // ============================================================
    // 统计
    // ============================================================

    public int countSignedStudents(String taskId, String classId, Object courseDate, Object period) {
        if (taskId == null || classId == null || SyncContract.normalizeDate(courseDate).isEmpty()) {
            return 0;
        }
        String periodKey = SyncContract.normalizePeriod(period);
        Integer total = jdbc.queryForObject("""
                SELECT COUNT(*) AS signed_count
                FROM (
                    SELECT s.student_no AS student_no
                    FROM attendance_record ar
                    INNER JOIN students s ON s.id = ar.student_id
                    WHERE ar.task_id = ?
                    UNION
                    SELECT csr.student_no AS student_no
                    FROM cross_site_record csr
                    WHERE """ + VALID_CROSS_CONDITION + """
                      AND csr.course_date = ?
                      AND csr.period = ?
                      AND csr.student_no IN (
                          SELECT s2.student_no FROM students s2 WHERE s2.class_id = ?
                      )
                ) u
                """, Integer.class, taskId, SyncContract.normalizeDate(courseDate),
                periodKey.isEmpty() ? null : periodKey, classId);
        return total == null ? 0 : total;
    }

    public int[] attendanceStatusCounts(String taskId, String classId, Object courseDate, Object period) {
        int[] counts = new int[7];
        if (taskId == null || classId == null || SyncContract.normalizeDate(courseDate).isEmpty()) {
            return counts;
        }
        String periodKey = SyncContract.normalizePeriod(period);

        List<Map<String, Object>> rows = jdbc.queryForList("""
                SELECT u.status AS status, COUNT(*) AS cnt
                FROM (
                    SELECT s.student_no AS student_no, MIN(ar.status) AS status
                    FROM attendance_record ar
                    INNER JOIN students s ON s.id = ar.student_id
                    WHERE ar.task_id = ?
                    GROUP BY s.student_no
                    UNION
                    SELECT csr.student_no AS student_no, MIN(csr.attendance_status) AS status
                    FROM cross_site_record csr
                    WHERE """ + VALID_CROSS_CONDITION + """
                      AND csr.course_date = ?
                      AND csr.period = ?
                      AND csr.student_no IN (
                          SELECT s2.student_no FROM students s2 WHERE s2.class_id = ?
                      )
                      AND csr.student_no NOT IN (
                          SELECT s3.student_no
                          FROM attendance_record ar3
                          INNER JOIN students s3 ON s3.id = ar3.student_id
                          WHERE ar3.task_id = ?
                      )
                    GROUP BY csr.student_no
                ) u
                WHERE u.status IS NOT NULL
                GROUP BY u.status
                """, taskId, SyncContract.normalizeDate(courseDate),
                periodKey.isEmpty() ? null : periodKey, classId, taskId);

        for (Map<String, Object> row : rows) {
            Integer status = DbValues.nullableInt(row.get("status"));
            if (status != null && status >= 1 && status <= 6) {
                counts[status] += DbValues.intValue(row.get("cnt"));
            }
        }
        return counts;
    }

    /**
     * 批量统计（教师「签到任务」与「统计」页共用）。
     *
     * 本地按任务一次查出、外部记录按日期一次查出，
     * 避免每个任务各跑两条 SQL 的 N+1 往返。
     */
    public Map<String, TaskStat> taskStats(List<TaskContext> tasks) {
        Map<String, TaskStat> result = new HashMap<>();
        if (tasks == null || tasks.isEmpty()) {
            return result;
        }

        // 1) 本站签到：task_id -> (student_no -> min(status))
        List<String> taskIds = tasks.stream().map(TaskContext::taskId).toList();
        String placeholders = String.join(",", java.util.Collections.nCopies(taskIds.size(), "?"));
        List<Map<String, Object>> localRows = jdbc.queryForList("""
                SELECT ar.task_id AS task_id, s.student_no AS student_no, MIN(ar.status) AS status
                FROM attendance_record ar
                INNER JOIN students s ON s.id = ar.student_id
                WHERE ar.task_id IN (%s)
                GROUP BY ar.task_id, s.student_no
                """.formatted(placeholders), taskIds.toArray());

        Map<String, Map<String, Integer>> localByTask = new HashMap<>();
        for (Map<String, Object> row : localRows) {
            String taskId = DbValues.text(row.get("task_id"));
            localByTask.computeIfAbsent(taskId, key -> new HashMap<>())
                    .put(DbValues.text(row.get("student_no")), DbValues.nullableInt(row.get("status")));
        }

        // 2) 班级学号集合
        Set<String> classIds = new LinkedHashSet<>();
        for (TaskContext task : tasks) {
            if (task.classId() != null) {
                classIds.add(task.classId());
            }
        }
        Map<String, Set<String>> classStudents = new HashMap<>();
        if (!classIds.isEmpty()) {
            String classPlaceholders = String.join(",", java.util.Collections.nCopies(classIds.size(), "?"));
            for (Map<String, Object> row : jdbc.queryForList("""
                    SELECT class_id, student_no FROM students WHERE class_id IN (%s)
                    """.formatted(classPlaceholders), classIds.toArray())) {
                classStudents.computeIfAbsent(DbValues.text(row.get("class_id")), key -> new HashSet<>())
                        .add(DbValues.text(row.get("student_no")));
            }
        }

        // 3) 外部记录按日期一次查出
        Set<String> dates = new LinkedHashSet<>();
        for (TaskContext task : tasks) {
            String date = SyncContract.normalizeDate(task.courseDate());
            if (!date.isEmpty()) {
                dates.add(date);
            }
        }
        Map<String, List<Map<String, Object>>> crossByDate = new HashMap<>();
        if (!dates.isEmpty()) {
            String datePlaceholders = String.join(",", java.util.Collections.nCopies(dates.size(), "?"));
            List<Object> args = new ArrayList<>(dates);
            for (Map<String, Object> row : jdbc.queryForList("""
                    SELECT student_no, class_name, course_date, period, attendance_status
                    FROM `cross_site_record`
                    WHERE course_date IN (%s)""".formatted(datePlaceholders)
                            + " AND " + VALID_CROSS_CONDITION,
                    args.toArray())) {
                crossByDate.computeIfAbsent(SyncContract.normalizeDate(row.get("course_date")),
                        key -> new ArrayList<>()).add(row);
            }
        }

        // 4) 逐个任务合并（本地优先）
        for (TaskContext task : tasks) {
            int[] counts = new int[7];
            Set<String> signed = new HashSet<>();
            Map<String, Integer> local = localByTask.getOrDefault(task.taskId(), Map.of());

            for (Map.Entry<String, Integer> entry : local.entrySet()) {
                signed.add(entry.getKey());
                if (entry.getValue() != null && entry.getValue() >= 1 && entry.getValue() <= 6) {
                    counts[entry.getValue()]++;
                }
            }

            String date = SyncContract.normalizeDate(task.courseDate());
            String period = SyncContract.normalizePeriod(task.period());
            Set<String> roster = classStudents.getOrDefault(task.classId(), Set.of());

            for (Map<String, Object> row : crossByDate.getOrDefault(date, List.of())) {
                String studentNo = DbValues.text(row.get("student_no"));
                if (studentNo == null || !roster.contains(studentNo) || signed.contains(studentNo)) {
                    continue;
                }
                if (!SyncContract.normalizePeriod(row.get("period")).equals(period)) {
                    continue;
                }
                signed.add(studentNo);
                Integer status = DbValues.nullableInt(row.get("attendance_status"));
                if (status != null && status >= 1 && status <= 6) {
                    counts[status]++;
                }
            }

            result.put(task.taskId(), new TaskStat(signed.size(), counts));
        }

        return result;
    }

    public List<Map<String, Object>> crossRecordsForStudent(String studentNo, String dateFilter) {
        List<Map<String, Object>> rows = new ArrayList<>();
        if (studentNo == null || studentNo.isEmpty()) {
            return rows;
        }

        String sql = """
                SELECT id, origin_site, class_name, course_name, course_date,
                       period, time_slot, attendance_status, sign_time,
                       device_id, location, ip, is_script
                FROM `cross_site_record`
                WHERE student_no = ? AND """ + VALID_CROSS_CONDITION;

        List<Object> args = new ArrayList<>();
        args.add(truncate(SyncContract.normalizeText(studentNo), 32));

        if (dateFilter != null && !dateFilter.isEmpty()) {
            sql += " AND DATE(sign_time) = ?";
            args.add(dateFilter);
        }
        sql += " ORDER BY sign_time DESC";

        rows.addAll(jdbc.queryForList(sql, args.toArray()));
        return rows;
    }

    // ============================================================
    // 对账
    // ============================================================

    private record Candidate(String kind, String id, String originSite, String originRecordId,
                             LocalDateTime signTime, String studentName, Integer attendanceStatus,
                             String alignKey) {
    }

    public Map<String, Object> reconcile() {
        Map<String, Object> stats = new LinkedHashMap<>();
        int groups = 0;
        int voided = 0;
        int conflicts = 0;
        stats.put("groups", groups);
        stats.put("voided", voided);
        stats.put("conflicts", conflicts);

        List<Map<String, Object>> crossRows = jdbc.queryForList("""
                SELECT id, origin_site, origin_record_id, student_no, student_name,
                       class_name, course_name, course_date, period, time_slot,
                       align_key, attendance_status, sign_time
                FROM `cross_site_record`
                WHERE resolve_state <> ?
                  AND sign_time >= DATE_SUB(NOW(), INTERVAL ? DAY)
                """, RESOLVE_VOID, SyncConfig.RECONCILE_DAYS);

        if (crossRows.isEmpty()) {
            return stats;
        }

        Set<String> studentNos = new LinkedHashSet<>();
        for (Map<String, Object> row : crossRows) {
            String studentNo = SyncContract.normalizeText(row.get("student_no"));
            if (!studentNo.isEmpty()) {
                studentNos.add(studentNo);
            }
        }

        Map<String, List<Candidate>> groupsMap = new HashMap<>();

        if (!studentNos.isEmpty()) {
            String placeholders = String.join(",", java.util.Collections.nCopies(studentNos.size(), "?"));
            List<Object> args = new ArrayList<>(studentNos);
            args.add(SyncConfig.RECONCILE_DAYS);

            for (Map<String, Object> row : jdbc.queryForList("""
                    SELECT ar.id AS record_id, ar.sign_time, ar.status,
                           s.student_no, s.name AS student_name, cl.name AS class_name,
                           c.name AS course_name, c.course_date, c.time AS time_raw
                    FROM attendance_record ar
                    JOIN students s ON s.id = ar.student_id
                    JOIN attendance_task at ON at.id = ar.task_id
                    JOIN courses c ON c.id = at.course_id
                    LEFT JOIN classes cl ON cl.id = s.class_id
                    WHERE s.student_no IN (%s)
                      AND c.course_date >= DATE_SUB(CURDATE(), INTERVAL ? DAY)
                    """.formatted(placeholders), args.toArray())) {

                String alignKey = SyncContract.buildAlignKey(row.get("student_no"), row.get("class_name"),
                        row.get("course_date"), row.get("time_raw"));
                groupsMap.computeIfAbsent(alignKey, key -> new ArrayList<>()).add(new Candidate(
                        "local",
                        DbValues.text(row.get("record_id")),
                        config.siteCode(),
                        DbValues.text(row.get("record_id")),
                        DbValues.localDateTime(row.get("sign_time")),
                        DbValues.text(row.get("student_name")),
                        DbValues.nullableInt(row.get("status")),
                        alignKey));
            }
        }

        for (Map<String, Object> row : crossRows) {
            String alignKey = DbValues.text(row.get("align_key"));
            if (alignKey == null || alignKey.isEmpty()) {
                alignKey = SyncContract.buildAlignKey(row.get("student_no"), row.get("class_name"),
                        row.get("course_date"), row.get("period"));
            }
            groupsMap.computeIfAbsent(alignKey, key -> new ArrayList<>()).add(new Candidate(
                    "cross",
                    DbValues.text(row.get("id")),
                    DbValues.text(row.get("origin_site")),
                    DbValues.text(row.get("origin_record_id")),
                    DbValues.localDateTime(row.get("sign_time")),
                    DbValues.text(row.get("student_name")),
                    DbValues.nullableInt(row.get("attendance_status")),
                    alignKey));
        }

        for (Map.Entry<String, List<Candidate>> entry : groupsMap.entrySet()) {
            List<Candidate> candidates = entry.getValue();
            if (candidates.size() < 2) {
                continue;
            }
            Set<String> sites = new HashSet<>();
            for (Candidate candidate : candidates) {
                sites.add(candidate.originSite());
            }
            if (sites.size() < 2) {
                continue;
            }

            groups++;

            Candidate winner = candidates.stream().min(Comparator
                    .comparing((Candidate c) -> c.signTime(), SyncStore::compareNullLast)
                    .thenComparing(c -> "local".equals(c.kind()) ? 0 : 1)
                    .thenComparing(c -> c.originSite() == null ? "" : c.originSite())
                    .thenComparing(c -> c.originRecordId() == null ? "" : c.originRecordId()))
                    .orElseThrow();

            List<Candidate> crossLosers = new ArrayList<>();
            List<Candidate> localLosers = new ArrayList<>();
            for (Candidate candidate : candidates) {
                if (candidate == winner) {
                    continue;
                }
                if ("cross".equals(candidate.kind())) {
                    crossLosers.add(candidate);
                } else {
                    localLosers.add(candidate);
                }
            }

            for (Candidate loser : crossLosers) {
                writer.update("""
                        UPDATE `cross_site_record`
                        SET resolve_state = ?, is_duplicate = 1, duplicate_of = ?
                        WHERE id = ?
                        """, RESOLVE_VOID, winner.id(), loser.id());
                voided++;
            }

            if (!localLosers.isEmpty()) {
                Integer count = jdbc.queryForObject("""
                        SELECT COUNT(*) AS cnt
                        FROM `cross_site_conflict`
                        WHERE align_key = ? AND winner_record_id = ?
                        """, Integer.class, truncate(entry.getKey(), 255), winner.id());

                if (count == null || count == 0) {
                    List<Map<String, Object>> losers = new ArrayList<>();
                    for (Candidate loser : localLosers) {
                        Map<String, Object> item = new LinkedHashMap<>();
                        item.put("site", loser.originSite());
                        item.put("record_id", loser.id());
                        item.put("sign_time", loser.signTime() == null ? "" : loser.signTime().toString());
                        item.put("attendance_status", loser.attendanceStatus());
                        losers.add(item);
                    }

                    Map<String, Object> winnerItem = new LinkedHashMap<>();
                    winnerItem.put("site", winner.originSite());
                    winnerItem.put("record_id", winner.id());
                    winnerItem.put("sign_time", winner.signTime() == null ? "" : winner.signTime().toString());

                    Map<String, Object> loserJson = new LinkedHashMap<>();
                    loserJson.put("winner", winnerItem);
                    loserJson.put("losers", losers);

                    String json;
                    try {
                        json = mapper.writeValueAsString(loserJson);
                    } catch (Exception e) {
                        json = "{}";
                    }

                    writer.update("""
                            INSERT INTO `cross_site_conflict`
                            (`id`, `align_key`, `winner_record_id`, `winner_site`, `loser_json`, `state`)
                            VALUES (?, ?, ?, ?, ?, ?)
                            """, UUID.randomUUID().toString(), truncate(entry.getKey(), 255),
                            winner.id(), winner.originSite(), json, CONFLICT_PENDING);
                    conflicts++;
                }
            }
        }

        stats.put("groups", groups);
        stats.put("voided", voided);
        stats.put("conflicts", conflicts);
        return stats;
    }

    // ============================================================
    // 管理页
    // ============================================================

    public Map<String, Object> outboxStats() {
        Map<String, Object> stats = new LinkedHashMap<>();
        stats.put(String.valueOf(OUTBOX_PENDING), 0);
        stats.put(String.valueOf(OUTBOX_SENT), 0);
        stats.put(String.valueOf(OUTBOX_FAILED), 0);

        for (Map<String, Object> row : jdbc.queryForList("""
                SELECT status, COUNT(*) AS cnt FROM `sync_outbox` GROUP BY status
                """)) {
            stats.put(DbValues.text(row.get("status")), DbValues.intValue(row.get("cnt")));
        }
        return stats;
    }

    public List<Map<String, Object>> listOutbox(Integer status, int limit) {
        if (status == null) {
            return jdbc.queryForList("""
                    SELECT id, target_peer, event_id, event_type, status,
                           retry_count, next_retry_at, last_error, created_at, sent_at
                    FROM `sync_outbox`
                    ORDER BY id ASC
                    LIMIT ?
                    """, limit);
        }
        return jdbc.queryForList("""
                SELECT id, target_peer, event_id, event_type, status,
                       retry_count, next_retry_at, last_error, created_at, sent_at
                FROM `sync_outbox`
                WHERE status = ?
                ORDER BY id ASC
                LIMIT ?
                """, status, limit);
    }

    public int retryOutbox(long outboxId) {
        return writer.update("""
                UPDATE `sync_outbox`
                SET status = ?, retry_count = 0, next_retry_at = NOW(), last_error = NULL
                WHERE id = ?
                """, OUTBOX_PENDING, outboxId);
    }

    public int countPendingOutbox() {
        Integer count = jdbc.queryForObject(
                "SELECT COUNT(*) AS cnt FROM `sync_outbox` WHERE status = ?",
                Integer.class, OUTBOX_PENDING);
        return count == null ? 0 : count;
    }

    public List<Map<String, Object>> listConflicts(Integer state, int limit, String keyword) {
        List<Object> args = new ArrayList<>();
        String where = conflictWhere(state, keyword, args);
        args.add(limit);

        return jdbc.queryForList(
                "SELECT id, align_key, winner_record_id, winner_site, "
                        + "loser_json, state, created_at, handled_by, handled_at "
                        + "FROM `cross_site_conflict`"
                        + where
                        + " ORDER BY created_at DESC LIMIT ?",
                args.toArray());
    }

    public int countConflicts(Integer state, String keyword) {
        List<Object> args = new ArrayList<>();
        String where = conflictWhere(state, keyword, args);
        Integer count = jdbc.queryForObject(
                "SELECT COUNT(*) AS cnt FROM `cross_site_conflict`" + where,
                Integer.class, args.toArray());
        return count == null ? 0 : count;
    }

    private static String conflictWhere(Integer state, String keyword, List<Object> args) {
        List<String> clauses = new ArrayList<>();
        if (state != null) {
            clauses.add("`state` = ?");
            args.add(state);
        }
        String normalized = SyncContract.normalizeText(keyword);
        if (!normalized.isEmpty()) {
            clauses.add("`align_key` LIKE ?");
            args.add("%" + normalized + "%");
        }
        return clauses.isEmpty() ? "" : " WHERE " + String.join(" AND ", clauses);
    }

    public int handleConflicts(String action, String userId, List<String> ids) {
        int state = "resolve".equals(action) ? CONFLICT_RESOLVED : CONFLICT_IGNORED;

        List<String> cleanIds = new ArrayList<>();
        for (String id : ids == null ? List.<String>of() : ids) {
            String text = SyncContract.normalizeText(id);
            if (!text.isEmpty()) {
                cleanIds.add(text);
            }
        }

        StringBuilder sql = new StringBuilder("""
                UPDATE `cross_site_conflict`
                SET state = ?, handled_by = ?, handled_at = NOW()
                WHERE state = ?
                """);
        List<Object> args = new ArrayList<>();
        args.add(state);
        args.add(userId);
        args.add(CONFLICT_PENDING);

        if (!cleanIds.isEmpty()) {
            sql.append(" AND `id` IN (")
                    .append(String.join(",", java.util.Collections.nCopies(cleanIds.size(), "?")))
                    .append(")");
            args.addAll(cleanIds);
        }

        return writer.update(sql.toString(), args.toArray());
    }

    public int countPendingConflicts() {
        Integer count = jdbc.queryForObject(
                "SELECT COUNT(*) AS cnt FROM `cross_site_conflict` WHERE state = ?",
                Integer.class, CONFLICT_PENDING);
        return count == null ? 0 : count;
    }

    public int handleConflict(String conflictId, String action, String userId) {
        int state = "resolve".equals(action) ? CONFLICT_RESOLVED : CONFLICT_IGNORED;
        return writer.update("""
                UPDATE `cross_site_conflict`
                SET state = ?, handled_by = ?, handled_at = NOW()
                WHERE id = ? AND state = ?
                """, state, userId, conflictId, CONFLICT_PENDING);
    }

    public Map<String, Object> crossRecordCount() {
        Map<String, Object> result = new LinkedHashMap<>();
        List<Map<String, Object>> rows = jdbc.queryForList("""
                SELECT COUNT(*) AS total,
                       SUM(CASE WHEN resolve_state = 2 THEN 1 ELSE 0 END) AS voided
                FROM `cross_site_record`
                """);
        Map<String, Object> row = rows.isEmpty() ? Map.of() : rows.get(0);
        result.put("total", DbValues.intValue(row.get("total")));
        result.put("voided", DbValues.intValue(row.get("voided")));
        return result;
    }

    // ============================================================
    // 小工具
    // ============================================================

    private static int compareNullLast(LocalDateTime left, LocalDateTime right) {
        if (left == null && right == null) {
            return 0;
        }
        if (left == null) {
            return 1;
        }
        if (right == null) {
            return -1;
        }
        return left.compareTo(right);
    }

    private static String truncate(String value, int max) {
        if (value == null) {
            return "";
        }
        return value.length() > max ? value.substring(0, max) : value;
    }

    private static String truncate(Object value, int max) {
        return truncate(value == null ? "" : String.valueOf(value), max);
    }

    private static String nullIfEmpty(String value) {
        return value == null || value.isEmpty() ? null : value;
    }

    private static String emptyToNull(String value) {
        return value == null || value.isEmpty() ? null : value;
    }

    private static int toInt(Object value) {
        if (value instanceof Number number) {
            return number.intValue();
        }
        if (value == null || String.valueOf(value).isBlank()) {
            return 0;
        }
        return Integer.parseInt(String.valueOf(value).trim());
    }
}
