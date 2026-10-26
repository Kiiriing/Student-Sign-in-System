package com.stu.signin.student;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.stu.signin.common.Api;
import com.stu.signin.common.ApiException;
import com.stu.signin.common.DbValues;
import com.stu.signin.common.RequestUtils;
import com.stu.signin.logging.CrawlerDetector;
import com.stu.signin.persistence.DbWriteTracker;
import com.stu.signin.sync.SyncConfig;
import com.stu.signin.sync.SyncContract;
import com.stu.signin.sync.SyncStore;
import com.stu.signin.sync.SyncWorker;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.support.TransactionTemplate;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.regex.Pattern;

/**
 * 学生端业务，对应 Python api/student.py。
 *
 * 4 个接口：今日课程、签到、签到记录、班级签到情况。
 * 查询统一改成批量 SQL，避免课程 / 学生循环里的 N+1 往返。
 */
@Service
public class StudentService {

    private static final Logger log = LoggerFactory.getLogger(StudentService.class);

    private static final DateTimeFormatter DATE_FORMAT = DateTimeFormatter.ofPattern("yyyy-MM-dd");

    private static final Map<Integer, String> STATUS_MAP = Map.of(
            1, "正常",
            2, "迟到",
            3, "缺勤",
            4, "早退",
            5, "病假",
            6, "事假");

    private static final Map<Integer, String> CLASS_STATUS_MAP = Map.of(
            1, "正常",
            2, "迟到",
            3, "旷课",
            4, "早退",
            5, "病假",
            6, "事假",
            7, "未签到");

    private static final Pattern SCRIPT_UA_PATTERNS = Pattern.compile(
            "python-requests|python-urllib|scrapy|curl|wget|postman|insomnia|"
                    + "httpclient|okhttp|java/|go-http-client|node-fetch|axios|bot|"
                    + "spider|crawler|scraper|headless|selenium|phantomjs|puppeteer|"
                    + "playwright|aiohttp|httpx|mechanize|googlehttpclient|webdriver",
            Pattern.CASE_INSENSITIVE);

    private static final Pattern SCRIPT_BODY_PATTERNS = Pattern.compile(
            "scraper|spider|crawler|selenium|puppeteer|playwright|headless|"
                    + "phantomjs|mechanize|scrapy|aiohttp|httpx|webdriver",
            Pattern.CASE_INSENSITIVE);

    private static final Pattern BROWSER_UA_REGEX = Pattern.compile(
            "Mozilla|Chrome|Safari|Edge|Firefox|OPR|Opera|MSIE|Trident",
            Pattern.CASE_INSENSITIVE);

    private static final String[] BROWSER_CORE_HEADERS = {"Accept", "Accept-Language", "Accept-Encoding"};

    private final JdbcTemplate jdbc;
    private final SyncStore store;
    private final SyncConfig config;
    private final SyncWorker worker;
    private final CrawlerDetector crawlerDetector;
    private final DbWriteTracker tracker;
    private final ObjectMapper mapper;
    private final TransactionTemplate transactionTemplate;

    public StudentService(JdbcTemplate jdbc, SyncStore store, SyncConfig config, SyncWorker worker,
                          CrawlerDetector crawlerDetector, DbWriteTracker tracker, ObjectMapper mapper,
                          TransactionTemplate transactionTemplate) {
        this.jdbc = jdbc;
        this.store = store;
        this.config = config;
        this.worker = worker;
        this.crawlerDetector = crawlerDetector;
        this.tracker = tracker;
        this.mapper = mapper;
        this.transactionTemplate = transactionTemplate;
    }

    // ============================================================
    // 工具
    // ============================================================

    private static String str(Object value) {
        return value == null ? "" : String.valueOf(value);
    }

    private static boolean truthy(Object value) {
        if (value == null) {
            return false;
        }
        if (value instanceof Number number) {
            return number.doubleValue() != 0;
        }
        if (value instanceof Boolean bool) {
            return bool;
        }
        return !String.valueOf(value).isBlank();
    }

    private Map<String, Object> queryStudent(String userId) {
        List<Map<String, Object>> rows = jdbc.queryForList("""
                SELECT s.id AS student_id, s.student_no, s.name AS student_name,
                       s.class_id, c.name AS class_name
                FROM students s
                LEFT JOIN classes c ON c.id = s.class_id
                WHERE s.user_id = ?
                LIMIT 1
                """, userId);
        return rows.isEmpty() ? null : rows.get(0);
    }

