package com.stu.signin.teacher;

import com.stu.signin.common.Api;
import com.stu.signin.security.AuthGuard;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

/**
 * 教师端接口，对应 Python api/teacher.py 的路由定义。
 */
@RestController
public class TeacherController {

    private final TeacherService teacherService;
    private final AuthGuard authGuard;

    public TeacherController(TeacherService teacherService, AuthGuard authGuard) {
        this.teacherService = teacherService;
        this.authGuard = authGuard;
    }

    private AuthGuard.User requireTeacher(HttpServletRequest request) {
        return authGuard.require(request, 2, "只有教师可以访问此接口");
    }

    @GetMapping("/api/teacher/courses")
    public Map<String, Object> courses(HttpServletRequest request) {
        AuthGuard.User user = requireTeacher(request);
        return Api.guard("获取课程失败", () -> teacherService.courses(user.userId()));
    }

    @PostMapping("/api/teacher/attendance/create")
    public Map<String, Object> createAttendance(HttpServletRequest request,
                                                @RequestBody(required = false) Map<String, Object> body) {
        AuthGuard.User user = requireTeacher(request);
        return Api.guard("创建签到任务失败",
                () -> teacherService.createAttendance(user.userId(), body));
    }

    @PostMapping("/api/teacher/attendance/close")
    public Map<String, Object> closeAttendance(HttpServletRequest request,
                                               @RequestBody(required = false) Map<String, Object> body) {
        AuthGuard.User user = requireTeacher(request);
        return Api.guard("关闭签到任务失败",
                () -> teacherService.closeAttendance(user.userId(), body));
    }

    @PostMapping("/api/teacher/attendance/delete")
    public Map<String, Object> deleteAttendance(HttpServletRequest request,
                                                @RequestBody(required = false) Map<String, Object> body) {
        AuthGuard.User user = requireTeacher(request);
        return Api.guard("删除签到任务失败",
                () -> teacherService.deleteAttendance(user.userId(), body));
    }

    @GetMapping("/api/teacher/attendance/records")
    public Map<String, Object> records(HttpServletRequest request,
                                       @RequestParam(value = "task_id", required = false) String taskId) {
        AuthGuard.User user = requireTeacher(request);

        List<Map<String, Object>> records = Api.guard("获取签到记录失败",
                () -> teacherService.records(user.userId(), taskId));

        return Api.body("code", 200, "message", "获取签到记录成功", "data", records);
    }

    @GetMapping("/api/teacher/tasks")
    public Map<String, Object> tasks(HttpServletRequest request,
                                     @RequestParam(value = "course_id", required = false) String courseId,
                                     @RequestParam(value = "date", required = false) String date) {
        AuthGuard.User user = requireTeacher(request);
        return Api.guard("获取签到任务失败",
                () -> teacherService.tasks(user.userId(), courseId, date));
    }

    @GetMapping("/api/teacher/attendance/roster")
    public Map<String, Object> roster(HttpServletRequest request,
                                      @RequestParam(value = "task_id", required = false) String taskId) {
        AuthGuard.User user = requireTeacher(request);
        return Api.guard("获取签到名册失败",
                () -> teacherService.roster(user.userId(), taskId));
    }

    @PutMapping("/api/teacher/attendance/record")
    public Map<String, Object> updateRecord(HttpServletRequest request,
                                            @RequestBody(required = false) Map<String, Object> body) {
        AuthGuard.User user = requireTeacher(request);
        return Api.guard("修改签到状态失败",
                () -> teacherService.updateRecord(user.userId(), body));
    }

    @GetMapping("/api/teacher/statistics")
    public Map<String, Object> statistics(HttpServletRequest request,
                                          @RequestParam(value = "course_id", required = false) String courseId,
                                          @RequestParam(value = "date", required = false) String date) {
        AuthGuard.User user = requireTeacher(request);
        return Api.guard("获取统计失败",
                () -> teacherService.statistics(user.userId(), courseId, date));
    }
}
