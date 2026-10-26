package com.stu.signin.student;

import com.stu.signin.common.Api;
import com.stu.signin.security.AuthGuard;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * 学生端接口，对应 Python api/student.py 的路由定义。
 */
@RestController
public class StudentController {

    private final StudentService studentService;
    private final AuthGuard authGuard;

    public StudentController(StudentService studentService, AuthGuard authGuard) {
        this.studentService = studentService;
        this.authGuard = authGuard;
    }

    private AuthGuard.User requireStudent(HttpServletRequest request) {
        return authGuard.require(request, 1, "只有学生可以访问此接口");
    }

    @GetMapping("/api/student/courses")
    public Map<String, Object> courses(HttpServletRequest request) {
        AuthGuard.User user = requireStudent(request);
        return Api.guard("获取课程失败", () -> studentService.courses(user.userId()));
    }

    @PostMapping("/api/student/signin")
    public ResponseEntity<Map<String, Object>> signin(
            HttpServletRequest request,
            @RequestBody(required = false) Map<String, Object> body) {

        AuthGuard.User user = requireStudent(request);

        try {
            Map<String, Object> response = Api.guard("签到失败",
                    () -> studentService.signin(user.userId(), body, request));
            return ResponseEntity.ok(response);
        } catch (StudentService.ApiExceptionData e) {
            Map<String, Object> response = new LinkedHashMap<>();
            response.put("code", e.getStatus());
            response.put("message", e.getMessage());
            response.put("data", e.getData());
            return ResponseEntity.status(e.getStatus()).body(response);
        }
    }

    @GetMapping("/api/student/records")
    public Map<String, Object> records(HttpServletRequest request,
                                       @RequestParam(value = "date", required = false) String date) {
        AuthGuard.User user = requireStudent(request);

        List<Map<String, Object>> records = Api.guard("获取签到记录失败",
                () -> studentService.records(user.userId(), date));

        return Api.body("code", 200, "message", "获取签到记录成功", "data", records);
    }

    @GetMapping("/api/student/class-attendance")
    public Map<String, Object> classAttendance(HttpServletRequest request,
                                               @RequestParam(value = "date", required = false) String date) {
        AuthGuard.User user = requireStudent(request);
        return Api.guard("获取班级签到情况失败",
                () -> studentService.classAttendance(user.userId(), date));
    }
}