    private static Map<String, Object> statusSummary() {
        Map<String, Object> summary = new LinkedHashMap<>();
        summary.put("normal", 0);
        summary.put("late", 0);
        summary.put("absent", 0);
        summary.put("early", 0);
        summary.put("sick", 0);
        summary.put("leave", 0);
        summary.put("unsigned", 0);
        summary.put("script", 0);
        summary.put("cross", 0);
        return summary;
    }

    private static void bump(Map<String, Object> summary, String key) {
        summary.put(key, DbValues.intValue(summary.get(key)) + 1);
    }

    // ============================================================
    // 1. 获取学生课程
    // ============================================================

    public Map<String, Object> courses(String userId) {
        Map<String, Object> student = queryStudent(userId);
        if (student == null) {
            throw new ApiException(404, "学生信息不存在");
        }

        List<Map<String, Object>> courses = jdbc.queryForList("""
                SELECT c.id, c.name, c.course_date AS date, c.time, c.teacher_id,
                       t.name AS teacher_name
                FROM courses c
                LEFT JOIN teachers t ON t.id = c.teacher_id
                WHERE c.class_id = ? AND c.course_date = CURDATE()
                ORDER BY c.time ASC
                """, student.get("class_id"));

        String today = LocalDate.now().format(DATE_FORMAT);

        Map<String, String> taskMap = new LinkedHashMap<>();
        Set<String> signedTaskIds = new LinkedHashSet<>();

        if (!courses.isEmpty()) {
            List<Object> courseIds = new ArrayList<>();
            for (Map<String, Object> course : courses) {
                courseIds.add(course.get("id"));
            }

            String placeholders = String.join(",", java.util.Collections.nCopies(courseIds.size(), "?"));
            for (Map<String, Object> row : jdbc.queryForList("""
                    SELECT at.course_id, at.id AS task_id
                    FROM attendance_task at
                    WHERE at.course_id IN (%s)
                      AND at.status = 1
                      AND NOW() BETWEEN at.start_time AND DATE_ADD(at.end_time, INTERVAL 10 MINUTE)
                    ORDER BY at.start_time ASC
                    """.formatted(placeholders), courseIds.toArray())) {
                taskMap.putIfAbsent(str(row.get("course_id")), str(row.get("task_id")));
            }

            if (!taskMap.isEmpty()) {
                List<Object> taskIds = new ArrayList<>(taskMap.values());
                String taskPlaceholders = String.join(",",
                        java.util.Collections.nCopies(taskIds.size(), "?"));

                List<Object> args = new ArrayList<>();
                args.add(student.get("student_id"));
                args.addAll(taskIds);

                for (Map<String, Object> row : jdbc.queryForList(
                        "SELECT DISTINCT task_id FROM attendance_record WHERE student_id = ? AND task_id IN (%s)"
                                .formatted(taskPlaceholders), args.toArray())) {
                    signedTaskIds.add(str(row.get("task_id")));
                }
            }
        }

        Map<String, SyncStore.CrossSign> crossMap;
        try {
            crossMap = store.crossSignsForStudent(str(student.get("student_no")), today);
        } catch (Exception e) {
            crossMap = Map.of();
            log.warn("跨站同步读取异地签到失败（忽略）：{}", e.getMessage());
        }

        List<Map<String, Object>> items = new ArrayList<>();

        for (Map<String, Object> course : courses) {
            String courseDate = DbValues.date(course.get("date"));
            if (courseDate == null) {
                courseDate = today;
            }

            String taskId = taskMap.get(str(course.get("id")));
            String alignKey = SyncContract.buildAlignKey(
                    student.get("student_no"),
                    student.get("class_name"),
                    courseDate,
                    SyncContract.normalizePeriod(course.get("time")));
            SyncStore.CrossSign cross = crossMap.get(alignKey);

            Map<String, Object> item = new LinkedHashMap<>();
            item.put("id", course.get("id"));
            item.put("name", DbValues.text(course.get("name")));
            item.put("date", courseDate);
            item.put("time", DbValues.text(course.get("time")));
            item.put("teacher_id", course.get("teacher_id"));
            item.put("teacher_name", DbValues.text(course.get("teacher_name")));
            item.put("signed", taskId != null && signedTaskIds.contains(taskId));
            item.put("task_id", taskId);
            item.put("has_active_task", taskId != null);
            item.put("cross_signed", cross != null);
            item.put("cross_source_site", cross == null ? null : cross.originSite());
            item.put("cross_source_site_name",
                    cross == null ? null : config.siteNameOf(cross.originSite()));
            item.put("cross_sign_time", cross == null ? null : DbValues.dateTime(cross.signTime()));
            items.add(item);
        }

        Map<String, Object> data = new LinkedHashMap<>();
        data.put("student_id", str(student.get("student_id")));
        data.put("student_no", DbValues.text(student.get("student_no")));
        data.put("student_name", DbValues.text(student.get("student_name")));
        data.put("class_name", DbValues.text(student.get("class_name")));
        data.put("courses", items);

        return Api.body("code", 200, "message", "获取课程成功", "data", data);
    }

