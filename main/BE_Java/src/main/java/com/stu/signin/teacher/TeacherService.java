package com.stu.signin.teacher;

import com.stu.signin.common.Api;
import com.stu.signin.common.ApiException;
import com.stu.signin.common.DbValues;
import com.stu.signin.persistence.DbWriteTracker;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import com.stu.signin.sync.SyncConfig;
import com.stu.signin.sync.SyncContract;
import com.stu.signin.sync.SyncStore;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * 教师端业务，对应 Python api/teacher.py。
 *
 * 8 个接口：课程、创建/关闭/删除签到任务、签到记录、任务列表、名册、改状态、统计。
 * 任务列表与统计用 SyncStore.taskStats 批量计算已到人数与状态分布，
 * 替代原先「每个任务各跑两条 SQL」的 N+1。
 */
@Service
public class TeacherService {

    private static final Logger log = LoggerFactory.getLogger(TeacherService.class);

    private static final Map<Integer, String> STATUS_MAP = Map.of(
            1, "正常",
            2, "迟到",
            3, "缺勤",
            4, "早退",
            5, "病假",
            6, "事假");

    private static final Map<Integer, String> ROSTER_STATUS_MAP = Map.of(
            1, "正常",
            2, "迟到",
            3, "旷课",
            4, "早退",
            5, "病假",
            6, "事假",
            7, "未签到");

    private final JdbcTemplate jdbc;
    private final SyncStore store;
    private final SyncConfig config;
    private final DbWriteTracker tracker;

    public TeacherService(JdbcTemplate jdbc, SyncStore store, SyncConfig config, DbWriteTracker tracker) {
        this.jdbc = jdbc;
        this.store = store;
        this.config = config;
        this.tracker = tracker;
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
        return !String.valueOf(value).isBlank();
    }

    private Object teacherId(String userId) {
        List<Map<String, Object>> rows = jdbc.queryForList(
                "SELECT id FROM teachers WHERE user_id = ? LIMIT 1", userId);
        return rows.isEmpty() ? null : rows.get(0).get("id");
    }

    private Object requireTeacherId(String userId) {
        Object id = teacherId(userId);
        if (id == null) {
            throw new ApiException(404, "教师信息不存在");
        }
        return id;
    }

    private boolean taskBelongsToTeacher(Object taskId, Object teacherId) {
        List<Map<String, Object>> rows = jdbc.queryForList("""
                SELECT at.id
                FROM attendance_task at
                INNER JOIN courses c ON c.id = at.course_id
                WHERE at.id = ? AND c.teacher_id = ?
                LIMIT 1
                """, taskId, teacherId);
        return !rows.isEmpty();
    }

    private static Integer statusAsInt(Object status) {
        if (status instanceof Number number) {
            return number.intValue();
        }
        try {
            return Integer.parseInt(String.valueOf(status).trim());
        } catch (Exception e) {
            return null;
        }
    }

    // ============================================================
    // 1. 获取教师课程
    // ============================================================

    public Map<String, Object> courses(String userId) {
        Object teacherId = requireTeacherId(userId);

        List<Map<String, Object>> items = new ArrayList<>();

        for (Map<String, Object> row : jdbc.queryForList("""
                SELECT c.id, c.name, c.course_date AS date, c.time, c.class_id,
                       cl.name AS class_name
                FROM courses c
                LEFT JOIN classes cl ON cl.id = c.class_id
                WHERE c.teacher_id = ?
                ORDER BY c.course_date DESC, c.time ASC
                """, teacherId)) {

            Map<String, Object> item = new LinkedHashMap<>();
            item.put("id", row.get("id"));
            item.put("name", DbValues.text(row.get("name")));
            item.put("date", DbValues.date(row.get("date")));
            item.put("time", DbValues.text(row.get("time")));
            item.put("class_id", row.get("class_id"));
            item.put("class_name", DbValues.text(row.get("class_name")));
            items.add(item);
        }

        return Api.body("code", 200, "message", "获取课程成功", "data", items);
    }

