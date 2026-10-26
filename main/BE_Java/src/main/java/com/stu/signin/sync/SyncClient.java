package com.stu.signin.sync;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.stereotype.Component;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.http.HttpTimeoutException;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.Map;

/**
 * 出站 HTTP 客户端，对应 Python sync/client.py。
 *
 * 用 JDK 的 HttpClient（HTTP/1.1），不复用第三方库；
 * 异常文案尽量贴近 Python 版，便于沿用同一套排查话术。
 */
@Component
public class SyncClient {

    public static class SyncHttpException extends RuntimeException {
        public SyncHttpException(String message) {
            super(message);
        }
    }

    private final ObjectMapper mapper;
    private final HttpClient httpClient;

    public SyncClient(ObjectMapper mapper) {
        this.mapper = mapper;
        this.httpClient = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(3))
                .version(HttpClient.Version.HTTP_1_1)
                .build();
    }

    public JsonNode requestJson(String method, String url, String token, Object payload, double timeoutSeconds) {
        try {
            HttpRequest.Builder builder = HttpRequest.newBuilder(URI.create(url))
                    .timeout(Duration.ofMillis(Math.max(1L, (long) (timeoutSeconds * 1000))))
                    .header("Accept", "application/json");

            if (payload != null) {
                String requestBody = mapper.writeValueAsString(payload);
                builder.header("Content-Type", "application/json; charset=utf-8");
                builder.method(method, HttpRequest.BodyPublishers.ofString(requestBody, StandardCharsets.UTF_8));
            } else {
                builder.method(method, HttpRequest.BodyPublishers.noBody());
            }

            if (token != null && !token.isEmpty()) {
                builder.header("X-Sync-Token", token);
            }

            HttpResponse<String> response = httpClient.send(builder.build(),
                    HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8));

            int status = response.statusCode();
            String body = response.body() == null ? "" : response.body();

            if (status < 200 || status >= 300) {
                throw new SyncHttpException("HTTP " + status + " " + cleanText(body).substring(0,
                        Math.min(cleanText(body).length(), 200)));
            }

            if (body.isBlank()) {
                return mapper.createObjectNode();
            }

            try {
                return mapper.readTree(body);
            } catch (Exception e) {
                throw new SyncHttpException("响应不是合法 JSON：" + body.substring(0, Math.min(body.length(), 200)));
            }
        } catch (SyncHttpException e) {
            throw e;
        } catch (HttpTimeoutException e) {
            throw new SyncHttpException("网络不可达或超时：" + cleanText(e.getMessage()));
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new SyncHttpException("请求异常：请求被中断");
        } catch (Exception e) {
            if (isTimeout(e)) {
                throw new SyncHttpException("网络不可达或超时：" + cleanText(e.getMessage()));
            }
            throw new SyncHttpException("请求异常：" + cleanText(e.getMessage()));
        }
    }

    private static boolean isTimeout(Throwable e) {
        Throwable current = e;
        while (current != null) {
            if (current instanceof java.net.http.HttpTimeoutException
                    || current instanceof java.net.SocketTimeoutException
                    || current instanceof java.util.concurrent.TimeoutException) {
                return true;
            }
            current = current.getCause();
        }
        return false;
    }

    public JsonNode postJson(String url, Object payload, String token, double timeoutSeconds) {
        return requestJson("POST", url, token, payload, timeoutSeconds);
    }

    public JsonNode getJson(String url, String token, double timeoutSeconds) {
        return requestJson("GET", url, token, null, timeoutSeconds);
    }

    public static String joinUrl(String baseUrl, String path) {
        String base = baseUrl == null ? "" : baseUrl;
        while (base.endsWith("/")) {
            base = base.substring(0, base.length() - 1);
        }
        return base + path;
    }

    /** 剔除原始响应字节解码出来的不可打印字符 */
    private static String cleanText(String value) {
        if (value == null) {
            return "";
        }
        StringBuilder out = new StringBuilder();
        for (int i = 0; i < value.length(); i++) {
            char ch = value.charAt(i);
            if (ch == '\r' || ch == '\n' || ch == '\t' || (ch >= 0x20 && ch <= 0x7E) || ch >= 0x2E80) {
                out.append(ch);
            }
        }
        return out.toString().trim();
    }

    @SuppressWarnings("unchecked")
    public Map<String, Object> asMap(JsonNode node) {
        if (node == null || node.isNull() || !node.isObject()) {
            return null;
        }
        return mapper.convertValue(node, Map.class);
    }
}
