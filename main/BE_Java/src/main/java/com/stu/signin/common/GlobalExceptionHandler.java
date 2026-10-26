package com.stu.signin.common;

import jakarta.servlet.http.HttpServletRequest;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.HttpRequestMethodNotSupportedException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.servlet.NoHandlerFoundException;
import org.springframework.web.servlet.resource.NoResourceFoundException;

import java.sql.SQLTransientConnectionException;
import java.util.Map;

@RestControllerAdvice
public class GlobalExceptionHandler {

    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    @ExceptionHandler(ApiException.class)
    public ResponseEntity<Map<String, Object>> handleApi(ApiException e, HttpServletRequest request) {
        Map<String, Object> body = Api.message(e.getStatus(), e.getMessage());
        if (e.getError() != null) {
            body.put("error", e.getError());
        }
        return ResponseEntity.status(e.getStatus()).body(body);
    }

    /**
     * 连接池排队超时 → 503（服务暂不可用），对应 Python 的 DBPoolBusyError
     */
    @ExceptionHandler(SQLTransientConnectionException.class)
    public ResponseEntity<Map<String, Object>> handlePoolBusy(SQLTransientConnectionException e) {
        log.warn("数据库连接池繁忙：{}", e.getMessage());
        return ResponseEntity.status(503).body(Api.message(503, "服务繁忙，请稍后重试"));
    }

    @ExceptionHandler({NoHandlerFoundException.class, NoResourceFoundException.class})
    public ResponseEntity<Map<String, Object>> handleNotFound(Exception e) {
        return ResponseEntity.status(404).body(Api.message(404, "请求接口不存在"));
    }

    @ExceptionHandler(HttpRequestMethodNotSupportedException.class)
    public ResponseEntity<Map<String, Object>> handleMethod(HttpRequestMethodNotSupportedException e) {
        return ResponseEntity.status(405).body(Api.message(405, "请求方法不允许"));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<Map<String, Object>> handleOther(Exception e, HttpServletRequest request) {
        log.error("未处理异常 {} {}", request.getMethod(), request.getRequestURI(), e);
        return ResponseEntity.status(500).body(Api.message(500, "服务器内部错误"));
    }
}
