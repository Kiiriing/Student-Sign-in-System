package com.stu.signin.auth;

import com.stu.signin.common.Api;
import com.stu.signin.common.ApiException;
import com.stu.signin.security.JwtService;
import com.stu.signin.security.PasswordVerifier;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * 登录业务，对应 Python 版 api/auth.py。
 */
@Service
public class AuthService {

    private static final String FIND_USER_SQL = """
            SELECT
                u.id AS user_id,
                u.username,
                u.password,
                u.role,
                u.phone,
                u.status,

                s.id AS student_id,
                s.student_no,
                s.name AS student_name,
                s.class_id,

                c.name AS class_name,

                t.id AS teacher_id,
                t.name AS teacher_name,
                t.department

            FROM users u

            LEFT JOIN students s
                ON s.user_id = u.id

            LEFT JOIN classes c
                ON c.id = s.class_id

            LEFT JOIN teachers t
                ON t.user_id = u.id

            WHERE
                u.username = ?
                OR s.student_no = ?
                OR s.name = ?

            LIMIT 1
            """;

    private final JdbcTemplate jdbcTemplate;
    private final PasswordVerifier passwordVerifier;
    private final JwtService jwtService;

    public AuthService(JdbcTemplate jdbcTemplate, PasswordVerifier passwordVerifier, JwtService jwtService) {
        this.jdbcTemplate = jdbcTemplate;
        this.passwordVerifier = passwordVerifier;
        this.jwtService = jwtService;
    }

    public Map<String, Object> login(String username, String password, String deviceId) {
        List<Map<String, Object>> rows = jdbcTemplate.queryForList(FIND_USER_SQL, username, username, username);

        if (rows.isEmpty()) {
            throw new ApiException(401, "账号或密码错误");
        }

        Map<String, Object> user = rows.get(0);

        int status = toInt(user.get("status"));
        if (status != 1) {
            throw new ApiException(403, "账号已被禁用");
        }

        if (!passwordVerifier.matches(toStr(user.get("password")), password)) {
            throw new ApiException(401, "账号或密码错误");
        }

        int role = toInt(user.get("role"));
        String userId = toStr(user.get("user_id"));

        // 学生每日设备限制
        if (role == 1) {
            List<Map<String, Object>> records = jdbcTemplate.queryForList(
                    "SELECT id, user_id, login_date FROM device_login_record "
                            + "WHERE device_id = ? AND login_date = CURDATE() LIMIT 1",
                    deviceId);

            if (!records.isEmpty()) {
                if (!toStr(records.get(0).get("user_id")).equals(userId)) {
                    throw new ApiException(403,
                            "该设备今天已经登录其他学生账号，每台设备每天只能登录一个学生账号");
                }
            } else {
                jdbcTemplate.update(
                        "INSERT INTO device_login_record (device_id, user_id, login_date) "
                                + "VALUES (?, ?, CURDATE())",
                        deviceId, userId);
            }
        }

        String accessToken = jwtService.createAccessToken(userId, role);

        Map<String, Object> result = Api.body(
                "code", 200,
                "message", "登录成功",
                "access_token", accessToken,
                "user_id", userId,
                "username", user.get("username"),
                "role", role
        );

        if (role == 1) {
            result.put("student_id", user.get("student_id") == null ? null : toStr(user.get("student_id")));
            result.put("student_no", user.get("student_no"));
            result.put("student_name", user.get("student_name"));
            result.put("class_name", user.get("class_name"));
        } else if (role == 2) {
            result.put("teacher_id", user.get("teacher_id") == null ? null : toStr(user.get("teacher_id")));
            result.put("teacher_name", user.get("teacher_name"));
            result.put("department", user.get("department"));
        } else if (role == 3) {
            result.put("admin_name", user.get("username"));
        }

        return result;
    }

    private static String toStr(Object value) {
        return value == null ? null : String.valueOf(value);
    }

    private static int toInt(Object value) {
        if (value instanceof Number number) {
            return number.intValue();
        }
        return value == null ? 0 : Integer.parseInt(String.valueOf(value));
    }
}
