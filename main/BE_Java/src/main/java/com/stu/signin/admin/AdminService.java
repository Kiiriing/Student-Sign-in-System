package com.stu.signin.admin;

import com.stu.signin.common.Api;
import com.stu.signin.common.ApiException;
import com.stu.signin.common.DbValues;
import com.stu.signin.persistence.DbWriteTracker;
import com.stu.signin.persistence.DbWriter;
import com.stu.signin.security.PasswordHasher;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.support.GeneratedKeyHolder;
import org.springframework.jdbc.support.KeyHolder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.support.TransactionTemplate;

import java.sql.PreparedStatement;
import java.sql.Statement;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * 管理员端业务，对应 Python api/admin.py 的 22 个接口。
 *
 * 所有 SQL 走 JdbcTemplate（预编译参数绑定），多语句写操作统一包在
 * TransactionTemplate 里，保证与 Python 版 commit / rollback 语义一致。
 */
@Service
public class AdminService {

    private static final DateTimeFormatter DATE_TIME_OUT = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
    private static final DateTimeFormatter DATE_ONLY = DateTimeFormatter.ofPattern("yyyy-MM-dd");

    private static final List<String> UPDATE_TAGS = List.of("新增", "优化", "修复");
    private static final int UPDATE_CONTENT_MAX = 500;

    private final JdbcTemplate jdbc;
    private final DbWriter writer;
    private final DbWriteTracker tracker;
    private final PasswordHasher passwordHasher;
    private final TransactionTemplate transactionTemplate;

    public AdminService(JdbcTemplate jdbc, DbWriter writer, DbWriteTracker tracker,
                        PasswordHasher passwordHasher, TransactionTemplate transactionTemplate) {
        this.jdbc = jdbc;
        this.writer = writer;
        this.tracker = tracker;
        this.passwordHasher = passwordHasher;
        this.transactionTemplate = transactionTemplate;
    }

    // ============================================================
    // 工具
    // ============================================================

    private static String text(Object value) {
        return value == null ? null : String.valueOf(value);
    }

    private static boolean blank(Object value) {
        return value == null || String.valueOf(value).isBlank();
    }

    private Map<String, Object> userRow(Map<String, Object> raw) {
        Map<String, Object> item = new LinkedHashMap<>();
        item.put("id", raw.get("id"));
        item.put("username", raw.get("username"));
        item.put("phone", raw.get("phone"));
        item.put("role", raw.get("role"));
        item.put("status", raw.get("status"));
        item.put("create_time", DbValues.dateTime(raw.get("create_time")));
        return item;
    }

    // ============================================================
    // 1. 管理员信息
    // ============================================================

    public Map<String, Object> profile(String adminId) {
        try {
            List<Map<String, Object>> rows = jdbc.queryForList("""
                    SELECT id, username, phone, role, status, create_time
                    FROM users
                    WHERE id = ?
                    """, adminId);

            Map<String, Object> user = rows.isEmpty() ? null : userRow(rows.get(0));

            Map<String, Object> response = new LinkedHashMap<>();
            response.put("code", 200);
            response.put("data", user);
            return response;
        } catch (Exception e) {
            throw new ApiException(500, String.valueOf(e.getMessage()));
        }
    }

    // ============================================================
    // 2. 获取所有用户
    // ============================================================

    public Map<String, Object> users() {
        try {
            List<Map<String, Object>> users = jdbc.queryForList("""
                    SELECT id, username, phone, role, status, create_time
                    FROM users
                    ORDER BY create_time DESC
                    """);

            List<Map<String, Object>> data = new ArrayList<>(users.size());
            for (Map<String, Object> item : users) {
                data.add(userRow(item));
            }

            Map<String, Object> response = new LinkedHashMap<>();
            response.put("code", 200);
            response.put("data", data);
            return response;
        } catch (Exception e) {
            throw new ApiException(500, String.valueOf(e.getMessage()));
        }
    }

    // ============================================================
    // 3. 创建教师账号
    // ============================================================

