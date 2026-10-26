package com.stu.signin.sync;

import java.time.Instant;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.OffsetDateTime;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.UUID;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * 跨站同步契约层，对应 Python sync/contract.py。
 *
 * 归一化规则是三站之间唯一约定，必须与对端实现完全一致，
 * 否则同一门课会对不上。
 */
public final class SyncContract {

    public static final String SCHEMA_VERSION = "1.0";

    public static final String EVENT_SIGNIN = "attendance.signin";
    public static final String EVENT_UPDATE = "attendance.update";
    public static final String EVENT_DELETE = "attendance.delete";

    public static final List<String> EVENT_TYPES = List.of(EVENT_SIGNIN, EVENT_UPDATE, EVENT_DELETE);

    public static final String ALIGN_SEP = "|";

    public static final Map<Integer, String> STATUS_TEXT = Map.of(
            1, "正常",
            2, "迟到",
            3, "旷课",
            4, "早退",
            5, "病假",
            6, "事假");

    private static final Map<String, Integer> STATUS_ALIAS = Map.ofEntries(
            Map.entry("normal", 1),
            Map.entry("正常", 1),
            Map.entry("late", 2),
            Map.entry("迟到", 2),
            Map.entry("absent", 3),
            Map.entry("旷课", 3),
            Map.entry("缺勤", 3),
            Map.entry("early", 4),
            Map.entry("早退", 4),
            Map.entry("sick", 5),
            Map.entry("病假", 5),
            Map.entry("leave", 6),
            Map.entry("事假", 6));

    private static final ZoneId LOCAL_ZONE = ZoneId.systemDefault();

    private static final Pattern TIME_RE = Pattern.compile("(\\d{1,2})\\s*[:：]\\s*(\\d{1,2})");
    private static final Pattern LONG_DIGITS_RE = Pattern.compile("\\d{6,}");

    private static final DateTimeFormatter DATE_FORMAT = DateTimeFormatter.ofPattern("yyyy-MM-dd");
    private static final DateTimeFormatter DATE_TIME_FORMAT = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    private SyncContract() {
    }

    public record ValidationResult(boolean valid, String reason) {
    }

    // ============================================================
    // 归一化
    // ============================================================

    public static String normalizeText(Object value) {
        if (value == null) {
            return "";
        }
        String text = String.valueOf(value).replace("\u3000", " ");
        return text.trim().replaceAll("\\s+", " ");
    }

    public static String normalizeTimeSlot(Object value) {
        if (value == null) {
            return "";
        }
        String text = String.valueOf(value);

        Matcher matcher = TIME_RE.matcher(text);
        List<int[]> found = new ArrayList<>();
        while (matcher.find()) {
            found.add(new int[]{Integer.parseInt(matcher.group(1)), Integer.parseInt(matcher.group(2))});
        }

        if (found.size() >= 2) {
            return String.format("%02d:%02d-%02d:%02d",
                    found.get(0)[0], found.get(0)[1], found.get(1)[0], found.get(1)[1]);
        }

        String fallback = normalizeText(text).replace(" ", "");
        for (String sep : List.of("~", "至", "—", "－", "到")) {
            fallback = fallback.replace(sep, "-");
        }
        return fallback;
    }

    public static String normalizeDate(Object value) {
        if (value == null) {
            return "";
        }
        if (value instanceof LocalDate date) {
            return date.format(DATE_FORMAT);
        }
        if (value instanceof LocalDateTime dateTime) {
            return dateTime.format(DATE_FORMAT);
        }
        if (value instanceof java.sql.Date date) {
            return date.toLocalDate().format(DATE_FORMAT);
        }
        if (value instanceof java.sql.Timestamp timestamp) {
            return timestamp.toLocalDateTime().format(DATE_FORMAT);
        }
        if (value instanceof java.util.Date date) {
            return date.toInstant().atZone(LOCAL_ZONE).toLocalDate().format(DATE_FORMAT);
        }

        String text = normalizeText(value);
        if (text.isEmpty()) {
            return "";
        }

        String head = text.length() > 10 ? text.substring(0, 10) : text;
        for (String pattern : List.of("yyyy-MM-dd", "yyyy/MM/dd", "yyyy.MM.dd", "yyyyMMdd")) {
            try {
                return LocalDate.parse(head, DateTimeFormatter.ofPattern(pattern)).format(DATE_FORMAT);
            } catch (Exception ignored) {
                // 继续尝试下一个格式
            }
        }

        return head;
    }