    // ============================================================
    // 2. 学生签到
    // ============================================================

    public Map<String, Object> signin(String userId, Map<String, Object> body, HttpServletRequest request) {
        Map<String, Object> data = body == null ? Map.of() : body;

        Object courseId = data.get("course_id");
        String deviceId = str(data.get("device_id")).trim();
        String location = str(data.get("location")).trim();

        if (!truthy(courseId)) {
            throw new ApiException(400, "课程ID不能为空");
        }
        if (deviceId.isEmpty()) {
            throw new ApiException(400, "设备标识不能为空");
        }

        String ip = RequestUtils.clientIp(request);

        Map<String, Object> result;
        try {
            result = transactionTemplate.execute(status ->
                    doSignin(userId, courseId, deviceId, location, ip, data, request));
        } catch (ApiException e) {
            throw e;
        } catch (Exception e) {
            log.error("学生签到失败", e);
            throw new ApiException(500, "签到失败", String.valueOf(e.getMessage()));
        }

        if (result == null) {
            throw new ApiException(500, "签到失败");
        }

        String message = str(result.remove("message"));
        @SuppressWarnings("unchecked")
        List<Object> eventArgs = (List<Object>) result.remove("_event_args");

        // 跨站同步：本地记录已提交后再入队并唤醒同步线程，失败不影响签到结果
        try {
            Map<String, Object> event = store.buildLocalSigninEvent(
                    str(eventArgs.get(0)), str(eventArgs.get(1)),
                    eventArgs.get(2), eventArgs.get(3), eventArgs.get(4),
                    eventArgs.get(5), str(eventArgs.get(6)), eventArgs.get(7),
                    eventArgs.get(8), eventArgs.get(9), eventArgs.get(10),
                    eventArgs.get(11), eventArgs.get(12), eventArgs.get(13),
                    eventArgs.get(14), eventArgs.get(15), eventArgs.get(16));
            store.enqueueEventToPeers(event);
            worker.triggerSync();
        } catch (Exception e) {
            log.warn("跨站同步出站入队失败（不影响本站签到）：{}", e.getMessage());
        }

        return Api.body("code", 200, "message", message, "data", result);
    }

