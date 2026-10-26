package com.stu.signin.auth;

import com.stu.signin.common.ApiException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
public class AuthController {

    private static final Logger log = LoggerFactory.getLogger(AuthController.class);

    private final AuthService authService;

    public AuthController(AuthService authService) {
        this.authService = authService;
    }

    /**
     * POST /api/auth/login
     *
     * student:  {"username":"20240001","password":"123456","device_id":"xxxx"}
     * teacher:  {"username":"teacher01","password":"123456","device_id":"xxxx"}
     */
    @PostMapping("/api/auth/login")
    public Map<String, Object> login(@RequestBody(required = false) Map<String, Object> data) {
        Map<String, Object> body = data == null ? Map.of() : data;

        String username = asText(body.get("username")).trim();
        String password = asText(body.get("password"));
        String deviceId = asText(body.get("device_id")).trim();

        if (username.isEmpty()) {
            throw new ApiException(400, "请输入账号");
        }
        if (password.isEmpty()) {
            throw new ApiException(400, "请输入密码");
        }
        if (deviceId.isEmpty()) {
            throw new ApiException(400, "设备标识不能为空");
        }

        try {
            return authService.login(username, password, deviceId);
        } catch (ApiException e) {
            throw e;
        } catch (Exception e) {
            log.error("登录接口错误", e);
            throw new ApiException(500, "服务器内部错误", String.valueOf(e.getMessage()));
        }
    }

    private static String asText(Object value) {
        return value == null ? "" : String.valueOf(value);
    }
}
