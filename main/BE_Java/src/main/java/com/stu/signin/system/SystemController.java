package com.stu.signin.system;

import com.stu.signin.common.ApiException;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
public class SystemController {

    private final SystemService systemService;

    public SystemController(SystemService systemService) {
        this.systemService = systemService;
    }

    /** GET /api/system/updates?page=1 —— 无需登录 */
    @GetMapping("/api/system/updates")
    public Map<String, Object> updates(@RequestParam(value = "page", required = false) String page) {
        try {
            return systemService.listUpdates(page);
        } catch (Exception e) {
            throw new ApiException(500, "获取更新日志失败", String.valueOf(e.getMessage()));
        }
    }
}
