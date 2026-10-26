package com.stu.signin.security;

import com.stu.signin.common.ApiException;
import com.stu.signin.common.RequestUtils;
import jakarta.servlet.http.HttpServletRequest;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

/**
 * 角色校验，对应 Python 的 core/auth_utils.py。
 *
 * 令牌解析结果由 JwtAuthFilter 放在 request attribute 里，
 * 这里只负责「没有身份 / 角色不符」时返回与 Python 完全一致的 401/403。
 */
@Component
public class AuthGuard {

    private static final Logger log = LoggerFactory.getLogger(AuthGuard.class);

    public static final String ATTR_USER_ID = "jwt.userId";
    public static final String ATTR_ROLE = "jwt.role";
    public static final String ATTR_REASON = "jwt.reason";
    public static final String ATTR_DETAIL = "jwt.detail";

    public record User(String userId, Integer role) {
    }

    /** 已认证用户（未认证时返回 userId=null） */
    public User current(HttpServletRequest request) {
        Object userId = request.getAttribute(ATTR_USER_ID);
        Object role = request.getAttribute(ATTR_ROLE);
        Integer parsedRole = role instanceof Integer i ? i : null;
        return new User(userId == null ? null : String.valueOf(userId), parsedRole);
    }

    /**
     * 校验当前登录用户角色
     *
     * role 1=学生 / 2=教师 / 3=管理员
     */
    public User require(HttpServletRequest request, int role, String message) {
        User user = current(request);

        if (user.userId() == null) {
            logFailure(request);
            throw new ApiException(401, unauthorizedMessage(request));
        }

        int currentRole = user.role() == null ? 0 : user.role();
        if (currentRole != role) {
            throw new ApiException(403, message);
        }

        return user;
    }

    /** 只要求登录、不限制角色 */
    public User requireLogin(HttpServletRequest request) {
        User user = current(request);
        if (user.userId() == null) {
            logFailure(request);
            throw new ApiException(401, unauthorizedMessage(request));
        }
        return user;
    }

    private String unauthorizedMessage(HttpServletRequest request) {
        Object reason = request.getAttribute(ATTR_REASON);
        if (JwtService.Reason.EXPIRED.name().equals(reason)) {
            return "登录已过期，请重新登录";
        }
        if (JwtService.Reason.INVALID.name().equals(reason)) {
            return "登录令牌无效";
        }
        return "未登录或缺少访问令牌";
    }

    private void logFailure(HttpServletRequest request) {
        Object reason = request.getAttribute(ATTR_REASON);
        Object detail = request.getAttribute(ATTR_DETAIL);

        String reasonText;
        if (JwtService.Reason.EXPIRED.name().equals(reason)) {
            reasonText = "令牌已过期 " + (detail == null ? "" : detail);
        } else if (JwtService.Reason.INVALID.name().equals(reason)) {
            reasonText = "令牌无效：" + (detail == null ? "未知原因" : detail);
        } else {
            reasonText = "未携带令牌（缺少 Authorization 头）";
        }

        String ip = RequestUtils.clientIp(request);
        String ua = truncate(request.getHeader("User-Agent"), 120);

        log.warn("JWT 校验失败 ip={} {} {} reason={} ua={}",
                ip, request.getMethod(), request.getRequestURI(), reasonText, ua);
    }

    private static String truncate(String value, int max) {
        if (value == null || value.isEmpty()) {
            return "-";
        }
        return value.length() > max ? value.substring(0, max) : value;
    }
}
