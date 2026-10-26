package com.stu.signin.security;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.stu.signin.config.AppProperties;
import org.springframework.stereotype.Service;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.Base64;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;

/**
 * JWT 生成与校验（HS256）。
 *
 * 与 flask-jwt-extended 的令牌格式保持一致：
 * header  {"alg":"HS256","typ":"JWT"}
 * payload {"sub","iat","nbf","jti","exp","type":"access","fresh":false,"role"}
 *
 * 注意：密钥沿用 Python 版的 'student-signin-jwt-secret-2026'（30 字节，
 * 不足 256 位），JJWT 会拒绝这种弱密钥，所以这里直接用 JDK 的 HmacSHA256 实现。
 */
@Service
public class JwtService {

    public enum Reason {
        EXPIRED, INVALID, MISSING
    }

    public static class JwtFailure extends Exception {
        private final Reason reason;

        public JwtFailure(Reason reason, String message) {
            super(message);
            this.reason = reason;
        }

        public Reason getReason() {
            return reason;
        }
    }

    public record ParsedToken(Map<String, Object> claims) {

        public String userId() {
            Object sub = claims.get("sub");
            return sub == null ? null : String.valueOf(sub);
        }

        public Integer role() {
            Object role = claims.get("role");
            if (role instanceof Number n) {
                return n.intValue();
            }
            if (role != null) {
                try {
                    return Integer.valueOf(String.valueOf(role));
                } catch (NumberFormatException ignored) {
                    return null;
                }
            }
            return null;
        }

        public Long exp() {
            Object exp = claims.get("exp");
            return exp instanceof Number n ? n.longValue() : null;
        }
    }

    private static final Base64.Encoder URL_ENCODER = Base64.getUrlEncoder().withoutPadding();
    private static final Base64.Decoder URL_DECODER = Base64.getUrlDecoder();

    private final ObjectMapper mapper;
    private final byte[] keyBytes;
    private final long expiresSeconds;

    public JwtService(AppProperties properties, ObjectMapper mapper) {
        this.mapper = mapper;
        this.keyBytes = properties.jwt().secret().getBytes(StandardCharsets.UTF_8);
        this.expiresSeconds = properties.jwt().expiresSeconds();
    }

    public String createAccessToken(String userId, int role) {
        long now = System.currentTimeMillis() / 1000L;

        Map<String, Object> header = new LinkedHashMap<>();
        header.put("alg", "HS256");
        header.put("typ", "JWT");

        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("sub", userId);
        payload.put("iat", now);
        payload.put("nbf", now);
        payload.put("jti", UUID.randomUUID().toString());
        payload.put("exp", now + expiresSeconds);
        payload.put("type", "access");
        payload.put("fresh", false);
        payload.put("role", role);

        try {
            String headerPart = URL_ENCODER.encodeToString(mapper.writeValueAsBytes(header));
            String payloadPart = URL_ENCODER.encodeToString(mapper.writeValueAsBytes(payload));
            String signingInput = headerPart + "." + payloadPart;
            return signingInput + "." + URL_ENCODER.encodeToString(sign(signingInput));
        } catch (Exception e) {
            throw new IllegalStateException("生成令牌失败", e);
        }
    }

    @SuppressWarnings("unchecked")
    public ParsedToken parse(String token) throws JwtFailure {
        if (token == null || token.isBlank()) {
            throw new JwtFailure(Reason.MISSING, "缺少令牌");
        }

        String[] parts = token.split("\\.", -1);
        if (parts.length != 3 || parts[0].isEmpty() || parts[1].isEmpty() || parts[2].isEmpty()) {
            throw new JwtFailure(Reason.INVALID, "令牌格式错误");
        }

        byte[] expected;
        try {
            expected = sign(parts[0] + "." + parts[1]);
        } catch (Exception e) {
            throw new JwtFailure(Reason.INVALID, "令牌签名计算失败");
        }

        byte[] actual;
        try {
            actual = URL_DECODER.decode(parts[2]);
        } catch (IllegalArgumentException e) {
            throw new JwtFailure(Reason.INVALID, "令牌签名编码错误");
        }

        if (!MessageDigest.isEqual(expected, actual)) {
            throw new JwtFailure(Reason.INVALID, "签名验证失败");
        }

        Map<String, Object> claims;
        try {
            claims = mapper.readValue(URL_DECODER.decode(parts[1]), Map.class);
        } catch (Exception e) {
            throw new JwtFailure(Reason.INVALID, "令牌内容解析失败");
        }

        long now = System.currentTimeMillis() / 1000L;

        Object nbf = claims.get("nbf");
        if (nbf instanceof Number n && n.longValue() > now) {
            throw new JwtFailure(Reason.INVALID, "令牌尚未生效");
        }

        Object exp = claims.get("exp");
        if (exp instanceof Number n && n.longValue() < now) {
            throw new JwtFailure(Reason.EXPIRED, "令牌已过期");
        }

        if (claims.get("sub") == null) {
            throw new JwtFailure(Reason.INVALID, "令牌缺少 sub");
        }

        return new ParsedToken(claims);
    }

    private byte[] sign(String input) throws Exception {
        Mac mac = Mac.getInstance("HmacSHA256");
        mac.init(new SecretKeySpec(keyBytes, "HmacSHA256"));
        return mac.doFinal(input.getBytes(StandardCharsets.UTF_8));
    }
}