    // ============================================================
    // 2. 创建签到任务
    // ============================================================

    public Map<String, Object> createAttendance(String userId, Map<String, Object> body) {
        Map<String, Object> data = body == null ? Map.of() : body;

        Object courseId = data.get("course_id");
        Object startTime = data.get("start_time");
        Object endTime = data.get("end_time");

        if (!truthy(courseId)) {
            throw new ApiException(400, "课程ID不能为空");
        }
        if (!truthy(startTime)) {
            throw new ApiException(400, "签到开始时间不能为空");
        }
        if (!truthy(endTime)) {
            throw new ApiException(400, "签到结束时间不能为空");
        }

        Object teacherId = requireTeacherId(userId);

        List<Map<String, Object>> courseRows = jdbc.queryForList("""
                SELECT id, name, class_id
                FROM courses
                WHERE id = ? AND teacher_id = ?
                LIMIT 1
                """, courseId, teacherId);

        if (courseRows.isEmpty()) {
            throw new ApiException(403, "你没有权限操作该课程");
        }
        Map<String, Object> course = courseRows.get(0);

        if (str(startTime).compareTo(str(endTime)) >= 0) {
            throw new ApiException(400, "签到结束时间必须晚于开始时间");
        }

        String taskId = UUID.randomUUID().toString();

        jdbc.update("""
                INSERT INTO attendance_task (id, course_id, start_time, end_time, status)
                VALUES (?, ?, ?, ?, 1)
                """, taskId, courseId, startTime, endTime);
        tracker.mark();

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("id", taskId);
        result.put("course_id", courseId);
        result.put("course_name", DbValues.text(course.get("name")));
        result.put("start_time", startTime);
        result.put("end_time", endTime);
        result.put("status", 1);

        return Api.body("code", 200, "message", "签到任务创建成功", "data", result);
    }

    // ============================================================
    // 3. 关闭签到任务
    // ============================================================

    public Map<String, Object> closeAttendance(String userId, Map<String, Object> body) {
        Map<String, Object> data = body == null ? Map.of() : body;
        Object taskId = data.get("task_id");

        if (!truthy(taskId)) {
            throw new ApiException(400, "签到任务ID不能为空");
        }

        Object teacherId = requireTeacherId(userId);

        List<Map<String, Object>> taskRows = jdbc.queryForList("""
                SELECT at.id, at.status, c.name AS course_name
                FROM attendance_task at
                INNER JOIN courses c ON c.id = at.course_id
                WHERE at.id = ? AND c.teacher_id = ?
                LIMIT 1
                """, taskId, teacherId);

        if (taskRows.isEmpty()) {
            throw new ApiException(404, "签到任务不存在或无权限");
        }

        if (DbValues.intValue(taskRows.get(0).get("status")) == 0) {
            throw new ApiException(400, "签到任务已经关闭");
        }

        jdbc.update("UPDATE attendance_task SET status = 0 WHERE id = ?", taskId);
        tracker.mark();

        return Api.message(200, "签到任务已关闭");
    }

    // ============================================================
    // 4. 删除签到任务
    // ============================================================

    public Map<String, Object> deleteAttendance(String userId, Map<String, Object> body) {
        Map<String, Object> data = body == null ? Map.of() : body;
        Object taskId = data.get("task_id");

        if (!truthy(taskId)) {
            throw new ApiException(400, "签到任务ID不能为空");
        }

        Object teacherId = requireTeacherId(userId);

        if (!taskBelongsToTeacher(taskId, teacherId)) {
            throw new ApiException(404, "签到任务不存在或无权限");
        }

        jdbc.update("DELETE FROM attendance_task WHERE id = ?", taskId);
        tracker.mark();

        return Api.message(200, "签到任务已删除");
    }

    // ============================================================
    // 5. 查看签到记录
    // ============================================================