    private Map<String, Object> doSignin(String userId, Object courseId, String deviceId, String location,
                                         String ip, Map<String, Object> body, HttpServletRequest request) {

        Map<String, Object> student = queryStudent(userId);
        if (student == null) {
            throw new ApiException(404, "学生信息不存在");
        }

        List<Map<String, Object>> courseRows = jdbc.queryForList("""
                SELECT id, name, class_id, course_date, time
                FROM courses
                WHERE id = ? AND class_id = ?
                LIMIT 1
                """, courseId, student.get("class_id"));

        if (courseRows.isEmpty()) {
            throw new ApiException(404, "课程不存在或不属于你的班级");
        }
        Map<String, Object> course = courseRows.get(0);

        List<Map<String, Object>> taskRows = jdbc.queryForList("""
                SELECT id, course_id, start_time, end_time, status
                FROM attendance_task
                WHERE course_id = ?
                  AND status = 1
                  AND NOW() BETWEEN start_time AND DATE_ADD(end_time, INTERVAL 10 MINUTE)
                ORDER BY start_time DESC
                LIMIT 1
                """, courseId);
        if (taskRows.isEmpty()) {
            throw new ApiException(400, "当前没有正在进行的签到");
        }
        Map<String, Object> task = taskRows.get(0);
        Object taskId = task.get("id");

        List<Map<String, Object>> duplicateRows = jdbc.queryForList("""
                SELECT id, status, sign_time
                FROM attendance_record
                WHERE task_id = ? AND student_id = ?
                LIMIT 1
                """, taskId, student.get("student_id"));
        if (!duplicateRows.isEmpty()) {
            Map<String, Object> duplicate = duplicateRows.get(0);
            Map<String, Object> extra = new LinkedHashMap<>();
            extra.put("status", duplicate.get("status"));
            extra.put("sign_time", DbValues.dateTime(duplicate.get("sign_time")));
            throw new ApiExceptionData(400, "你已经签到过了", extra);
        }

        String alignKey = SyncContract.buildAlignKey(
                student.get("student_no"),
                student.get("class_name"),
                course.get("course_date"),
                SyncContract.normalizePeriod(course.get("time")));

        // 第二道：本站已同步回来的异地记录
        Map<String, Object> crossHit;
        try {
            crossHit = store.findCrossDuplicate(str(student.get("student_no")), alignKey);
        } catch (Exception e) {
            crossHit = null;
            log.warn("跨站同步本地异地记录查重失败（放行）：{}", e.getMessage());
        }

        if (crossHit != null) {
            Map<String, Object> extra = new LinkedHashMap<>();
            extra.put("source_site", DbValues.text(crossHit.get("origin_site")));
            extra.put("source_site_name", config.siteNameOf(DbValues.text(crossHit.get("origin_site"))));
            extra.put("sign_time", DbValues.dateTime(crossHit.get("sign_time")));
            extra.put("course_name", DbValues.text(crossHit.get("course_name")));
            throw new ApiExceptionData(400, "已在其他网站签到", extra);
        }

        // 第三道：实时询问其他站点（fail-open）
        SyncWorker.DuplicateCheck peerCheck;
        try {
            peerCheck = worker.checkDuplicateOnPeers(str(student.get("student_no")), alignKey);
        } catch (Exception e) {
            peerCheck = new SyncWorker.DuplicateCheck(null, List.of());
            log.warn("跨站同步实时跨站查重失败（放行）：{}", e.getMessage());
        }

        if (peerCheck.warnings() != null && !peerCheck.warnings().isEmpty()) {
            log.warn("跨站同步实时查重告警：{}", String.join("；", peerCheck.warnings()));
        }

        if (peerCheck.hit() != null) {
            Map<String, Object> hit = peerCheck.hit();
            Map<String, Object> extra = new LinkedHashMap<>();
            extra.put("source_site", hit.get("source_site"));
            extra.put("source_site_name", config.siteNameOf(DbValues.text(hit.get("source_site"))));
            extra.put("sign_time", hit.get("sign_time"));
            extra.put("course_name", hit.get("course_name"));
            throw new ApiExceptionData(400, "已在其他网站签到", extra);
        }

        // 防止同一个设备给不同学生签到
        List<Map<String, Object>> deviceRows = jdbc.queryForList("""
                SELECT id, student_id
                FROM attendance_record
                WHERE task_id = ? AND device_id = ?
                LIMIT 1
                """, taskId, deviceId);

        if (!deviceRows.isEmpty()
                && !str(deviceRows.get(0).get("student_id")).equals(str(student.get("student_id")))) {
            throw new ApiException(403, "该设备已经为其他学生完成本次签到");
        }

        // 迟到判定
        List<Map<String, Object>> statusRows = jdbc.queryForList("""
                SELECT CASE WHEN NOW() <= end_time THEN 1 ELSE 2 END AS attendance_status
                FROM attendance_task
                WHERE id = ?
                LIMIT 1
                """, taskId);

        int attendanceStatus = statusRows.isEmpty() ? 1
                : DbValues.intValue(statusRows.get(0).get("attendance_status"));

        int isScript = isScriptSigninRequest(request, body) ? 1 : 0;

        String recordId = UUID.randomUUID().toString();

        jdbc.update("""
                INSERT INTO attendance_record
                (id, task_id, student_id, status, sign_time, ip, device_id, location, is_script)
                VALUES (?, ?, ?, ?, NOW(), ?, ?, ?, ?)
                """, recordId, taskId, student.get("student_id"), attendanceStatus,
                ip, deviceId, location, isScript);
        tracker.mark();

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("record_id", recordId);
        result.put("course_id", courseId);
        result.put("course_name", DbValues.text(course.get("name")));
        result.put("status", attendanceStatus);
        result.put("is_script", isScript);
        result.put("status_text", isScript == 1 ? "脚本签到" : (attendanceStatus == 1 ? "正常" : "迟到"));
        result.put("message", attendanceStatus == 1 ? "签到成功" : "签到成功，但已迟到");

        // 事务提交后再入队、唤醒同步线程（由 signin 外层处理）
        result.put("_event_args", java.util.Arrays.asList(
                recordId, taskId, student.get("student_no"), student.get("student_name"),
                student.get("class_name"), course.get("course_date"),
                SyncContract.normalizePeriod(course.get("time")), attendanceStatus,
                LocalDateTime.now(), course.get("name"), course.get("time"),
                deviceId, ip, location, isScript,
                task.get("start_time"), task.get("end_time")));

        return result;
    }

