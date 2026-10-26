package com.stu.signin.common;

import java.util.LinkedHashMap;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * 统一响应体构造工具。
 *
 * Python 版全部接口返回 {"code": ..., "message": ...} 结构的 JSON，
 * 这里用 LinkedHashMap 保证字段顺序稳定、null 字段照常输出。
 */
public final class Api {

    private static final Logger log = LoggerFactory.getLogger(Api.class);

    private Api() {
    }

    public static Map<String, Object> body(Object... keyValues) {
        LinkedHashMap<String, Object> map = new LinkedHashMap<>();
        for (int i = 0; i + 1 < keyValues.length; i += 2) {
            map.put(String.valueOf(keyValues[i]), keyValues[i + 1]);
        }
        return map;
    }

    public static Map<String, Object> message(int code, String message) {
        return body("code", code, "message", message);
    }

    /**
     * 与 Python 各接口 try/except 保持一致的异常收敛：
     * 业务异常原样抛出，其它异常转换成 500 + 失败描述 + error 详情。
     */
    public static <T> T guard(String failMessage, java.util.function.Supplier<T> task) {
        try {
            return task.get();
        } catch (ApiException e) {
            throw e;
        } catch (Exception e) {
            log.error(failMessage, e);
            throw new ApiException(500, failMessage, String.valueOf(e.getMessage()));
        }
    }
}
