package com.stu.signin.logging;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.stu.signin.common.RequestUtils;
import com.stu.signin.security.AuthGuard;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;
import org.springframework.web.util.ContentCachingRequestWrapper;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

/**
 * 请求日志：每个 /api 请求记录方法、路径、状态码、耗时、用户、IP、UA、请求体，
 * 并按 Python 版规则标注爬虫特征。日志输出走 Java 日志框架（logback）。
 */
@Component
@Order(1)
public class RequestLogFilter extends OncePerRequestFilter {

    private static final Logger log = LoggerFactory.getLogger(RequestLogFilter.class);
    private static final int LOG_BODY_MAX = 500;

    private final CrawlerDetector crawlerDetector;
    private final ObjectMapper mapper;

    public RequestLogFilter(CrawlerDetector crawlerDetector, ObjectMapper mapper) {
        this.crawlerDetector = crawlerDetector;
        this.mapper = mapper;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain chain)
            throws ServletException, IOException {

        ContentCachingRequestWrapper wrapped = new ContentCachingRequestWrapper(request, 64 * 1024);
        long start = System.nanoTime();

        try {
            chain.doFilter(wrapped, response);
        } finally {
            try {
                writeLog(wrapped, response, start);
            } catch (Exception e) {
                log.error("请求日志记录失败", e);
            }
        }
    }

    private void writeLog(ContentCachingRequestWrapper request, HttpServletResponse response, long startNanos) {
        String method = request.getMethod();
        String path = request.getRequestURI();

        if (!path.startsWith("/api") || "OPTIONS".equalsIgnoreCase(method)) {
            return;
        }

        long elapsed = Math.max(0L, (System.nanoTime() - startNanos) / 1_000_000L);

        Object userIdAttr = request.getAttribute(AuthGuard.ATTR_USER_ID);
        String userId = userIdAttr == null ? "-" : String.valueOf(userIdAttr);

        String ip = RequestUtils.clientIp(request);
        String ua = request.getHeader("User-Agent");
        int status = response.getStatus();

        String body = "-";
        JsonNode parsedBody = null;

        if ("POST".equals(method) || "PUT".equals(method) || "PATCH".equals(method)) {
            if (!"/api/sync/import".equals(path)) {
                byte[] raw = request.getContentAsByteArray();
                if (raw.length > 0) {
                    String text = new String(raw, StandardCharsets.UTF_8);
                    try {
                        JsonNode parsed = mapper.readTree(text);
                        parsedBody = parsed;
                        if (parsed.isObject()) {
                            ObjectNode masked = parsed.deepCopy();
                            List<String> keys = new ArrayList<>();
                            Iterator<String> names = masked.fieldNames();
                            while (names.hasNext()) {
                                keys.add(names.next());
                            }
                            for (String key : keys) {
                                String lower = key.toLowerCase();
                                if (lower.contains("password") || lower.contains("pwd")) {
                                    masked.put(key, "***");
                                }
                            }
                            body = mapper.writeValueAsString(masked);
                        } else {
                            body = text;
                        }
                    } catch (Exception e) {
                        body = text;
                    }
                }
            }

            if (body.length() > LOG_BODY_MAX) {
                body = body.substring(0, LOG_BODY_MAX) + "...(截断)";
            }
        }

        String crawlerFlag = crawlerDetector.detect(ip, path, ua, body, parsedBody, request);

        String uaText = ua == null || ua.isEmpty() ? "-" : ua;
        if (uaText.length() > 120) {
            uaText = uaText.substring(0, 120);
        }

        String message = "{} {} status={} user={} ip={} time={}ms ua=\"{}\" body={}";
        if (!crawlerFlag.isEmpty()) {
            message = message + " crawler=" + crawlerFlag;
        }

        if (status >= 500) {
            log.error(message, method, path, status, userId, ip, elapsed, uaText, body);
        } else if (status >= 400 || !crawlerFlag.isEmpty()) {
            log.warn(message, method, path, status, userId, ip, elapsed, uaText, body);
        } else {
            log.info(message, method, path, status, userId, ip, elapsed, uaText, body);
        }
    }
}