    public List<Map<String, Object>> records(String userId, String taskId) {
        Object teacherId = requireTeacherId(userId);

        String sql = """
                SELECT ar.id, ar.status, ar.sign_time, ar.ip, ar.device_id, ar.location,
                       ar.is_script,
                       s.id AS student_id, s.student_no, s.name AS student_name,
                       cl.name AS class_name,
                       c.id AS course_id, c.name AS course_name,
                       at.id AS task_id, at.start_time, at.end_time
                FROM attendance_record ar
                INNER JOIN students s ON s.id = ar.student_id
                LEFT JOIN classes cl ON cl.id = s.class_id
                INNER JOIN attendance_task at ON at.id = ar.task_id
                INNER JOIN courses c ON c.id = at.course_id
                """;

        List<Map<String, Object>> rows;
        if (taskId != null && !taskId.trim().isEmpty()) {
            rows = jdbc.queryForList(sql + """
                    WHERE at.id = ? AND c.teacher_id = ?
                    ORDER BY ar.sign_time DESC
                    """, taskId, teacherId);
        } else {
            rows = jdbc.queryForList(sql + """
                    WHERE c.teacher_id = ?
                    ORDER BY ar.sign_time DESC
                    """, teacherId);
        }

        List<Map<String, Object>> records = new ArrayList<>();
        for (Map<String, Object> row : rows) {
            int isScript = DbValues.intValue(row.get("is_script"));

            Map<String, Object> record = new LinkedHashMap<>();
            record.put("id", row.get("id"));
            record.put("status", row.get("status"));
            record.put("sign_time", DbValues.dateTime(row.get("sign_time")));
            record.put("ip", DbValues.text(row.get("ip")));
            record.put("device_id", DbValues.text(row.get("device_id")));
            record.put("location", DbValues.text(row.get("location")));
            record.put("is_script", isScript == 1 ? 1 : 0);
            record.put("student_id", row.get("student_id"));
            record.put("student_no", DbValues.text(row.get("student_no")));
            record.put("student_name", DbValues.text(row.get("student_name")));
            record.put("class_name", DbValues.text(row.get("class_name")));
            record.put("course_id", row.get("course_id"));
            record.put("course_name", DbValues.text(row.get("course_name")));
            record.put("task_id", row.get("task_id"));
            record.put("start_time", DbValues.dateTime(row.get("start_time")));
            record.put("end_time", DbValues.dateTime(row.get("end_time")));
            record.put("status_text", isScript == 1 ? "脚本签到"
                    : STATUS_MAP.getOrDefault(DbValues.nullableInt(row.get("status")), "未知"));
            record.put("source_site", config.siteCode());
            record.put("source_site_name", config.siteName());
            record.put("is_cross", 0);
            records.add(record);
        }
        return records;
    }

    // ============================================================
    // 6. 获取签到任务列表
    // ============================================================

    private record TaskRow(Map<String, Object> raw, String taskId, String classId,
                           LocalDateTime courseDate, String courseTime, int totalCount) {
    }

    private List<TaskRow> loadTasks(Object teacherId, String courseId, String date) {
        String sql = """
                SELECT at.id AS task_id, at.course_id, c.name AS course_name,
                       cl.id AS class_id, cl.name AS class_name,
                       at.start_time, at.end_time, at.status,
                       c.course_date, c.time AS course_time,
                       (SELECT COUNT(*) FROM students s WHERE s.class_id = c.class_id) AS total_count
                FROM attendance_task at
                INNER JOIN courses c ON c.id = at.course_id
                LEFT JOIN classes cl ON cl.id = c.class_id
                WHERE c.teacher_id = ?
                """;

        List<Object> args = new ArrayList<>();
        args.add(teacherId);

        if (courseId != null && !courseId.trim().isEmpty()) {
            sql += " AND at.course_id = ?";
            args.add(courseId);
        }
        if (date != null && !date.trim().isEmpty()) {
            sql += " AND DATE(at.start_time) = ?";
            args.add(date);
        }
        sql += " ORDER BY at.start_time DESC";

        List<TaskRow> tasks = new ArrayList<>();
        for (Map<String, Object> row : jdbc.queryForList(sql, args.toArray())) {
            tasks.add(new TaskRow(
                    row,
                    str(row.get("task_id")),
                    row.get("class_id") == null ? null : str(row.get("class_id")),
                    DbValues.localDateTime(row.get("course_date")),
                    DbValues.text(row.get("course_time")),
                    DbValues.intValue(row.get("total_count"))));
        }
        return tasks;
    }