    public Map<String, Object> createTeacher(Map<String, Object> body) {
        Map<String, Object> data = body == null ? Map.of() : body;

        Object username = data.get("username");
        Object password = data.get("password");
        Object name = data.get("name");
        Object department = data.get("department");
        Object phone = data.get("phone");

        if (blank(username) || blank(password) || blank(name)) {
            throw new ApiException(400, "用户名、密码、姓名不能为空");
        }

        String userText = String.valueOf(username);
        if (usernameExists(userText)) {
            throw new ApiException(400, "用户名已经存在");
        }

        String userId = UUID.randomUUID().toString();
        String teacherId = UUID.randomUUID().toString();
        String passwordHash = passwordHasher.generate(String.valueOf(password));

        transactionTemplate.executeWithoutResult(status -> {
            writer.update("""
                    INSERT INTO users (id, username, password, role, phone, status)
                    VALUES (?, ?, ?, 2, ?, 1)
                    """, userId, userText, passwordHash, phone);

            writer.update("""
                    INSERT INTO teachers (id, user_id, name, department)
                    VALUES (?, ?, ?, ?)
                    """, teacherId, userId, String.valueOf(name), department);
        });

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("user_id", userId);
        result.put("teacher_id", teacherId);

        return Api.body("code", 200, "message", "教师创建成功", "data", result);
    }

    private boolean usernameExists(String username) {
        List<Map<String, Object>> rows = jdbc.queryForList(
                "SELECT id FROM users WHERE username = ?", username);
        return !rows.isEmpty();
    }

    // ============================================================
    // 4. 创建学生账号
    // ============================================================

    public Map<String, Object> createStudent(Map<String, Object> body) {
        Map<String, Object> data = body == null ? Map.of() : body;

        Object username = data.get("username");
        Object password = data.get("password");
        Object studentNo = data.get("student_no");
        Object name = data.get("name");
        Object classId = data.get("class_id");
        Object phone = data.get("phone");

        if (blank(username) || blank(password) || blank(studentNo) || blank(name)) {
            throw new ApiException(400, "参数不能为空");
        }

        String userText = String.valueOf(username);
        String studentNoText = String.valueOf(studentNo);

        if (usernameExists(userText)) {
            throw new ApiException(400, "用户名已经存在");
        }

        if (!jdbc.queryForList("SELECT id FROM students WHERE student_no = ?", studentNoText).isEmpty()) {
            throw new ApiException(400, "学号已经存在");
        }

        String userId = UUID.randomUUID().toString();
        String studentId = UUID.randomUUID().toString();
        String passwordHash = passwordHasher.generate(String.valueOf(password));

        transactionTemplate.executeWithoutResult(status -> {
            writer.update("""
                    INSERT INTO users (id, username, password, role, phone, status)
                    VALUES (?, ?, ?, 1, ?, 1)
                    """, userId, userText, passwordHash, phone);

            writer.update("""
                    INSERT INTO students (id, user_id, student_no, name, class_id)
                    VALUES (?, ?, ?, ?, ?)
                    """, studentId, userId, studentNoText, String.valueOf(name), classId);
        });

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("user_id", userId);
        result.put("student_id", studentId);

        return Api.body("code", 200, "message", "学生创建成功", "data", result);
    }

    // ============================================================
    // 5. 创建课程
    // ============================================================

    public Map<String, Object> createCourse(Map<String, Object> body) {
        Map<String, Object> data = body == null ? Map.of() : body;

        Object name = data.get("name");
        Object teacherId = data.get("teacher_id");
        Object classId = data.get("class_id");
        Object courseDate = data.get("course_date");
        Object courseTime = data.get("time");

        if (blank(name) || blank(teacherId) || blank(classId)) {
            throw new ApiException(400, "课程参数不完整");
        }

        if (jdbc.queryForList("SELECT id FROM teachers WHERE id = ?", teacherId).isEmpty()) {
            throw new ApiException(404, "教师不存在");
        }

        if (jdbc.queryForList("SELECT id FROM classes WHERE id = ?", classId).isEmpty()) {
            throw new ApiException(404, "班级不存在");
        }

        String courseId = UUID.randomUUID().toString();

        writer.update("""
                INSERT INTO courses (id, name, teacher_id, class_id, course_date, time)
                VALUES (?, ?, ?, ?, ?, ?)
                """, courseId, String.valueOf(name), teacherId, classId, courseDate, courseTime);

        return Api.body("code", 200, "message", "课程创建成功",
                "data", DbValues.row("course_id", courseId));
    }

