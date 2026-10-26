package com.stu.signin.common;

import java.math.BigDecimal;
import java.sql.Timestamp;
import java.time.Instant;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.OffsetDateTime;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * JDBC 查询结果的取值与时间格式化工具。
 *
 * MySQL Connector/J 对 DATE / DATETIME 可能返回 LocalDate / LocalDateTime /
 * Timestamp，这里统一收敛，避免每个接口各写一套判断。
 */
public final class DbValues {

    private static final DateTimeFormatter DATE_TIME = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
    private static final DateTimeFormatter ISO_DATE_TIME = DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss");
    private static final DateTimeFormatter DATE = DateTimeFormatter.ofPattern("yyyy-MM-dd");

    private DbValues() {
    }

    public static String text(Object value) {
        return value == null ? null : String.valueOf(value);
    }

    public static int intValue(Object value) {
        if (value instanceof Number number) {
            return number.intValue();
        }
        if (value == null || String.valueOf(value).isBlank()) {
            return 0;
        }
        return Integer.parseInt(String.valueOf(value).trim());
    }

    public static long longValue(Object value) {
        if (value instanceof Number number) {
            return number.longValue();
        }
        if (value == null || String.valueOf(value).isBlank()) {
            return 0L;
        }
        return Long.parseLong(String.valueOf(value).trim());
    }

    public static Integer nullableInt(Object value) {
        if (value instanceof Number number) {
            return number.intValue();
        }
        if (value == null || String.valueOf(value).isBlank()) {
            return null;
        }
        try {
            return Integer.parseInt(String.valueOf(value).trim());
        } catch (NumberFormatException e) {
            return null;
        }
    }

    /** 任意时间值 → yyyy-MM-dd HH:mm:ss */
    public static String dateTime(Object value) {
        LocalDateTime parsed = localDateTime(value);
        if (parsed != null) {
            return parsed.format(DATE_TIME);
        }
        return value == null ? null : String.valueOf(value);
    }

    /** 任意时间值 → yyyy-MM-dd'T'HH:mm:ss（对应 Python 的 datetime.isoformat() 常规写法） */
    public static String isoDateTime(Object value) {
        LocalDateTime parsed = localDateTime(value);
        if (parsed != null) {
            return parsed.format(ISO_DATE_TIME);
        }
        return value == null ? null : String.valueOf(value);
    }

    /** 任意日期值 → yyyy-MM-dd */
    public static String date(Object value) {
        LocalDate parsed = localDate(value);
        if (parsed != null) {
            return parsed.format(DATE);
        }
        return value == null ? null : String.valueOf(value);
    }

    public static LocalDateTime localDateTime(Object value) {
        if (value == null) {
            return null;
        }
        if (value instanceof LocalDateTime dateTime) {
            return dateTime;
        }
        if (value instanceof Timestamp timestamp) {
            return timestamp.toLocalDateTime();
        }
        if (value instanceof LocalDate date) {
            return date.atStartOfDay();
        }
        if (value instanceof OffsetDateTime offset) {
            return offset.atZoneSameInstant(ZoneId.systemDefault()).toLocalDateTime();
        }
        if (value instanceof ZonedDateTime zoned) {
            return zoned.withZoneSameInstant(ZoneId.systemDefault()).toLocalDateTime();
        }
        if (value instanceof Instant instant) {
            return LocalDateTime.ofInstant(instant, ZoneId.systemDefault());
        }
        // java.sql.Date.toInstant() 会抛 UnsupportedOperationException，必须先单独处理
        if (value instanceof java.sql.Date sqlDate) {
            return sqlDate.toLocalDate().atStartOfDay();
        }
        if (value instanceof java.util.Date date) {
            return LocalDateTime.ofInstant(date.toInstant(), ZoneId.systemDefault());
        }
        if (value instanceof String text && !text.isBlank()) {
            return com.stu.signin.sync.SyncContract.toDbDateTime(text);
        }
        return null;
    }

    public static LocalDate localDate(Object value) {
        if (value == null) {
            return null;
        }
        if (value instanceof LocalDate date) {
            return date;
        }
        if (value instanceof LocalDateTime dateTime) {
            return dateTime.toLocalDate();
        }
        if (value instanceof Timestamp timestamp) {
            return timestamp.toLocalDateTime().toLocalDate();
        }
        if (value instanceof java.sql.Date sqlDate) {
            return sqlDate.toLocalDate();
        }
        if (value instanceof java.util.Date date) {
            return date.toInstant().atZone(ZoneId.systemDefault()).toLocalDate();
        }
        if (value instanceof String text && !text.isBlank()) {
            String trimmed = text.trim();
            if (trimmed.length() >= 10) {
                try {
                    return LocalDate.parse(trimmed.substring(0, 10));
                } catch (Exception ignored) {
                    return null;
                }
            }
        }
        return null;
    }

    public static Map<String, Object> row(Object... keyValues) {
        Map<String, Object> map = new LinkedHashMap<>();
        for (int i = 0; i + 1 < keyValues.length; i += 2) {
            map.put(String.valueOf(keyValues[i]), keyValues[i + 1]);
        }
        return map;
    }

    public static BigDecimal decimal(Object value) {
        if (value instanceof BigDecimal decimal) {
            return decimal;
        }
        if (value instanceof Number number) {
            return BigDecimal.valueOf(number.longValue());
        }
        return value == null ? null : new BigDecimal(String.valueOf(value));
    }
}