    private Map<String, SyncStore.TaskStat> batchStats(List<TaskRow> tasks) {
        List<SyncStore.TaskContext> contexts = new ArrayList<>();
        for (TaskRow task : tasks) {
            contexts.add(new SyncStore.TaskContext(task.taskId(), task.classId(),
                    task.courseDate(), task.courseTime()));
        }
        return store.taskStats(contexts);
    }

    public Map<String, Object> tasks(String userId, String courseId, String date) {
        Object teacherId = requireTeacherId(userId);
        List<TaskRow> taskRows = loadTasks(teacherId, courseId, date);
        Map<String, SyncStore.TaskStat> stats = batchStats(taskRows);

        List<Map<String, Object>> items = new ArrayList<>();

        for (TaskRow task : taskRows) {
            Map<String, Object> row = task.raw();

            Map<String, Object> item = new LinkedHashMap<>();
            item.put("task_id", row.get("task_id"));
            item.put("course_id", row.get("course_id"));
            item.put("course_name", DbValues.text(row.get("course_name")));
            item.put("class_id", row.get("class_id"));
            item.put("class_name", DbValues.text(row.get("class_name")));
            item.put("start_time", DbValues.isoDateTime(row.get("start_time")));
            item.put("end_time", DbValues.isoDateTime(row.get("end_time")));
            item.put("status", row.get("status"));
            item.put("total_count", task.totalCount());
            item.put("signed_count", stats.containsKey(task.taskId())
                    ? stats.get(task.taskId()).signedCount() : 0);
            items.add(item);
        }

        return Api.body("code", 200, "message", "获取签到任务成功", "data", items);
    }

    // ============================================================
    // 7. 查看某次签到的全班名册
    // ============================================================

