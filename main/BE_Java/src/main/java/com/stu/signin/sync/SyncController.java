package com.stu.signin.sync;

import com.stu.signin.common.Api;
import com.stu.signin.common.ApiException;
import com.stu.signin.common.DbValues;
import com.stu.signin.security.AuthGuard;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * 跨站同步接口层，对应 Python sync/api.py 的对外部分。
 *
 * 契约式 4 个接口用 X-Sync-Token 鉴权；快照式 3 个接口无令牌、无统一外壳，
 * 直接收发裸 JSON（与 A 站约定一致）。
 */
@RestController
public class SyncController {

    private static final DateTimeFormatter TIME_FORMAT = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
    private static final DateTimeFormatter FILE_STAMP = DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss");

    private final SyncConfig config;
    private final SyncStore store;
    private final SnapshotService snapshotService;
    private final SyncWorker worker;
    private final AuthGuard authGuard;

    public SyncController(SyncConfig config, SyncStore store, SnapshotService snapshotService,
                          SyncWorker worker, AuthGuard authGuard) {
        this.config = config;
        this.store = store;
        this.snapshotService = snapshotService;
        this.worker = worker;
        this.authGuard = authGuard;
    }

    // ============================================================
    // 工具
    // ============================================================

    private SyncConfig.SyncPeer requirePeer(String token) {
        SyncConfig.SyncPeer peer = config.getPeerByToken(token);
        if (peer == null) {
            throw new ApiException(401, "同步令牌无效");
        }
        return peer;
    }

    private static int toInt(Object value, int fallback) {
        try {
            return Integer.parseInt(String.valueOf(value).trim());
        } catch (Exception e) {
            return fallback;
        }
    }

    // ============================================================
    // 对端接口
    // ============================================================

    @GetMapping("/api/sync/health")
    public Map<String, Object> health() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("site_code", config.siteCode());
        data.put("site_name", config.siteName());
        data.put("schema_version", SyncContract.SCHEMA_VERSION);
        data.put("server_time", LocalDateTime.now().format(TIME_FORMAT));