    // ============================================================
    // 6. 修改用户密码
    // ============================================================

    public Map<String, Object> updatePassword(Map<String, Object> body) {
        Map<String, Object> data = body == null ? Map.of() : body;

        Object userId = data.get("user_id");
        Object password = data.get("password");

        if (blank(userId) || blank(password)) {
            throw new ApiException(400, "参数错误");
        }

        writer.update("UPDATE users SET password = ? WHERE id = ?",
                passwordHasher.generate(String.valueOf(password)), userId);

        return Api.message(200, "密码修改成功");
    }

    // ============================================================
    // 7. 修改账号状态
    // ============================================================

    public Map<String, Object> updateUserStatus(Map<String, Object> body) {
        Map<String, Object> data = body == null ? Map.of() : body;

        Object userId = data.get("user_id");
        Object status = data.get("status");

        if (userId == null || status == null) {
            throw new ApiException(400, "参数错误");
        }

        writer.update("UPDATE users SET status = ? WHERE id = ?", status, userId);

        return Api.message(200, "账号状态修改成功");
    }

    // ============================================================
    // 8. 教师列表
    // ============================================================

    public Map<String, Object> teachers() {
        List<Map<String, Object>> raw = jdbc.queryForList("""
                SELECT t.id AS teacher_id, t.user_id, t.name, t.department, t.class_id,
                       c.name AS class_name, u.username, u.phone, u.status, u.create_time
                FROM teachers t
                INNER JOIN users u ON u.id = t.user_id
                LEFT JOIN classes c ON c.id = t.class_id
                ORDER BY u.create_time DESC, t.name ASC
                """);

        List<Map<String, Object>> data = new ArrayList<>(raw.size());
        for (Map<String, Object> item : raw) {
            Map<String, Object> out = new LinkedHashMap<>();
            out.put("teacher_id", item.get("teacher_id"));
            out.put("user_id", item.get("user_id"));
            out.put("name", item.get("name"));
            out.put("department", item.get("department"));
            out.put("class_id", item.get("class_id"));
            out.put("class_name", item.get("class_name"));
            out.put("username", item.get("username"));
            out.put("phone", item.get("phone"));
            out.put("status", item.get("status"));
            out.put("create_time", DbValues.dateTime(item.get("create_time")));
            data.add(out);
        }

        Map<String, Object> response = new LinkedHashMap<>();
        response.put("code", 200);
        response.put("data", data);
        return response;
    }

    // ============================================================
    // 9. 学生列表
    // ============================================================

    public Map<String, Object> students() {
        List<Map<String, Object>> raw = jdbc.queryForList("""
                SELECT s.id AS student_id, s.user_id, s.student_no, s.name, s.class_id,
                       c.name AS class_name, u.username, u.phone, u.status, u.create_time
                FROM students s
                INNER JOIN users u ON u.id = s.user_id
                LEFT JOIN classes c ON c.id = s.class_id
                ORDER BY s.student_no ASC
                """);

        List<Map<String, Object>> data = new ArrayList<>(raw.size());
        for (Map<String, Object> item : raw) {
            Map<String, Object> out = new LinkedHashMap<>();
            out.put("student_id", item.get("student_id"));
            out.put("user_id", item.get("user_id"));
            out.put("student_no", item.get("student_no"));
            out.put("name", item.get("name"));
            out.put("class_id", item.get("class_id"));
            out.put("class_name", item.get("class_name"));
            out.put("username", item.get("username"));
            out.put("phone", item.get("phone"));
            out.put("status", item.get("status"));
            out.put("create_time", DbValues.dateTime(item.get("create_time")));
            data.add(out);
        }

        Map<String, Object> response = new LinkedHashMap<>();
        response.put("code", 200);
        response.put("data", data);
        return response;
    }

    // ============================================================
    // 10. 班级列表
    // ============================================================