    public Map<String, Object> roster(String userId, String taskId) {
        if (taskId == null || taskId.trim().isEmpty()) {
            throw new ApiException(400, "签到任务ID不能为空");
        }

        Object teacherId = requireTeacherId(userId);

        List<Map<String, Object>> taskRows = jdbc.queryForList("""
                SELECT at.id, at.course_id, at.start_time, at.end_time, at.status,
                       c.name AS course_name, c.class_id, cl.name AS class_name,
                       c.course_date, c.time
                FROM attendance_task at
                INNER JOIN courses c ON c.id = at.course_id
                LEFT JOIN classes cl ON cl.id = c.class_id
                WHERE at.id = ? AND c.teacher_id = ?
                LIMIT 1
                """, taskId, teacherId);

        if (taskRows.isEmpty()) {
            throw new ApiException(404, "签到任务不存在或无权限");
        }
        Map<String, Object> task = taskRows.get(0);

        Map<String, SyncStore.CrossSign> crossMap;
        try {
            crossMap = store.crossSignsForCourse(task.get("course_date"));
        } catch (Exception e) {
            crossMap = Map.of();
            log.warn("跨站同步读取课程异地签到失败（忽略）：{}", e.getMessage());
        }

        List<Map<String, Object>> students = jdbc.queryForList("""
                SELECT s.id AS student_id, s.student_no, s.name AS student_name,
                       ar.id AS record_id, ar.status AS record_status, ar.sign_time,
                       ar.ip, ar.location, ar.is_script
                FROM students s
                LEFT JOIN attendance_record ar ON ar.student_id = s.id AND ar.task_id = ?
                WHERE s.class_id = ?
                ORDER BY s.student_no ASC
                """, taskId, task.get("class_id"));

        LocalDateTime now = LocalDateTime.now();
        LocalDateTime taskStart = DbValues.localDateTime(task.get("start_time"));
        LocalDateTime taskEnd = DbValues.localDateTime(task.get("end_time"));
        boolean inWindow = taskStart != null && taskEnd != null
                && !now.isBefore(taskStart) && !now.isAfter(taskEnd.plusMinutes(10));

        List<Map<String, Object>> roster = new ArrayList<>();
        Map<String, Object> stats = new LinkedHashMap<>();
        for (int i = 1; i <= 7; i++) {
            stats.put(String.valueOf(i), 0);
        }
        int crossCount = 0;

        for (Map<String, Object> s : students) {
            SyncStore.CrossSign cross = crossMap.get(SyncContract.buildAlignKey(
                    s.get("student_no"), task.get("class_name"),
                    task.get("course_date"), SyncContract.normalizePeriod(task.get("time"))));

            Object recordStatus = s.get("record_status");
            Integer status;
            if (recordStatus != null) {
                status = DbValues.nullableInt(recordStatus);
            } else {
                status = inWindow ? 7 : 3;
            }

            String signTime = s.get("sign_time") == null ? null : DbValues.isoDateTime(s.get("sign_time"));
            int isScript = s.get("is_script") == null ? 0 : DbValues.intValue(s.get("is_script"));

            int isCross = 0;
            String sourceSite = config.siteCode();
            String sourceSiteName = config.siteName();
            String crossSignTime = null;

            String statusText = isScript == 1 ? "脚本签到"
                    : ROSTER_STATUS_MAP.getOrDefault(status, "未知");

            if (cross != null && recordStatus == null) {
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
                statusText = isScript == 1 ? "脚本签到" : "已在其他网站签到";
            }

            Map<String, Object> item = new LinkedHashMap<>();
            item.put("student_id", s.get("student_id"));
            item.put("student_no", DbValues.text(s.get("student_no")));
            item.put("student_name", DbValues.text(s.get("student_name")));
            item.put("record_id", s.get("record_id"));
            item.put("status", status);
            item.put("status_text", statusText);
            item.put("sign_time", signTime);
            item.put("ip", DbValues.text(s.get("ip")));
            item.put("location", DbValues.text(s.get("location")));
            item.put("is_script", isScript);
            item.put("is_cross", isCross);
            item.put("source_site", sourceSite);
            item.put("source_site_name", sourceSiteName);
            item.put("cross_sign_time", crossSignTime);
            roster.add(item);

            String statusKey = String.valueOf(status);
            stats.put(statusKey, DbValues.intValue(stats.get(statusKey)) + 1);

            if (isCross == 1) {
                crossCount++;
            }
        }

        stats.put("cross", crossCount);

        Map<String, Object> taskData = new LinkedHashMap<>();
        taskData.put("task_id", task.get("id"));
        taskData.put("course_id", task.get("course_id"));
        taskData.put("course_name", DbValues.text(task.get("course_name")));
        taskData.put("class_id", task.get("class_id"));
        taskData.put("class_name", DbValues.text(task.get("class_name")));
        taskData.put("start_time", DbValues.isoDateTime(task.get("start_time")));
        taskData.put("end_time", DbValues.isoDateTime(task.get("end_time")));
        taskData.put("status", task.get("status"));

        Map<String, Object> data = new LinkedHashMap<>();
        data.put("task", taskData);
        data.put("stats", stats);
        data.put("roster", roster);

        return Api.body("code", 200, "message", "获取签到名册成功", "data", data);
    }

    // ============================================================
    // 8. 修改学生签到状态
    // ============================================================