    public static String normalizePeriod(Object value) {
        if (value == null) {
            return "";
        }
        String text = normalizeText(value).toLowerCase(Locale.ROOT);
        if (text.isEmpty()) {
            return "";
        }

        for (String word : List.of("afternoon", "下午", "午后")) {
            if (text.contains(word)) {
                return "afternoon";
            }
        }
        for (String word : List.of("morning", "上午", "早上", "清晨")) {
            if (text.contains(word)) {
                return "morning";
            }
        }

        Matcher matcher = TIME_RE.matcher(text);
        if (matcher.find()) {
            int hour = Integer.parseInt(matcher.group(1));
            return hour < 12 ? "morning" : "afternoon";
        }

        return "";
    }

    public static Integer normalizeAttendanceStatus(Object value) {
        if (value == null || "".equals(value)) {
            return null;
        }
        if (value instanceof Boolean) {
            return null;
        }
        if (value instanceof Number number) {
            int parsed = number.intValue();
            return STATUS_TEXT.containsKey(parsed) ? parsed : null;
        }

        String text = normalizeText(value).toLowerCase(Locale.ROOT);
        if (text.isEmpty()) {
            return null;
        }
        if (text.chars().allMatch(Character::isDigit)) {
            int parsed = Integer.parseInt(text);
            return STATUS_TEXT.containsKey(parsed) ? parsed : null;
        }
        return STATUS_ALIAS.get(text);
    }

    public static String normalizeClassKey(Object value) {
        String text = normalizeText(value);
        if (text.isEmpty()) {
            return "";
        }
        Matcher matcher = LONG_DIGITS_RE.matcher(text);
        if (matcher.find()) {
            return matcher.group();
        }
        return text;
    }

    public static String buildAlignKey(Object studentNo, Object className, Object courseDate, Object period) {
        return String.join(ALIGN_SEP,
                normalizeText(studentNo),
                normalizeClassKey(className),
                normalizeDate(courseDate),
                normalizePeriod(period));
    }

    @SuppressWarnings("unchecked")
    public static String alignKeyOfPayload(Object payload) {
        if (!(payload instanceof Map<?, ?> map)) {
            return "";
        }
        Object period = map.get("period");
        if (period == null || normalizeText(period).isEmpty()) {
            period = map.get("time_slot");
        }
        return buildAlignKey(map.get("student_no"), map.get("class_name"), map.get("course_date"), period);
    }

    // ============================================================
    // 时间转换
    // ============================================================

    public static String toIso(Object value) {
        if (value == null) {
            return null;
        }
        if (value instanceof String text) {
            return text;
        }
        LocalDateTime local = toLocalDateTime(value);
        if (local == null) {
            return String.valueOf(value);
        }
        return local.atZone(LOCAL_ZONE).toOffsetDateTime().toString();
    }

    public static LocalDateTime toDbDateTime(Object value) {
        if (value == null || "".equals(value)) {
            return null;
        }
        if (value instanceof LocalDateTime dateTime) {
            return dateTime;
        }
        if (value instanceof LocalDate date) {
            return date.atStartOfDay();
        }
        if (value instanceof java.sql.Timestamp timestamp) {
            return timestamp.toLocalDateTime();
        }
        if (value instanceof java.util.Date date) {
            return LocalDateTime.ofInstant(date.toInstant(), LOCAL_ZONE);
        }

        String text = String.valueOf(value).trim();
        if (text.isEmpty()) {
            return null;
        }

        try {
            return OffsetDateTime.parse(text.replace("Z", "+00:00"))
                    .atZoneSameInstant(LOCAL_ZONE).toLocalDateTime();
        } catch (Exception ignored) {
            // 继续尝试其它格式
        }
        try {
            return ZonedDateTime.parse(text).withZoneSameInstant(LOCAL_ZONE).toLocalDateTime();
        } catch (Exception ignored) {
            // 继续尝试其它格式
        }
        try {
            return LocalDateTime.parse(text);
        } catch (Exception ignored) {
            // 继续尝试其它格式
        }
        try {
            return LocalDateTime.ofInstant(Instant.parse(text), LOCAL_ZONE);
        } catch (Exception ignored) {
            // 继续尝试其它格式
        }

        for (String pattern : List.of("yyyy-MM-dd HH:mm:ss", "yyyy-MM-dd'T'HH:mm:ss",
                "yyyy-MM-dd HH:mm", "yyyy-MM-dd")) {
            try {
                return LocalDateTime.parse(text, DateTimeFormatter.ofPattern(pattern));
            } catch (Exception ignored) {
                // 继续尝试下一个格式
            }
        }

        return null;
    }