        return Api.body("code", 200, "message", "ok", "data", data);
    }

    @GetMapping("/api/sync/export")
    public ResponseEntity<Map<String, Object>> export() {
        try {
            return ResponseEntity.ok(snapshotService.buildSnapshot());
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of("detail", "导出失败：" + e.getMessage()));
        }
    }

    @GetMapping("/api/sync/download")
    public ResponseEntity<Map<String, Object>> download() {
        Map<String, Object> snapshot;
        try {
            snapshot = snapshotService.buildSnapshot();
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of("detail", "导出失败：" + e.getMessage()));
        }

        String filename = "checkin_sync_" + LocalDateTime.now().format(FILE_STAMP) + ".json";

        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename*=UTF-8''" + filename)
                .contentType(MediaType.APPLICATION_JSON)
                .body(snapshot);
    }

    @PostMapping("/api/sync/import")
    @SuppressWarnings("unchecked")
    public ResponseEntity<Map<String, Object>> importSnapshot(@RequestBody(required = false) Object body) {
        if (!(body instanceof Map<?, ?> map)) {
            return ResponseEntity.status(422).body(Map.of("detail", "请求体不是 JSON 对象"));
        }

        Map<String, Object> result;
        try {
            result = snapshotService.importSnapshot((Map<String, Object>) map, SyncConfig.SNAPSHOT_DEFAULT_ORIGIN);
        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of("detail", "写入同步表失败：" + e.getMessage()));
        }

        if (DbValues.intValue(result.get("created_records")) > 0) {
            worker.triggerSync();
        }

        return ResponseEntity.ok(result);
    }

    @PostMapping("/api/sync/inbound/push")
    public Map<String, Object> inboundPush(
            @RequestHeader(value = "X-Sync-Token", required = false) String token,
            @RequestBody(required = false) Map<String, Object> body) {

        requirePeer(token);

        Object events = body == null ? null : body.get("events");
        if (!(events instanceof List<?> list)) {
            throw new ApiException(400, "events 必须是数组");
        }

        List<Map<String, Object>> eventList = new ArrayList<>();
        for (Object item : list) {
            if (item instanceof Map<?, ?> map) {
                @SuppressWarnings("unchecked")
                Map<String, Object> event = (Map<String, Object>) map;
                eventList.add(event);
            } else {
                eventList.add(null);
            }
        }

        SyncStore.IngestResult result;
        try {
            result = store.ingestEvents(eventList);
        } catch (Exception e) {
            throw new ApiException(500, "写入同步表失败", String.valueOf(e.getMessage()));
        }

        if (!result.accepted().isEmpty()) {
            worker.triggerSync();
        }

        return Api.body("code", 200, "message", "接收完成", "data", result.toMap());
    }

    @GetMapping("/api/sync/inbound/pull")
    public Map<String, Object> inboundPull(
            @RequestHeader(value = "X-Sync-Token", required = false) String token,
            @RequestParam(value = "since", required = false) String sinceArg,
            @RequestParam(value = "limit", required = false) String limitArg) {

        SyncConfig.SyncPeer peer = requirePeer(token);

        long since = 0L;
        try {
            since = Long.parseLong(String.valueOf(sinceArg == null ? "0" : sinceArg).trim());
        } catch (Exception ignored) {
            since = 0L;
        }

        int limit = toInt(limitArg == null ? 200 : limitArg, 200);
        limit = Math.max(1, Math.min(limit, 500));

        SyncStore.OutboundBatch batch = store.fetchOutboundBatch(peer.code(), since, limit);

        Map<String, Object> data = new LinkedHashMap<>();
        data.put("events", batch.events());
        data.put("next_cursor", batch.nextCursor());
        data.put("has_more", batch.events().size() >= limit);

        return Api.body("code", 200, "message", "ok", "data", data);
    }

    @PostMapping("/api/sync/check-dup")
    public Map<String, Object> checkDup(
            @RequestHeader(value = "X-Sync-Token", required = false) String token,
            @RequestBody(required = false) Map<String, Object> body) {

        requirePeer(token);

        Map<String, Object> data = body == null ? Map.of() : body;

        String studentNo = SyncContract.normalizeText(data.get("student_no"));
        String alignKey = SyncContract.normalizeText(data.get("align_key"));

        if (alignKey.isEmpty()) {
            Object period = data.get("period");
            if (SyncContract.normalizeText(period).isEmpty()) {
                period = data.get("time_slot");
            }
            alignKey = SyncContract.buildAlignKey(data.get("student_no"), data.get("class_name"),
                    data.get("course_date"), SyncContract.normalizePeriod(period));
        }

        if (studentNo.isEmpty() || alignKey.isEmpty()) {
            throw new ApiException(400, "student_no 与对齐键不能为空");
        }

        String sourceSite = null;
        String signTime = null;
        String courseName = null;

        // 1) 本站自己的签到记录
        Map<String, Object> local = store.findLocalDuplicate(studentNo, alignKey);
        if (local != null) {
            sourceSite = config.siteCode();
            signTime = DbValues.dateTime(local.get("sign_time"));
            courseName = DbValues.text(local.get("course_name"));
        }

        // 2) 本站已同步到的第三站记录
        if (sourceSite == null) {
            Map<String, Object> cross = store.findCrossDuplicate(studentNo, alignKey);
            if (cross != null) {
                sourceSite = DbValues.text(cross.get("origin_site"));
                signTime = DbValues.dateTime(cross.get("sign_time"));
                courseName = DbValues.text(cross.get("course_name"));
            }
        }

        if (sourceSite != null) {
            Map<String, String> names = config.peerNames();
            String sourceSiteName = names.getOrDefault(sourceSite, config.siteName());

            Map<String, Object> hit = new LinkedHashMap<>();
            hit.put("duplicated", true);
            hit.put("source_site", sourceSite);
            hit.put("source_site_name", sourceSiteName);
            hit.put("sign_time", signTime);
            hit.put("course_name", courseName);
            return Api.body("code", 200, "message", "ok", "data", hit);
        }

        Map<String, Object> miss = new LinkedHashMap<>();
        miss.put("duplicated", false);
        miss.put("source_site", null);
        miss.put("sign_time", null);
        miss.put("course_name", null);
        return Api.body("code", 200, "message", "ok", "data", miss);
    }

    @PostMapping("/api/sync/reconcile")
    public Map<String, Object> reconcile(HttpServletRequest request) {
        authGuard.require(request, 3, "无管理员权限");

        Map<String, Object> stats;
        try {
            stats = store.reconcile();
        } catch (Exception e) {
            throw new ApiException(500, "对账失败", String.valueOf(e.getMessage()));
        }

        return Api.body("code", 200, "message", "对账完成", "data", stats);
    }
}
