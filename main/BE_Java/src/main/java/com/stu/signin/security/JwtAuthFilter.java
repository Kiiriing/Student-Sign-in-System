package com.stu.signin.security;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;

/**
 * 解析 Authorization: Bearer <token>，把身份放进 request attribute。
 *
 * 不在这里直接拒绝请求：公开接口（登录、更新日志、跨站同步）即使带着
 * 过期令牌也应当正常工作，由各 Controller 通过 AuthGuard 决定是否要求登录。
 */
@Component
@Order(2)
public class JwtAuthFilter extends OncePerRequestFilter {

    private final JwtService jwtService;

    public JwtAuthFilter(JwtService jwtService) {
        this.jwtService = jwtService;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain chain)
            throws ServletException, IOException {

        String header = request.getHeader("Authorization");

        if (header != null && header.regionMatches(true, 0, "Bearer ", 0, 7)) {
            String token = header.substring(7).trim();
            try {
                JwtService.ParsedToken parsed = jwtService.parse(token);
                request.setAttribute(AuthGuard.ATTR_USER_ID, parsed.userId());
                if (parsed.role() != null) {
                    request.setAttribute(AuthGuard.ATTR_ROLE, parsed.role());
                }
            } catch (JwtService.JwtFailure e) {
                request.setAttribute(AuthGuard.ATTR_REASON, e.getReason().name());
                request.setAttribute(AuthGuard.ATTR_DETAIL, e.getMessage());
            }
        }

        chain.doFilter(request, response);
    }
}
