package com.stu.signin.sync;

import com.stu.signin.common.DbValues;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/**
 * 整库快照形态，对应 Python sync/snapshot.py。
 *
 * 对接只提供整库快照、不实现契约四接口的对端（A 站）：
 *   - buildSnapshot()  导出本站快照（对端 /api/sync/export 的格式）
 *   - importSnapshot() 把对端整库 JSON 转成契约事件并入账
 *
 * 入账不写本地考勤表：快照 records 先转成契约事件，
 * 再走 SyncStore.ingestEvents 落进 cross_site_record。
 */
@Service
public class SnapshotService {

    public static final int SNAPSHOT_VERSION = 1;

    /** 快照里的班级键是 int 列，超过 9 位数字改用哈希，避免溢出 */
    private static final int MAX_CLASS_DIGITS = 9;

    private final JdbcTemplate jdbc;
    private final SyncStore store;

    public SnapshotService(JdbcTemplate jdbc, SyncStore store) {
        this.jdbc = jdbc;
        this.store = store;
    }

    // ============================================================
    // 小工具
    // ============================================================

    @SuppressWarnings("unchecked")
    private static List<Object> asList(Object value) {
        return value instanceof List<?> list ? (List<Object>) list : List.of();
    }

    @SuppressWarnings("unchecked")
    private static Map<String, Object> asMap(Object value) {
        return value instanceof Map<?, ?> map ? (Map<String, Object>) map : null;
    }