    public Map<String, Object> classes() {
        List<Map<String, Object>> data = jdbc.queryForList("""
                SELECT c.id, c.name, c.grade, t.name AS teacher_name
                FROM classes c
                LEFT JOIN teachers t ON t.id = c.teacher_id
                ORDER BY c.grade DESC, c.name ASC
                """);

        Map<String, Object> response = new LinkedHashMap<>();
        response.put("code", 200);
        response.put("data", data);
        return response;
    }

    // ============================================================
    // 11. 课程列表
    // ============================================================

    public Map<String, Object> courses() {
        List<Map<String, Object>> raw = jdbc.queryForList("""
                SELECT co.id, co.name, co.teacher_id, co.class_id, co.course_date, co.time,
                       t.name AS teacher_name, c.name AS class_name
                FROM courses co
                INNER JOIN teachers t ON t.id = co.teacher_id
                INNER JOIN classes c ON c.id = co.class_id
                ORDER BY co.course_date DESC, co.time ASC
                """);

        List<Map<String, Object>> data = new ArrayList<>(raw.size());
        for (Map<String, Object> item : raw) {
            Map<String, Object> out = new LinkedHashMap<>();
            out.put("id", item.get("id"));
            out.put("name", item.get("name"));
            out.put("teacher_id", item.get("teacher_id"));
            out.put("class_id", item.get("class_id"));
            out.put("course_date", DbValues.date(item.get("course_date")));
            out.put("time", item.get("time"));
            out.put("teacher_name", item.get("teacher_name"));
            out.put("class_name", item.get("class_name"));
            data.add(out);
        }

        Map<String, Object> response = new LinkedHashMap<>();
        response.put("code", 200);
        response.put("data", data);
        return response;
    }

    // ============================================================
    // 12. 创建班级
    // ============================================================

    public Map<String, Object> createClass(Map<String, Object> body) {
        Map<String, Object> data = body == null ? Map.of() : body;

        Object name = data.get("name");
        Object grade = data.get("grade");
        Object teacherId = data.get("teacher_id");

        if (blank(name)) {
            throw new ApiException(400, "班级名称不能为空");
        }

        if (!blank(teacherId)
                && jdbc.queryForList("SELECT id FROM teachers WHERE id = ?", teacherId).isEmpty()) {
            throw new ApiException(404, "教师不存在");
        }

        String classId = UUID.randomUUID().toString();

        writer.update("""
                INSERT INTO classes (id, name, grade, teacher_id)
                VALUES (?, ?, ?, ?)
                """, classId, String.valueOf(name), grade, teacherId);

        return Api.body("code", 200, "message", "班级创建成功",
                "data", DbValues.row("class_id", classId));
    }

    // ============================================================
    // 13. 删除班级
    // ============================================================

    public Map<String, Object> deleteClass(String classId) {
        if (jdbc.queryForList("SELECT id, name FROM classes WHERE id = ?", classId).isEmpty()) {
            throw new ApiException(404, "班级不存在");
        }

        writer.update("DELETE FROM classes WHERE id = ?", classId);

        return Api.message(200, "班级删除成功");
    }

    // ============================================================
    // 14. 删除教师账户
    // ============================================================

    public Map<String, Object> deleteTeacher(String teacherId) {
        List<Map<String, Object>> rows = jdbc.queryForList(
                "SELECT id, user_id, name FROM teachers WHERE id = ?", teacherId);

        if (rows.isEmpty()) {
            throw new ApiException(404, "教师不存在");
        }

        writer.update("DELETE FROM users WHERE id = ?", rows.get(0).get("user_id"));

        return Api.message(200, "教师账户删除成功");
    }

    // ============================================================
    // 15. 删除学生账户
    // ============================================================

    public Map<String, Object> deleteStudent(String studentId) {
        List<Map<String, Object>> rows = jdbc.queryForList(
                "SELECT id, user_id, name FROM students WHERE id = ?", studentId);

        if (rows.isEmpty()) {
            throw new ApiException(404, "学生不存在");
        }

        writer.update("DELETE FROM users WHERE id = ?", rows.get(0).get("user_id"));

        return Api.message(200, "学生账户删除成功");
    }

    // ============================================================
    // 16. 删除课程
    // ============================================================