    /** 事务内抛出、带 data 字段的业务异常 */
    public static class ApiExceptionData extends ApiException {
        private final Map<String, Object> data;

        public ApiExceptionData(int status, String message, Map<String, Object> data) {
            super(status, message);
            this.data = data;
        }

        public Map<String, Object> getData() {
            return data;
        }
    }

    // ============================================================
    // 3. 获取签到记录
    // ============================================================

    public List<Map<String, Object>> records(String userId, String dateFilter) {
        List<Map<String, Object>> studentRows = jdbc.queryForList(
                "SELECT student_no FROM students WHERE user_id = ? LIMIT 1", userId);
        String studentNo = studentRows.isEmpty() ? null : DbValues.text(studentRows.get(0).get("student_no"));

        String sql = """
                SELECT ar.id, ar.status, ar.sign_time, ar.ip, ar.device_id, ar.location,
                       ar.create_time, ar.is_script,
                       at.id AS task_id, at.start_time, at.end_time,
                       c.id AS course_id, c.name AS course_name,
                       t.name AS teacher_name
                FROM attendance_record ar
                INNER JOIN students s ON s.id = ar.student_id
                INNER JOIN attendance_task at ON at.id = ar.task_id
                INNER JOIN courses c ON c.id = at.course_id
                LEFT JOIN teachers t ON t.id = c.teacher_id
                WHERE s.user_id = ?
                """;

        List<Object> args = new ArrayList<>();
        args.add(userId);

        String dateText = dateFilter == null ? "" : dateFilter.trim();
        if (!dateText.isEmpty()) {
            sql += " AND DATE(ar.sign_time) = ?";
            args.add(dateText);
        }
        sql += " ORDER BY ar.sign_time DESC";

        List<Map<String, Object>> records = new ArrayList<>();

        for (Map<String, Object> row : jdbc.queryForList(sql, args.toArray())) {
            int isScript = DbValues.intValue(row.get("is_script"));

            Map<String, Object> record = new LinkedHashMap<>();
            record.put("id", row.get("id"));
            record.put("status", row.get("status"));
            record.put("sign_time", DbValues.dateTime(row.get("sign_time")));
            record.put("ip", DbValues.text(row.get("ip")));
            record.put("device_id", DbValues.text(row.get("device_id")));
            record.put("location", DbValues.text(row.get("location")));
            record.put("create_time", DbValues.dateTime(row.get("create_time")));
            record.put("is_script", isScript);
            record.put("task_id", row.get("task_id"));
            record.put("start_time", DbValues.dateTime(row.get("start_time")));
            record.put("end_time", DbValues.dateTime(row.get("end_time")));
            record.put("course_id", row.get("course_id"));
            record.put("course_name", DbValues.text(row.get("course_name")));
            record.put("teacher_name", DbValues.text(row.get("teacher_name")));
            record.put("status_text", isScript == 1 ? "脚本签到"
                    : STATUS_MAP.getOrDefault(DbValues.nullableInt(row.get("status")), "未知"));
            record.put("source_site", config.siteCode());
            record.put("source_site_name", config.siteName());
            record.put("is_cross", 0);
            records.add(record);
        }

        // 并入本站同步回来的异地签到
        List<Map<String, Object>> crossRecords = new ArrayList<>();
        Map<String, List<Map<String, Object>>> teacherMap = new HashMap<>();

        try {
            crossRecords = store.crossRecordsForStudent(studentNo, dateText.isEmpty() ? null : dateText);

            Set<String> crossDates = new LinkedHashSet<>();
            for (Map<String, Object> row : crossRecords) {
                if (row.get("course_date") != null) {
                    crossDates.add(SyncContract.normalizeDate(row.get("course_date")));
                }
            }

            if (!crossDates.isEmpty()) {
                String placeholders = String.join(",",
                        java.util.Collections.nCopies(crossDates.size(), "?"));
                for (Map<String, Object> candidate : jdbc.queryForList("""
                        SELECT c.name AS course_name, c.course_date, c.time AS course_time,
                               cl.name AS class_name, t.name AS teacher_name
                        FROM courses c
                        LEFT JOIN classes cl ON cl.id = c.class_id
                        LEFT JOIN teachers t ON t.id = c.teacher_id
                        WHERE c.course_date IN (%s)
                        """.formatted(placeholders), crossDates.toArray())) {

                    String key = SyncContract.normalizeClassKey(candidate.get("class_name")) + "|"
                            + SyncContract.normalizeDate(candidate.get("course_date")) + "|"
                            + SyncContract.normalizePeriod(candidate.get("course_time"));
                    teacherMap.computeIfAbsent(key, k -> new ArrayList<>()).add(candidate);
                }
            }
        } catch (Exception e) {
            crossRecords = new ArrayList<>();
            teacherMap = new HashMap<>();
            log.warn("跨站同步读取异地签到明细失败（忽略）：{}", e.getMessage());
        }

        for (Map<String, Object> row : crossRecords) {
            Integer status = DbValues.nullableInt(row.get("attendance_status"));

            String key = SyncContract.normalizeClassKey(row.get("class_name")) + "|"
                    + SyncContract.normalizeDate(row.get("course_date")) + "|"
                    + SyncContract.normalizePeriod(row.get("period") != null
                    && !str(row.get("period")).isEmpty() ? row.get("period") : row.get("time_slot"));

            String teacherName = null;
            List<Map<String, Object>> candidates = teacherMap.getOrDefault(key, List.of());

            for (Map<String, Object> candidate : candidates) {
                String candidateTeacher = DbValues.text(candidate.get("teacher_name"));
                if (candidateTeacher != null && !candidateTeacher.isEmpty()
                        && (row.get("course_name") == null
                        || DbValues.text(candidate.get("course_name"))
                        .equals(DbValues.text(row.get("course_name"))))) {
                    teacherName = candidateTeacher;
                    break;
                }
            }
            if (teacherName == null) {
                for (Map<String, Object> candidate : candidates) {
                    String candidateTeacher = DbValues.text(candidate.get("teacher_name"));
                    if (candidateTeacher != null && !candidateTeacher.isEmpty()) {
                        teacherName = candidateTeacher;
                        break;
                    }
                }
            }

            int isScript = DbValues.intValue(row.get("is_script"));

            Map<String, Object> record = new LinkedHashMap<>();
            record.put("id", row.get("id"));
            record.put("status", status);
            record.put("sign_time", DbValues.dateTime(row.get("sign_time")));
            record.put("ip", DbValues.text(row.get("ip")));
            record.put("device_id", DbValues.text(row.get("device_id")));
            record.put("location", DbValues.text(row.get("location")));
            record.put("create_time", null);
            record.put("is_script", isScript);
            record.put("task_id", null);
            record.put("start_time", null);
            record.put("end_time", null);
            record.put("course_id", null);
            record.put("course_name", DbValues.text(row.get("course_name")));
            record.put("teacher_name", teacherName);
            record.put("status_text", isScript == 1 ? "脚本签到" : STATUS_MAP.getOrDefault(status, "未知"));
            record.put("source_site", DbValues.text(row.get("origin_site")));
            record.put("source_site_name", config.siteNameOf(DbValues.text(row.get("origin_site"))));
            record.put("is_cross", 1);

            // 异地行额外保留的原始字段（与 Python 版保持一致）
            record.put("origin_site", DbValues.text(row.get("origin_site")));
            record.put("class_name", DbValues.text(row.get("class_name")));
            record.put("course_date", DbValues.date(row.get("course_date")));
            record.put("period", DbValues.text(row.get("period")));
            record.put("time_slot", DbValues.text(row.get("time_slot")));
            record.put("attendance_status", status);

            records.add(record);
        }

        records.sort(Comparator.comparing(
                (Map<String, Object> record) -> DbValues.localDateTime(record.get("sign_time")),
                Comparator.nullsLast(Comparator.reverseOrder())));

        return records;
    }