    private static String stamp(Object value) {
        LocalDateTime parsed = DbValues.localDateTime(value);
        return parsed == null ? null : parsed.format(java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss"));
    }

    private static String secondText(Object value) {
        LocalDateTime parsed = SyncContract.toDbDateTime(value);
        if (parsed == null) {
            return SyncContract.normalizeText(value);
        }
        return parsed.format(java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
    }

    private static String[] splitTimeSlot(Object text) {
        String normalized = SyncContract.normalizeTimeSlot(text);
        int index = normalized.indexOf('-');
        if (index < 0) {
            return new String[]{null, null};
        }
        String start = normalized.substring(0, index).trim();
        String end = normalized.substring(index + 1).trim();
        return new String[]{start.isEmpty() ? null : start, end.isEmpty() ? null : end};
    }

    private static LocalDateTime dayStart(Object dateText, String timeText) {
        String date = SyncContract.normalizeDate(dateText);
        if (date.isEmpty() || timeText == null || timeText.isEmpty()) {
            return null;
        }
        return SyncContract.toDbDateTime(date + " " + timeText);
    }

    private static String md5Hex(String value) {
        try {
            MessageDigest digest = MessageDigest.getInstance("MD5");
            byte[] bytes = digest.digest(value.getBytes(StandardCharsets.UTF_8));
            StringBuilder out = new StringBuilder();
            for (byte b : bytes) {
                out.append(String.format("%02x", b));
            }
            return out.toString();
        } catch (Exception e) {
            throw new IllegalStateException("MD5 不可用", e);
        }
    }

    // ============================================================
    // 字段映射
    // ============================================================

    public static int classIdOf(Object className) {
        String key = SyncContract.normalizeClassKey(className);

        if (!key.isEmpty() && key.chars().allMatch(Character::isDigit) && key.length() <= MAX_CLASS_DIGITS) {
            return Integer.parseInt(key);
        }
        if (key.isEmpty()) {
            return 0;
        }
        return Integer.parseInt(md5Hex(key).substring(0, 8), 16);
    }

    public static String statusToRemote(Object status) {
        Integer normalized = SyncContract.normalizeAttendanceStatus(status);
        if (normalized == null) {
            return "normal";
        }
        return switch (normalized) {
            case 2 -> "late";
            case 3 -> "absent";
            default -> "normal";
        };
    }

    public static String sourceOf(Object isScript, Object deviceId) {
        if (DbValues.intValue(isScript) == 1) {
            return "script";
        }
        return SyncContract.normalizeText(deviceId).isEmpty() ? "auto" : "manual";
    }

    public static String snapshotRecordId(Object studentNo, Object checkInTime, Object period) {
        String raw = SyncContract.normalizeText(studentNo) + "|"
                + secondText(checkInTime) + "|"
                + SyncContract.normalizePeriod(period);
        return "snap-" + md5Hex(raw).substring(0, 16);
    }

    // ============================================================
    // 导出
    // ============================================================

    private List<Map<String, Object>> snapshotStudents() {
        List<Map<String, Object>> rows = new ArrayList<>();
        Map<String, Integer> seqByClass = new HashMap<>();

        for (Map<String, Object> row : jdbc.queryForList("""
                SELECT s.student_no AS student_no,
                       s.name AS student_name,
                       cl.name AS class_name
                FROM `students` s
                LEFT JOIN `classes` cl ON cl.id = s.class_id
                WHERE s.student_no IS NOT NULL AND s.student_no <> ''
                ORDER BY cl.name ASC, s.student_no ASC
                """)) {

            String classKey = SyncContract.normalizeClassKey(row.get("class_name"));
            int seq = seqByClass.getOrDefault(classKey, 0) + 1;
            seqByClass.put(classKey, seq);

            Map<String, Object> item = new LinkedHashMap<>();
            item.put("name", DbValues.text(row.get("student_name")));
            item.put("student_id", DbValues.text(row.get("student_no")));
            item.put("class_id", classIdOf(row.get("class_name")));
            item.put("seq", seq);
            rows.add(item);
        }
        return rows;
    }

    private List<Map<String, Object>> snapshotSessions(String sinceDate) {
        List<Map<String, Object>> sessions = new ArrayList<>();
        LocalDateTime now = LocalDateTime.now();

        for (Map<String, Object> row : jdbc.queryForList("""
                SELECT cl.name AS class_name,
                       c.course_date AS course_date,
                       c.time AS course_time
                FROM `courses` c
                LEFT JOIN `classes` cl ON cl.id = c.class_id
                WHERE c.course_date >= ?
                ORDER BY cl.name ASC, c.course_date ASC, c.time ASC
                """, sinceDate)) {

            String[] slot = splitTimeSlot(row.get("course_time"));
            LocalDateTime startAt = dayStart(row.get("course_date"), slot[0]);
            LocalDateTime endAt = dayStart(row.get("course_date"), slot[1]);

            Map<String, Object> item = new LinkedHashMap<>();
            item.put("class_id", classIdOf(row.get("class_name")));
            item.put("start_time", stamp(startAt));
            item.put("end_time", stamp(endAt));
            item.put("location", null);
            item.put("client_ip", null);
            item.put("is_active", startAt != null && endAt != null
                    && !startAt.isAfter(now) && !endAt.isBefore(now));
            sessions.add(item);
        }
        return sessions;
    }

    private List<Map<String, Object>> snapshotRecords(String sinceDate) {
        List<Map<String, Object>> records = new ArrayList<>();

        for (Map<String, Object> row : jdbc.queryForList("""
                SELECT s.student_no AS student_no,
                       ar.sign_time AS sign_time,
                       ar.status AS status,
                       ar.ip AS ip,
                       ar.device_id AS device_id,
                       ar.location AS location,
                       ar.is_script AS is_script,
                       c.time AS course_time
                FROM `attendance_record` ar
                JOIN `students` s ON s.id = ar.student_id
                JOIN `attendance_task` at ON at.id = ar.task_id
                JOIN `courses` c ON c.id = at.course_id
                WHERE ar.sign_time >= ?
                ORDER BY ar.sign_time ASC
                """, sinceDate)) {

            Map<String, Object> item = new LinkedHashMap<>();
            item.put("student_id", DbValues.text(row.get("student_no")));
            item.put("check_in_time", stamp(row.get("sign_time")));
            item.put("status", statusToRemote(row.get("status")));
            item.put("period", SyncContract.normalizePeriod(row.get("course_time")));
            item.put("source", sourceOf(row.get("is_script"), row.get("device_id")));
            item.put("client_ip", DbValues.text(row.get("ip")));
            item.put("client_fp", null);
            item.put("is_script", DbValues.intValue(row.get("is_script")) != 0);
            item.put("location", DbValues.text(row.get("location")));
            item.put("device_fp", DbValues.text(row.get("device_id")));
            item.put("suspicious", false);
            item.put("suspicious_reason", null);
            records.add(item);
        }
        return records;
    }

    public Map<String, Object> buildSnapshot(int days) {
        String sinceDate = LocalDate.now().minusDays(days)
                .format(java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd"));

        Map<String, Object> snapshot = new LinkedHashMap<>();
        snapshot.put("version", SNAPSHOT_VERSION);
        snapshot.put("exported_at", stamp(LocalDateTime.now()));
        snapshot.put("students", snapshotStudents());
        snapshot.put("sessions", snapshotSessions(sinceDate));
        snapshot.put("records", snapshotRecords(sinceDate));
        return snapshot;
    }

    public Map<String, Object> buildSnapshot() {
        return buildSnapshot(SyncConfig.RECONCILE_DAYS);
    }

    // ============================================================
    // 入账
    // ============================================================

    private static Map<String, String> classOfStudent(Map<String, Object> snapshot) {
        Map<String, String> mapping = new HashMap<>();
        for (Object raw : asList(snapshot.get("students"))) {
            Map<String, Object> item = asMap(raw);
            if (item == null) {
                continue;
            }
            String studentNo = SyncContract.normalizeText(item.get("student_id"));
            if (!studentNo.isEmpty()) {
                mapping.put(studentNo, SyncContract.normalizeText(item.get("class_id")));
            }
        }
        return mapping;
    }

    private static Map<String, String> timeSlotsOfSessions(Map<String, Object> snapshot) {
        Map<String, String> slots = new HashMap<>();

        for (Object raw : asList(snapshot.get("sessions"))) {
            Map<String, Object> item = asMap(raw);
            if (item == null) {
                continue;
            }
            String classKey = SyncContract.normalizeClassKey(item.get("class_id"));
            LocalDateTime startAt = SyncContract.toDbDateTime(item.get("start_time"));
            LocalDateTime endAt = SyncContract.toDbDateTime(item.get("end_time"));

            if (classKey.isEmpty() || startAt == null) {
                continue;
            }
            String key = classKey + "|" + startAt.toLocalDate();
            if (endAt == null) {
                slots.putIfAbsent(key, "");
                continue;
            }
            slots.put(key, String.format(Locale.ROOT, "%02d:%02d-%02d:%02d",
                    startAt.getHour(), startAt.getMinute(), endAt.getHour(), endAt.getMinute()));
        }
        return slots;
    }

    private static String periodOf(Map<String, Object> item, LocalDateTime signTime) {
        String period = SyncContract.normalizePeriod(item.get("period"));
        if (!period.isEmpty()) {
            return period;
        }
        return signTime.getHour() < 12 ? "morning" : "afternoon";
    }

    private record EventPair(String studentNo, Map<String, Object> event) {
    }

    private static List<EventPair> recordsToEvents(Map<String, Object> snapshot, String originSite) {
        Map<String, String> classOf = classOfStudent(snapshot);
        Map<String, String> slots = timeSlotsOfSessions(snapshot);
        List<EventPair> pairs = new ArrayList<>();

        for (Object raw : asList(snapshot.get("records"))) {
            Map<String, Object> item = asMap(raw);
            if (item == null) {
                continue;
            }

            String studentNo = SyncContract.normalizeText(item.get("student_id"));
            LocalDateTime signTime = SyncContract.toDbDateTime(item.get("check_in_time"));

            if (studentNo.isEmpty() || signTime == null) {
                continue;
            }

            String className = classOf.getOrDefault(studentNo, "");
            String period = periodOf(item, signTime);
            String timeSlot = slots.getOrDefault(
                    SyncContract.normalizeClassKey(className) + "|" + signTime.toLocalDate(), "");

            Map<String, Object> event = SyncContract.buildEvent(
                    SyncContract.EVENT_SIGNIN,
                    originSite,
                    snapshotRecordId(studentNo, signTime, period),
                    studentNo,
                    className,
                    signTime.toLocalDate(),
                    period,
                    item.get("status"),
                    signTime,
                    null,
                    timeSlot,
                    null,
                    item.get("device_fp"),
                    item.get("client_ip"),
                    item.get("location"),
                    Boolean.TRUE.equals(item.get("is_script")) ? 1 : 0,
                    null,
                    null,
                    null);

            pairs.add(new EventPair(studentNo, event));
        }
        return pairs;
    }

    public List<Map<String, Object>> snapshotToEvents(Map<String, Object> snapshot, String originSite) {
        List<Map<String, Object>> events = new ArrayList<>();
        for (EventPair pair : recordsToEvents(snapshot, originSite)) {
            events.add(pair.event());
        }
        return events;
    }

    public Map<String, Object> importSnapshot(Map<String, Object> snapshot, String originSite) {
        Map<String, Object> result = new LinkedHashMap<>();

        if (snapshot == null) {
            result.put("success", false);
            result.put("created_students", 0);
            result.put("skipped_students", 0);
            result.put("created_sessions", 0);
            result.put("skipped_sessions", 0);
            result.put("created_records", 0);
            result.put("skipped_records", 0);
            result.put("errors", List.of("快照不是 JSON 对象"));
            return result;
        }

        List<EventPair> pairs = recordsToEvents(snapshot, originSite);
        List<Map<String, Object>> events = new ArrayList<>();
        Map<String, String> byEventId = new HashMap<>();

        for (EventPair pair : pairs) {
            events.add(pair.event());
            byEventId.put(String.valueOf(pair.event().get("event_id")), pair.studentNo());
        }

        SyncStore.IngestResult ingest = store.ingestEvents(events);

        List<String> errors = new ArrayList<>();
        for (Map<String, Object> rejected : ingest.rejected()) {
            String studentNo = byEventId.get(String.valueOf(rejected.get("event_id")));
            if (studentNo != null && !studentNo.isEmpty()) {
                errors.add("签到记录 " + studentNo + "：" + rejected.get("reason"));
            } else {
                errors.add(String.valueOf(rejected.get("reason")));
            }
        }

        result.put("success", true);
        result.put("created_students", 0);
        result.put("skipped_students", asList(snapshot.get("students")).size());
        result.put("created_sessions", 0);
        result.put("skipped_sessions", asList(snapshot.get("sessions")).size());
        result.put("created_records", ingest.accepted().size());
        result.put("skipped_records", ingest.duplicated().size());
        result.put("errors", errors);
        return result;
    }
}