    public Map<String, Object> deleteCourse(String courseId) {
        if (jdbc.queryForList("SELECT id, name FROM courses WHERE id = ?", courseId).isEmpty()) {
            throw new ApiException(404, "课程不存在");
        }

        writer.update("DELETE FROM courses WHERE id = ?", courseId);

        return Api.message(200, "课程删除成功");
    }

    // ============================================================
    // 17. 分配学生到班级
    // ============================================================

    public Map<String, Object> assignStudentClass(Map<String, Object> body) {
        Map<String, Object> data = body == null ? Map.of() : body;

        Object studentId = data.get("student_id");
        Object classId = blank(data.get("class_id")) ? null : data.get("class_id");

        if (blank(studentId)) {
            throw new ApiException(400, "学生ID不能为空");
        }

        if (jdbc.queryForList("SELECT id FROM students WHERE id = ?", studentId).isEmpty()) {
            throw new ApiException(404, "学生不存在");
        }

        if (classId != null && jdbc.queryForList("SELECT id FROM classes WHERE id = ?", classId).isEmpty()) {
            throw new ApiException(404, "班级不存在");
        }

        writer.update("UPDATE students SET class_id = ? WHERE id = ?", classId, studentId);

        return Api.message(200, "学生班级分配成功");
    }

    // ============================================================
    // 18. 分配教师到班级
    // ============================================================

    public Map<String, Object> assignTeacherClass(Map<String, Object> body) {
        Map<String, Object> data = body == null ? Map.of() : body;

        Object teacherId = data.get("teacher_id");
        Object classId = blank(data.get("class_id")) ? null : data.get("class_id");

        if (blank(teacherId)) {
            throw new ApiException(400, "教师ID不能为空");
        }

        if (jdbc.queryForList("SELECT id FROM teachers WHERE id = ?", teacherId).isEmpty()) {
            throw new ApiException(404, "教师不存在");
        }

        if (classId != null && jdbc.queryForList("SELECT id FROM classes WHERE id = ?", classId).isEmpty()) {
            throw new ApiException(404, "班级不存在");
        }

        writer.update("UPDATE teachers SET class_id = ? WHERE id = ?", classId, teacherId);

        return Api.message(200, "教师班级分配成功");
    }

    // ============================================================
    // 19. 更新日志列表
    // ============================================================

    public Map<String, Object> listUpdates(String keyword) {
        String trimmed = keyword == null ? "" : keyword.trim();

        List<Map<String, Object>> data;
        if (!trimmed.isEmpty()) {
            String like = "%" + trimmed + "%";
            data = jdbc.queryForList("""
                    SELECT `update_id`, `tag`, `content`,
                           DATE_FORMAT(`created_at`, '%Y-%m-%d %H:%i') AS `created_at`
                    FROM `update_log`
                    WHERE `tag` LIKE ? OR `content` LIKE ?
                    ORDER BY `created_at` DESC, `update_id` DESC
                    """, like, like);
        } else {
            data = jdbc.queryForList("""
                    SELECT `update_id`, `tag`, `content`,
                           DATE_FORMAT(`created_at`, '%Y-%m-%d %H:%i') AS `created_at`
                    FROM `update_log`
                    ORDER BY `created_at` DESC, `update_id` DESC
                    """);
        }

        List<Map<String, Object>> rows = new ArrayList<>(data.size());
        for (Map<String, Object> item : data) {
            Map<String, Object> out = new LinkedHashMap<>();
            out.put("update_id", item.get("update_id"));
            out.put("tag", item.get("tag"));
            out.put("content", item.get("content"));
            out.put("created_at", item.get("created_at"));
            rows.add(out);
        }

        return Api.body("code", 200, "message", "ok", "data", rows);
    }

    // ============================================================
    // 20 / 21. 新增 / 修改更新日志
    // ============================================================

    /** 校验结果：tag / content / dateValue / error */
    private record UpdatePayload(String tag, String content, String dateValue, String error) {
    }

