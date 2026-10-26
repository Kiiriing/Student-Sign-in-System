package com.stu.signin.common;

/**
 * 带 HTTP 状态码的业务异常。
 *
 * 由 GlobalExceptionHandler 统一转换成 {"code","message"[,"error"]} 响应，
 * 对应 Python 版里 return jsonify({...}), 状态码 的写法。
 */
public class ApiException extends RuntimeException {

    private final int status;
    private final String error;

    public ApiException(int status, String message) {
        this(status, message, null);
    }

    public ApiException(int status, String message, String error) {
        super(message);
        this.status = status;
        this.error = error;
    }

    public int getStatus() {
        return status;
    }

    public String getError() {
        return error;
    }
}