    private static LocalDateTime toLocalDateTime(Object value) {
        if (value instanceof LocalDateTime dateTime) {
            return dateTime;
        }
        if (value instanceof OffsetDateTime offset) {
            return offset.atZoneSameInstant(LOCAL_ZONE).toLocalDateTime();
        }
        if (value instanceof ZonedDateTime zoned) {
            return zoned.withZoneSameInstant(LOCAL_ZONE).toLocalDateTime();
        }
        if (value instanceof Instant instant) {
            return LocalDateTime.ofInstant(instant, LOCAL_ZONE);
        }
        if (value instanceof java.sql.Timestamp timestamp) {
            return timestamp.toLocalDateTime();
        }
        if (value instanceof java.util.Date date) {
            return LocalDateTime.ofInstant(date.toInstant(), LOCAL_ZONE);
        }
        if (value instanceof LocalDate date) {
            return date.atStartOfDay();
        }
        return null;
    }

    public static String nowText() {
        return LocalDateTime.now().format(DATE_TIME_FORMAT);
    }

    // ============================================================
    // 事件构造与校验
    // ============================================================

    public static Map<String, Object> buildEvent(
            String eventType,
            String originSite,
            String originRecordId,
            Object studentNo,
            Object className,
            Object courseDate,
            Object period,
            Object attendanceStatus,
            Object signTime,
            Object courseName,
            Object timeSlot,
            Object studentName,
            Object deviceId,
            Object ip,
            Object location,
            Object isScript,
            Object taskStartTime,
            Object taskEndTime,
            Object originTaskId) {

        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("student_no", normalizeText(studentNo));
        payload.put("student_name", normalizeText(studentName));
        payload.put("class_name", normalizeText(className));
        payload.put("course_name", normalizeText(courseName));
        payload.put("course_date", normalizeDate(courseDate));

        String normalizedPeriod = normalizePeriod(period);
        if (normalizedPeriod.isEmpty()) {
            normalizedPeriod = normalizePeriod(timeSlot);
        }
        payload.put("period", normalizedPeriod);
        payload.put("time_slot", normalizeTimeSlot(timeSlot));
        payload.put("attendance_status", normalizeAttendanceStatus(attendanceStatus));
        payload.put("sign_time", toIso(signTime));
        payload.put("device_id", emptyToNull(normalizeText(deviceId)));
        payload.put("ip", emptyToNull(normalizeText(ip)));
        payload.put("location", emptyToNull(normalizeText(location)));
        payload.put("is_script", toInt(isScript));
        payload.put("task_start_time", toIso(taskStartTime));
        payload.put("task_end_time", toIso(taskEndTime));
        payload.put("server_time", toIso(LocalDateTime.now()));

        Map<String, Object> event = new LinkedHashMap<>();
        event.put("schema_version", SCHEMA_VERSION);
        event.put("event_id", UUID.randomUUID().toString());
        event.put("event_type", eventType);
        event.put("origin_site", normalizeText(originSite));
        event.put("origin_record_id", String.valueOf(originRecordId));
        event.put("origin_task_id", originTaskId == null ? null : String.valueOf(originTaskId));
        event.put("occurred_at", toIso(LocalDateTime.now()));
        event.put("align_key", alignKeyOfPayload(payload));
        event.put("payload", payload);
        return event;
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

    public static ValidationResult validateEvent(Map<String, Object> event) {
        if (event == null) {
            return new ValidationResult(false, "事件格式不是对象");
        }

        for (String field : List.of("event_type", "origin_site", "origin_record_id")) {
            if (normalizeText(event.get(field)).isEmpty()) {
                return new ValidationResult(false, "缺少必填字段 " + field);
            }
        }

        String eventType = normalizeText(event.get("event_type"));
        if (!EVENT_TYPES.contains(eventType)) {
            return new ValidationResult(false, "不支持的事件类型 " + eventType);
        }

        Object payloadObject = event.get("payload");
        if (!(payloadObject instanceof Map<?, ?> payload)) {
            return new ValidationResult(false, "缺少 payload");
        }

        for (String field : List.of("student_no", "class_name", "course_date", "sign_time")) {
            if (normalizeText(payload.get(field)).isEmpty()) {
                return new ValidationResult(false, "payload 缺少必填字段 " + field);
            }
        }

        if (toDbDateTime(payload.get("sign_time")) == null) {
            return new ValidationResult(false, "sign_time 无法解析");
        }
        if (normalizeDate(payload.get("course_date")).isEmpty()) {
            return new ValidationResult(false, "course_date 无法解析");
        }

        Object period = payload.get("period");
        if (normalizePeriod(period).isEmpty()) {
            period = payload.get("time_slot");
        }
        if (normalizePeriod(period).isEmpty()) {
            return new ValidationResult(false, "payload 的 period / time_slot 无法识别时段档");
        }

        Object status = payload.get("attendance_status");
        if (status != null && normalizeAttendanceStatus(status) == null) {
            return new ValidationResult(false, "attendance_status 取值非法");
        }

        return new ValidationResult(true, null);
    }
}