    // ============================================================
    // 4. 获取班级签到情况
    // ============================================================

    public Map<String, Object> classAttendance(String userId, String dateArg) {
        Map<String, Object> student = queryStudent(userId);
        if (student == null) {
            throw new ApiException(404, "学生信息不存在");
        }

        Object classId = student.get("class_id");
        if (!truthy(classId)) {
            throw new ApiException(400, "未分配班级");
        }

        String dateStr;
        if (dateArg != null && !dateArg.trim().isEmpty()) {
            try {
                dateStr = LocalDate.parse(dateArg.trim(), DATE_FORMAT).format(DATE_FORMAT);
            } catch (Exception e) {
                throw new ApiException(400, "日期格式错误，应为 YYYY-MM-DD");
            }
        } else {
            dateStr = LocalDate.now().format(DATE_FORMAT);
        }

        List<Map<String, Object>> courseRows = jdbc.queryForList("""
                SELECT c.id AS course_id, c.name AS course_name, c.time,
                       t.name AS teacher_name,
                       at.id AS task_id, at.start_time, at.end_time, at.status AS task_status
                FROM courses c
                LEFT JOIN teachers t ON t.id = c.teacher_id
                LEFT JOIN attendance_task at ON at.course_id = c.id AND DATE(at.start_time) = ?
                WHERE c.class_id = ? AND c.course_date = ?
                ORDER BY c.time ASC
                """, dateStr, classId, dateStr);

        List<Map<String, Object>> coursesList = new ArrayList<>();
        List<Object> taskIds = new ArrayList<>();

        for (Map<String, Object> row : courseRows) {
            Object taskId = row.get("task_id");
            String taskIdText = null;
            if (truthy(taskId)) {
                taskIds.add(taskId);
                taskIdText = str(taskId);
            }

            Map<String, Object> item = new LinkedHashMap<>();
            item.put("course_id", str(row.get("course_id")));
            item.put("course_name", DbValues.text(row.get("course_name")));
            item.put("time", DbValues.text(row.get("time")));
            item.put("teacher_name", DbValues.text(row.get("teacher_name")));
            item.put("task_id", taskIdText);
            item.put("start_time", DbValues.isoDateTime(row.get("start_time")));
            item.put("end_time", DbValues.isoDateTime(row.get("end_time")));
            item.put("task_status", row.get("task_status"));
            coursesList.add(item);
        }

        List<Map<String, Object>> studentsList = jdbc.queryForList("""
                SELECT id, student_no, name
                FROM students
                WHERE class_id = ?
                ORDER BY student_no ASC
                """, classId);

        Map<String, Map<String, Object>> recordsMap = new HashMap<>();
        if (!taskIds.isEmpty()) {
            String placeholders = String.join(",",
                    java.util.Collections.nCopies(taskIds.size(), "?"));
            for (Map<String, Object> row : jdbc.queryForList(
                    "SELECT student_id, task_id, status, sign_time, is_script FROM attendance_record WHERE task_id IN (%s)"
                            .formatted(placeholders), taskIds.toArray())) {
                recordsMap.put(str(row.get("student_id")) + "|" + str(row.get("task_id")), row);
            }
        }

        Map<String, SyncStore.CrossSign> crossMap;
        try {
            crossMap = store.crossSignsForCourse(dateStr);
        } catch (Exception e) {
            crossMap = Map.of();
            log.warn("获取班级异地签到失败：{}", e.getMessage());
        }

        List<Map<String, Object>> roster = new ArrayList<>();
        LocalDateTime now = LocalDateTime.now();

        for (Map<String, Object> s : studentsList) {
            Map<String, Object> rowStatus = new LinkedHashMap<>();
            Map<String, Object> summary = statusSummary();

            for (Map<String, Object> c : coursesList) {
                String taskId = (String) c.get("task_id");
                Map<String, Object> record = taskId == null ? null
                        : recordsMap.get(str(s.get("id")) + "|" + taskId);

                Integer status = null;
                String statusText = "无任务";
                String signTime = null;
                int isScript = 0;
                int isCross = 0;
                String sourceSite = config.siteCode();
                String sourceSiteName = config.siteName();
                String crossSignTime = null;

                if (taskId != null) {
                    if (record != null) {
                        status = DbValues.nullableInt(record.get("status"));
                        signTime = DbValues.isoDateTime(record.get("sign_time"));
                        isScript = DbValues.intValue(record.get("is_script"));
                        statusText = isScript == 1 ? "脚本签到"
                                : CLASS_STATUS_MAP.getOrDefault(status, "未知");
                    } else {
                        SyncStore.CrossSign cross = crossMap.get(SyncContract.buildAlignKey(
                                s.get("student_no"), student.get("class_name"),
                                dateStr, SyncContract.normalizePeriod(c.get("time"))));

                        if (cross != null) {
                            int crossStatus = cross.attendanceStatus() == null ? 1 : cross.attendanceStatus();
                            if (crossStatus < 1 || crossStatus > 6) {
                                crossStatus = 1;
                            }
                            status = crossStatus;
                            isCross = 1;
                            sourceSite = cross.originSite();
                            sourceSiteName = config.siteNameOf(cross.originSite());
                            crossSignTime = DbValues.isoDateTime(cross.signTime());
                            signTime = crossSignTime;
                            statusText = "已在其他网站签到";
                        } else {
                            boolean inWindow;
                            try {
                                LocalDateTime tStart = DbValues.localDateTime(c.get("start_time"));
                                LocalDateTime tEnd = DbValues.localDateTime(c.get("end_time"));
                                inWindow = tStart != null && tEnd != null
                                        && !now.isBefore(tStart) && !now.isAfter(tEnd.plusMinutes(10));
                            } catch (Exception e) {
                                inWindow = false;
                            }
                            status = inWindow ? 7 : 3;
                            statusText = CLASS_STATUS_MAP.getOrDefault(status, "未知");
                        }
                    }

                    if (isScript == 1) {
                        bump(summary, "script");
                    } else if (status == 1) {
                        bump(summary, "normal");
                    } else if (status == 2) {
                        bump(summary, "late");
                    } else if (status == 3) {
                        bump(summary, "absent");
                    } else if (status == 4) {
                        bump(summary, "early");
                    } else if (status == 5) {
                        bump(summary, "sick");
                    } else if (status == 6) {
                        bump(summary, "leave");
                    } else if (status == 7) {
                        bump(summary, "unsigned");
                    }

                    if (isCross == 1) {
                        bump(summary, "cross");
                    }
                }

                Map<String, Object> cell = new LinkedHashMap<>();
                cell.put("task_id", taskId);
                cell.put("status", status);
                cell.put("status_text", statusText);
                cell.put("sign_time", signTime);
                cell.put("is_script", isScript);
                cell.put("is_cross", isCross);
                cell.put("source_site", sourceSite);
                cell.put("source_site_name", sourceSiteName);
                cell.put("cross_sign_time", crossSignTime);

                rowStatus.put(str(c.get("course_id")), cell);
            }

            Map<String, Object> item = new LinkedHashMap<>();
            item.put("student_id", str(s.get("id")));
            item.put("student_no", DbValues.text(s.get("student_no")));
            item.put("student_name", DbValues.text(s.get("name")));
            item.put("is_me", str(s.get("id")).equals(str(student.get("student_id"))));
            item.put("row_status", rowStatus);
            item.put("summary", summary);
            roster.add(item);
        }

        Map<String, Object> data = new LinkedHashMap<>();
        data.put("date", dateStr);
        data.put("class_name", DbValues.text(student.get("class_name")));
        data.put("courses", coursesList);
        data.put("roster", roster);

        return Api.body("code", 200, "message", "获取班级签到情况成功", "data", data);
    }

