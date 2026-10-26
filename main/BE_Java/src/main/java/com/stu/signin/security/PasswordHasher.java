package com.stu.signin.security;

import org.bouncycastle.crypto.generators.SCrypt;
import org.springframework.stereotype.Component;

import java.nio.charset.StandardCharsets;
import java.security.SecureRandom;

/**
 * 生成与 werkzeug.security.generate_password_hash 默认格式一致的密码哈希：
 *
 *   scrypt:32768:8:1$<salt_hex>$<hash_hex>
 *
 * Flask 版新建账号 / 改密码写入的都是这种格式，Java 版必须保持一致，
 * 否则前后端切换后旧账号无法登录。
 */
@Component
public class PasswordHasher {

    private static final int N = 32768;
    private static final int R = 8;
    private static final int P = 1;
    private static final int DK_LEN = 64;
    private static final int SALT_BYTES = 16;

    private final SecureRandom random = new SecureRandom();

    public String generate(String password) {
        byte[] saltBytes = new byte[SALT_BYTES];
        random.nextBytes(saltBytes);
        String salt = hex(saltBytes);

        byte[] hash = SCrypt.generate(password.getBytes(StandardCharsets.UTF_8),
                salt.getBytes(StandardCharsets.US_ASCII), N, R, P, DK_LEN);

        return "scrypt:" + N + ":" + R + ":" + P + "$" + salt + "$" + hex(hash);
    }

    private static String hex(byte[] bytes) {
        StringBuilder builder = new StringBuilder(bytes.length * 2);
        for (byte value : bytes) {
            builder.append(Character.forDigit((value >> 4) & 0xF, 16));
            builder.append(Character.forDigit(value & 0xF, 16));
        }
        return builder.toString();
    }
}