    private UpdatePayload parseUpdatePayload(Map<String, Object> body) {
        Map<String, Object> data = body == null ? Map.of() : body;

        String tag = String.valueOf(data.getOrDefault("tag", "")).trim();
        String content = String.valueOf(data.getOrDefault("content", "")).trim();
        String date = String.valueOf(data.getOrDefault("date", "")).trim();

        if (!UPDATE_TAGS.contains(tag)) {
            return new UpdatePayload(null, null, null, "类型必须是 新增 / 优化 / 修复");
        }

        if (content.isEmpty()) {
            return new UpdatePayload(null, null, null, "请输入更新内容");
        }

        if (content.length() > UPDATE_CONTENT_MAX) {
            return new UpdatePayload(null, null, null,
                    "更新内容不能超过 " + UPDATE_CONTENT_MAX + " 字");
        }

        String dateValue = null;
        if (!date.isEmpty()) {
            try {
                LocalDate.parse(date, DATE_ONLY);
            } catch (DateTimeParseException e) {
                return new UpdatePayload(null, null, null, "日期格式不正确");
            }
            dateValue = date + " 00:00:00";
        }

        return new UpdatePayload(tag, content, dateValue, null);
    }

    public Map<String, Object> createUpdate(Map<String, Object> body) {
        UpdatePayload payload = parseUpdatePayload(body);
        if (payload.error() != null) {
            throw new ApiException(400, payload.error());
        }

        KeyHolder keyHolder = new GeneratedKeyHolder();

        if (payload.dateValue() != null) {
            jdbc.update(connection -> {
                PreparedStatement statement = connection.prepareStatement(
                        "INSERT INTO `update_log` (`tag`, `content`, `created_at`) VALUES (?, ?, ?)",
                        Statement.RETURN_GENERATED_KEYS);
                statement.setString(1, payload.tag());
                statement.setString(2, payload.content());
                statement.setString(3, payload.dateValue());
                return statement;
            }, keyHolder);
        } else {
            jdbc.update(connection -> {
                PreparedStatement statement = connection.prepareStatement(
                        "INSERT INTO `update_log` (`tag`, `content`) VALUES (?, ?)",
                        Statement.RETURN_GENERATED_KEYS);
                statement.setString(1, payload.tag());
                statement.setString(2, payload.content());
                return statement;
            }, keyHolder);
        }
        tracker.mark();

        Number key = keyHolder.getKey();
        return Api.body("code", 200, "message", "新增成功",
                "data", DbValues.row("update_id", key == null ? null : key.longValue()));
    }

    public Map<String, Object> updateUpdate(long updateId, Map<String, Object> body) {
        UpdatePayload payload = parseUpdatePayload(body);
        if (payload.error() != null) {
            throw new ApiException(400, payload.error());
        }

        if (jdbc.queryForList("SELECT `update_id` FROM `update_log` WHERE `update_id` = ?", updateId).isEmpty()) {
            throw new ApiException(404, "更新记录不存在");
        }

        if (payload.dateValue() != null) {
            writer.update("""
                    UPDATE `update_log`
                    SET `tag` = ?, `content` = ?, `created_at` = ?
                    WHERE `update_id` = ?
                    """, payload.tag(), payload.content(), payload.dateValue(), updateId);
        } else {
            writer.update("""
                    UPDATE `update_log`
                    SET `tag` = ?, `content` = ?
                    WHERE `update_id` = ?
                    """, payload.tag(), payload.content(), updateId);
        }

        return Api.message(200, "修改成功");
    }

    // ============================================================
    // 22. 删除更新日志
    // ============================================================

    public Map<String, Object> deleteUpdate(long updateId) {
        if (jdbc.queryForList("SELECT `update_id` FROM `update_log` WHERE `update_id` = ?", updateId).isEmpty()) {
            throw new ApiException(404, "更新记录不存在");
        }

        writer.update("DELETE FROM `update_log` WHERE `update_id` = ?", updateId);

        return Api.message(200, "删除成功");
    }

    /**
     * 供 Controller 复用的统一 500 收敛（错误文案 + error 详情），
     * 与 Python 各接口的 except 分支保持一致。
     */
    public static <T> T guard(String failMessage, java.util.function.Supplier<T> task) {
        try {
            return task.get();
        } catch (ApiException e) {
            throw e;
        } catch (Exception e) {
            throw new ApiException(500, failMessage, String.valueOf(e.getMessage()));
        }
    }
}