    // ============================================================
    // 脚本签到检测
    // ============================================================

    private boolean isScriptSigninRequest(HttpServletRequest request, Map<String, Object> body) {
        String ua = request.getHeader("User-Agent");
        if (ua == null) {
            ua = "";
        }

        // 1. UA 命中爬虫 / 自动化工具关键字
        if (!ua.isEmpty() && SCRIPT_UA_PATTERNS.matcher(ua).find()) {
            return true;
        }

        // 2. 请求体泄露脚本特征
        String bodyText = "";
        try {
            bodyText = mapper.writeValueAsString(body == null ? Map.of() : body);
        } catch (Exception ignored) {
            bodyText = "";
        }
        if (!bodyText.isEmpty() && SCRIPT_BODY_PATTERNS.matcher(bodyText).find()) {
            return true;
        }

        // 3. 同 IP 此前已被标记为爬虫会话
        if (crawlerDetector.isCrawlerSession(RequestUtils.clientIp(request))) {
            return true;
        }

        // 4. 缺少浏览器核心请求头（仅在 UA 不像浏览器时检测）
        if (!BROWSER_UA_REGEX.matcher(ua).find()) {
            int missing = 0;
            for (String header : BROWSER_CORE_HEADERS) {
                if (request.getHeader(header) == null) {
                    missing++;
                }
            }
            if (missing >= 2) {
                return true;
            }
        }

        // 5. 前端浏览器指纹
        Object clientFp = body == null ? null : body.get("client_fp");
        return clientFp != null && !String.valueOf(clientFp).trim().isEmpty();
    }
}