    public Map<String, Object> updateRecord(String userId, Map<String, Object> body) {
        Map<String, Object> data = body == null ? Map.of() : body;

        Object taskId = data.get("task_id");
        Object studentId = data.get("student_id");
        Integer status = statusAsInt(data.get("status"));

        if (!truthy(taskId)) {
            throw new ApiException(400, "签到任务ID不能为空");
        }
        if (!truthy(studentId)) {
            throw new ApiException(400, "学生ID不能为空");
        }
        if (status == null || status < 1 || status > 7) {
            throw new ApiException(400, "签到状态无效");
        }

        Object teacherId = requireTeacherId(userId);

        if (!taskBelongsToTeacher(taskId, teacherId)) {
            throw new ApiException(404, "签到任务不存在或无权限");
        }

        if (status == 7) {
            jdbc.update("DELETE FROM attendance_record WHERE task_id = ? AND student_id = ?",
                    taskId, studentId);
            tracker.mark();
            return Api.message(200, "已重置为未签到");
        }

        List<Map<String, Object>> recordRows = jdbc.queryForList(
                "SELECT id FROM attendance_record WHERE task_id = ? AND student_id = ? LIMIT 1",
                taskId, studentId);

        if (!recordRows.isEmpty()) {
            // 教师手动修改签到状态时清除脚本签到标记
            jdbc.update("UPDATE attendance_record SET status = ?, is_script = 0 WHERE id = ?",
                    status, recordRows.get(0).get("id"));
        } else {
            jdbc.update("""
                    INSERT INTO attendance_record (id, task_id, student_id, status, sign_time, is_script)
                    VALUES (?, ?, ?, ?, NOW(), 0)
                    """, UUID.randomUUID().toString(), taskId, studentId, status);
        }
        tracker.mark();

        return Api.message(200, "签到状态已更新");
    }

    // ============================================================
    // 9. 签到统计
    // ============================================================

    public Map<String, Object> statistics(String userId, String courseId, String date) {
        Object teacherId = requireTeacherId(userId);
        List<TaskRow> taskRows = loadTasks(teacherId, courseId, date);
        Map<String, SyncStore.TaskStat> stats = batchStats(taskRows);

        List<Map<String, Object>> items = new ArrayList<>();

        int sumNormal = 0;
        int sumLate = 0;
        int sumAbsent = 0;
        int sumEarly = 0;
        int sumSick = 0;
        int sumLeave = 0;
        int sumTotal = 0;

        for (TaskRow task : taskRows) {
            Map<String, Object> row = task.raw();
            SyncStore.TaskStat stat = stats.get(task.taskId());

            int normal = stat == null ? 0 : stat.count(1);
            int late = stat == null ? 0 : stat.count(2);
            int early = stat == null ? 0 : stat.count(4);
            int sick = stat == null ? 0 : stat.count(5);
            int leave = stat == null ? 0 : stat.count(6);

            int recorded = normal + late + early + sick + leave;
            int absent = Math.max(task.totalCount() - recorded, 0);

            Map<String, Object> item = new LinkedHashMap<>();
            item.put("task_id", row.get("task_id"));
            item.put("course_name", DbValues.text(row.get("course_name")));
            item.put("class_id", row.get("class_id"));
            item.put("class_name", DbValues.text(row.get("class_name")));
            item.put("start_time", DbValues.isoDateTime(row.get("start_time")));
            item.put("end_time", DbValues.isoDateTime(row.get("end_time")));
            item.put("total_count", task.totalCount());
            item.put("normal_count", normal);
            item.put("late_count", late);
            item.put("early_count", early);
            item.put("sick_count", sick);
            item.put("leave_count", leave);
            item.put("absent_count", absent);
            items.add(item);

            sumNormal += normal;
            sumLate += late;
            sumAbsent += absent;
            sumEarly += early;
            sumSick += sick;
            sumLeave += leave;
            sumTotal += task.totalCount();
        }

        Map<String, Object> summary = new LinkedHashMap<>();
        summary.put("normal", sumNormal);
        summary.put("late", sumLate);
        summary.put("absent", sumAbsent);
        summary.put("early", sumEarly);
        summary.put("sick", sumSick);
        summary.put("leave", sumLeave);
        summary.put("total", sumTotal);

        Map<String, Object> data = new LinkedHashMap<>();
        data.put("summary", summary);
        data.put("tasks", items);

        return Api.body("code", 200, "message", "获取统计成功", "data", data);
    }
}
