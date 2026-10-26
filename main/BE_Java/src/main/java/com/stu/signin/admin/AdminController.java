package com.stu.signin.admin;

import com.stu.signin.common.Api;
import com.stu.signin.security.AuthGuard;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

/**
 * 管理员端接口，对应 Python api/admin.py 的 22 个路由。
 */
@RestController
public class AdminController {

    private final AdminService adminService;
    private final AuthGuard authGuard;

    public AdminController(AdminService adminService, AuthGuard authGuard) {
        this.adminService = adminService;
        this.authGuard = authGuard;
    }

    private AuthGuard.User requireAdmin(HttpServletRequest request) {
        return authGuard.require(request, 3, "无管理员权限");
    }

    // ============================================================
    // 管理员信息 / 用户 / 列表
    // ============================================================

    @GetMapping("/api/admin/profile")
    public Map<String, Object> profile(HttpServletRequest request) {
        AuthGuard.User user = requireAdmin(request);
        return adminService.profile(user.userId());
    }

    @GetMapping("/api/admin/users")
    public Map<String, Object> users(HttpServletRequest request) {
        requireAdmin(request);
        return adminService.users();
    }

    @GetMapping("/api/admin/teachers")
    public Map<String, Object> teachers(HttpServletRequest request) {
        requireAdmin(request);
        return AdminService.guard("获取教师列表失败", adminService::teachers);
    }

    @GetMapping("/api/admin/students")
    public Map<String, Object> students(HttpServletRequest request) {
        requireAdmin(request);
        return AdminService.guard("获取学生列表失败", adminService::students);
    }

    @GetMapping("/api/admin/classes")
    public Map<String, Object> classes(HttpServletRequest request) {
        requireAdmin(request);
        return AdminService.guard("获取班级列表失败", adminService::classes);
    }

    @GetMapping("/api/admin/courses")
    public Map<String, Object> courses(HttpServletRequest request) {
        requireAdmin(request);
        return AdminService.guard("获取课程列表失败", adminService::courses);
    }

    // ============================================================
    // 创建账号 / 课程 / 班级
    // ============================================================

    @PostMapping("/api/admin/teacher/create")
    public Map<String, Object> createTeacher(HttpServletRequest request,
                                             @RequestBody(required = false) Map<String, Object> body) {
        requireAdmin(request);
        return AdminService.guard("创建教师失败", () -> adminService.createTeacher(body));
    }

    @PostMapping("/api/admin/student/create")
    public Map<String, Object> createStudent(HttpServletRequest request,
                                             @RequestBody(required = false) Map<String, Object> body) {
        requireAdmin(request);
        return AdminService.guard("创建学生失败", () -> adminService.createStudent(body));
    }

    @PostMapping("/api/admin/courses/create")
    public Map<String, Object> createCourse(HttpServletRequest request,
                                            @RequestBody(required = false) Map<String, Object> body) {
        requireAdmin(request);
        return AdminService.guard("课程创建失败", () -> adminService.createCourse(body));
    }

    @PostMapping("/api/admin/class/create")
    public Map<String, Object> createClass(HttpServletRequest request,
                                           @RequestBody(required = false) Map<String, Object> body) {
        requireAdmin(request);
        return AdminService.guard("班级创建失败", () -> adminService.createClass(body));
    }

    // ============================================================
    // 修改用户密码 / 状态
    // ============================================================

    @PutMapping("/api/admin/user/password")
    public Map<String, Object> updatePassword(HttpServletRequest request,
                                              @RequestBody(required = false) Map<String, Object> body) {
        requireAdmin(request);
        return AdminService.guard("密码修改失败", () -> adminService.updatePassword(body));
    }

    @PutMapping("/api/admin/user/status")
    public Map<String, Object> updateUserStatus(HttpServletRequest request,
                                                @RequestBody(required = false) Map<String, Object> body) {
        requireAdmin(request);
        return AdminService.guard("状态修改失败", () -> adminService.updateUserStatus(body));
    }

    // ============================================================
    // 删除班级 / 教师 / 学生 / 课程
    // ============================================================

    @DeleteMapping("/api/admin/class/{class_id}")
    public Map<String, Object> deleteClass(HttpServletRequest request,
                                           @PathVariable("class_id") String classId) {
        requireAdmin(request);
        return AdminService.guard("班级删除失败", () -> adminService.deleteClass(classId));
    }

    @DeleteMapping("/api/admin/teacher/{teacher_id}")
    public Map<String, Object> deleteTeacher(HttpServletRequest request,
                                             @PathVariable("teacher_id") String teacherId) {
        requireAdmin(request);
        return AdminService.guard("教师账户删除失败", () -> adminService.deleteTeacher(teacherId));
    }

    @DeleteMapping("/api/admin/student/{student_id}")
    public Map<String, Object> deleteStudent(HttpServletRequest request,
                                             @PathVariable("student_id") String studentId) {
        requireAdmin(request);
        return AdminService.guard("学生账户删除失败", () -> adminService.deleteStudent(studentId));
    }

    @DeleteMapping("/api/admin/course/{course_id}")
    public Map<String, Object> deleteCourse(HttpServletRequest request,
                                            @PathVariable("course_id") String courseId) {
        requireAdmin(request);
        return AdminService.guard("课程删除失败", () -> adminService.deleteCourse(courseId));
    }

    // ============================================================
    // 班级分配
    // ============================================================

    @PutMapping("/api/admin/student/class")
    public Map<String, Object> assignStudentClass(HttpServletRequest request,
                                                  @RequestBody(required = false) Map<String, Object> body) {
        requireAdmin(request);
        return AdminService.guard("学生班级分配失败", () -> adminService.assignStudentClass(body));
    }

    @PutMapping("/api/admin/teacher/class")
    public Map<String, Object> assignTeacherClass(HttpServletRequest request,
                                                  @RequestBody(required = false) Map<String, Object> body) {
        requireAdmin(request);
        return AdminService.guard("教师班级分配失败", () -> adminService.assignTeacherClass(body));
    }

    // ============================================================
    // 更新日志
    // ============================================================

    @GetMapping("/api/admin/updates")
    public Map<String, Object> listUpdates(HttpServletRequest request,
                                           @RequestParam(value = "keyword", required = false) String keyword) {
        requireAdmin(request);
        return AdminService.guard("获取更新日志失败", () -> adminService.listUpdates(keyword));
    }

    @PostMapping("/api/admin/updates")
    public Map<String, Object> createUpdate(HttpServletRequest request,
                                            @RequestBody(required = false) Map<String, Object> body) {
        requireAdmin(request);
        return AdminService.guard("新增更新日志失败", () -> adminService.createUpdate(body));
    }

    @PutMapping("/api/admin/updates/{update_id}")
    public Map<String, Object> updateUpdate(HttpServletRequest request,
                                            @PathVariable("update_id") long updateId,
                                            @RequestBody(required = false) Map<String, Object> body) {
        requireAdmin(request);
        return AdminService.guard("修改更新日志失败", () -> adminService.updateUpdate(updateId, body));
    }

    @DeleteMapping("/api/admin/updates/{update_id}")
    public Map<String, Object> deleteUpdate(HttpServletRequest request,
                                            @PathVariable("update_id") long updateId) {
        requireAdmin(request);
        return AdminService.guard("删除更新日志失败", () -> adminService.deleteUpdate(updateId));
    }
}
