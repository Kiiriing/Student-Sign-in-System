package com.stu.signin.security;

import org.bouncycastle.crypto.generators.SCrypt;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;

/**
 * 校验 werkzeug 生成的密码哈希（数据库里存的是 scrypt:32768:8:1$salt$hash）。
 *
 * 同时兼容旧版 werkzeug 的 pbkdf2:sha256 / pbkdf2:sha1 格式。
 */
@Component
public class PasswordVerifier {

    public boolean matches(String stored, String password) {
        if (stored == null || password == null || stored.isEmpty()) {
            return false;
        }

        try {
            if (stored.startsWith("scrypt:")) {
                return matchesScrypt(stored, password);
            }
            if (stored.startsWith("pbkdf2:")) {
                return matchesPbkdf2(stored, password);
            }
        } catch (Exception e) {
            return false;
        }

        return false;
    }

    private boolean matchesScrypt(String stored, String password) {
        String[] parts = stored.split("\\$", -1);
        if (parts.length != 3) {
            return false;
        }

        String[] method = parts[0].split(":");
        if (method.length != 4) {
            return false;
        }

        int n = Integer.parseInt(method[1]);
        int r = Integer.parseInt(method[2]);
        int p = Integer.parseInt(method[3]);

        byte[] salt = parts[1].getBytes(StandardCharsets.US_ASCII);
        byte[] expected = hexToBytes(parts[2]);
        if (expected.length == 0) {
            return false;
        }

        byte[] actual = SCrypt.generate(password.getBytes(StandardCharsets.UTF_8), salt, n, r, p, expected.length);
        return MessageDigest.isEqual(expected, actual);
    }

    private boolean matchesPbkdf2(String stored, String password) throws Exception {
        String[] parts = stored.split("\\$", -1);
        if (parts.length != 3) {
            return false;
        }

        String[] method = parts[0].split(":");
        String hashName = method.length > 1 ? method[1].toLowerCase() : "sha256";

        int iterations;
        if (method.length > 2) {
            iterations = Integer.parseInt(method[2]);
        } else {
            iterations = "sha256".equals(hashName) ? 600_000 : 1_000;
        }

        String algorithm = "sha1".equals(hashName) ? "PBKDF2WithHmacSHA1" : "PBKDF2WithHmacSHA256";
        byte[] salt = parts[1].getBytes(StandardCharsets.US_ASCII);
        byte[] expected = hexToBytes(parts[2]);
        if (expected.length == 0) {
            return false;
        }

        PBEKeySpec spec = new PBEKeySpec(password.toCharArray(), salt, iterations, expected.length * 8);
        byte[] actual = SecretKeyFactory.getInstance(algorithm).generateSecret(spec).getEncoded();
        return MessageDigest.isEqual(expected, actual);
    }

    private static byte[] hexToBytes(String hex) {
        int length = hex.length();
        if (length % 2 != 0) {
            return new byte[0];
        }
        byte[] out = new byte[length / 2];
        for (int i = 0; i < out.length; i++) {
            int hi = Character.digit(hex.charAt(i * 2), 16);
            int lo = Character.digit(hex.charAt(i * 2 + 1), 16);
            if (hi < 0 || lo < 0) {
                return new byte[0];
            }
            out[i] = (byte) ((hi << 4) | lo);
        }
        return out;
    }
}
