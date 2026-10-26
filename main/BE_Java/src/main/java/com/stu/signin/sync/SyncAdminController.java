package com.stu.signin.sync;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.stu.signin.common.Api;
import com.stu.signin.common.ApiException;
import com.stu.signin.common.DbValues;
import com.stu.signin.security.AuthGuard;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

/**
 * 同步管理接口，对应 Python sync/api.py 的管理员部分（走 JWT）。
 *
 * 对端连通性探测做并发 + 5 秒缓存 + 后台异步刷新：
 * 探测不可达对端最坏要等 1.2 秒，绝不能放在请求路径上等。
 */
@RestController
public class SyncAdminController {

    private static final long PEER_PROBE_TTL_MILLIS = 5_000L;

    private final SyncConfig config;
    private final SyncStore store;
    private final SyncWorker worker;
    private final AuthGuard authGuard;
    private final SyncClient client;
    private final ObjectMapper mapper;

    private final Object probeLock = new Object();
    private List<Map<String, Object>> probeCache;
    private long probeTime;
    private boolean refreshing;

    public SyncAdminController(SyncConfig config, SyncStore store, SyncWorker worker,
                               AuthGuard authGuard, SyncClient client, ObjectMapper mapper) {
        this.config = config;
        this.store = store;
        this.worker = worker;
        this.authGuard = authGuard;
        this.client = client;
        this.mapper = mapper;
    }

    // ============================================================
    // 对端探测
    // ============================================================

    private Map<String, Object> probePeer(SyncConfig.SyncPeer peer) {
        Map<String, Object> item = new LinkedHashMap<>();
        item.put("code", peer.code());
        item.put("name", peer.name());
        item.put("base_url", peer.baseUrl());
        item.put("online", false);
        item.put("site_name", null);
        item.put("server_time", null);
        item.put("error", null);

        if (SyncConfig.PROTOCOL_SNAPSHOT.equals(config.peerProtocol(peer))) {
            String url = SyncClient.joinUrl(peer.baseUrl(), "/api/sync/export");
            try {
                JsonNode snapshot = client.getJson(url, null, SyncConfig.SNAPSHOT_TIMEOUT);
                if (snapshot != null && snapshot.isObject()) {
                    item.put("online", true);
                    item.put("site_name", peer.name());
                    item.put("server_time", snapshot.path("exported_at").asText(null));
                } else {
                    item.put("error", "导出接口未返回快照 JSON");
                }
            } catch (Exception e) {
                item.put("error", e.getMessage());
            }
            return item;
        }

        String url = SyncClient.joinUrl(peer.baseUrl(), "/api/sync/health");
        try {
            JsonNode response = client.getJson(url, peer.token(), SyncConfig.CHECK_TIMEOUT);
            JsonNode data = response == null ? null : response.get("data");
            item.put("online", true);
            item.put("site_name", data == null ? null : data.path("site_name").asText(null));
            item.put("server_time", data == null ? null : data.path("server_time").asText(null));
        } catch (Exception e) {
            item.put("error", e.getMessage());
        }
        return item;
    }

    private List<Map<String, Object>> probeAllPeers() {
        List<SyncConfig.SyncPeer> peers = config.peers();
        if (peers.isEmpty()) {
            return List.of();
        }

        ExecutorService pool = Executors.newFixedThreadPool(Math.min(peers.size(), 8));
        try {
            List<Future<Map<String, Object>>> futures = new ArrayList<>();
            for (SyncConfig.SyncPeer peer : peers) {
                futures.add(pool.submit(() -> probePeer(peer)));
            }

            List<Map<String, Object>> result = new ArrayList<>();
            for (Future<Map<String, Object>> future : futures) {
                result.add(future.get());
            }
            return result;
        } catch (Exception e) {
            return List.of();
        } finally {
            pool.shutdown();
        }
    }

    private List<Map<String, Object>> peersStatus() {
        synchronized (probeLock) {
            if (probeCache != null) {
                if (System.currentTimeMillis() - probeTime < PEER_PROBE_TTL_MILLIS) {
                    return probeCache;
                }
                if (!refreshing) {
                    refreshing = true;
                    Thread thread = new Thread(this::refreshPeers, "sync-peer-probe");
                    thread.setDaemon(true);
                    thread.start();
                }
                return probeCache;
            }
        }

        List<Map<String, Object>> data = probeAllPeers();

        synchronized (probeLock) {
            probeTime = System.currentTimeMillis();
            probeCache = data;
        }
        return data;
    }

    private void refreshPeers() {
        List<Map<String, Object>> data = null;
        try {
            data = probeAllPeers();
        } catch (Exception ignored) {
            // 保留旧缓存
        }

        synchronized (probeLock) {
            if (data != null) {
                probeTime = System.currentTimeMillis();
                probeCache = data;
            }
            refreshing = false;
        }
    }

    // ============================================================
    // 工具
    // ============================================================

    private static Object normalizeValue(Object value) {
        if (value == null) {
            return null;
        }
        if (value instanceof LocalDate || value instanceof java.sql.Date) {
            return DbValues.date(value);
        }
        if (value instanceof LocalDateTime || value instanceof java.sql.Timestamp
                || value instanceof java.util.Date) {
            return DbValues.dateTime(value);
        }
        return value;
    }

    private static Map<String, Object> rowToDict(Map<String, Object> row) {
        if (row == null) {
            return null;
        }
        Map<String, Object> result = new LinkedHashMap<>();
        for (Map.Entry<String, Object> entry : row.entrySet()) {
            result.put(entry.getKey(), normalizeValue(entry.getValue()));
        }
        return result;
    }

    private static int toInt(Object value, int fallback) {
        try {
            return Integer.parseInt(String.valueOf(value).trim());
        } catch (Exception e) {
            return fallback;
        }
    }

    // ============================================================
    // 接口
    // ============================================================

    @GetMapping("/api/admin/sync/status")
    public Map<String, Object> status(HttpServletRequest request) {
        authGuard.require(request, 3, "无管理员权限");

        List<Map<String, Object>> peersStatus = peersStatus();

        Map<String, Map<String, Object>> cursors = new LinkedHashMap<>();
        for (Map.Entry<String, Map<String, Object>> entry : store.cursorSnapshot().entrySet()) {
            cursors.put(entry.getKey(), rowToDict(entry.getValue()));
        }

        Map<String, Object> data = new LinkedHashMap<>();
        data.put("site_code", config.siteCode());
        data.put("site_name", config.siteName());
        data.put("schema_version", SyncContract.SCHEMA_VERSION);
        data.put("peers", peersStatus);
        data.put("cursors", cursors);
        data.put("outbox", store.outboxStats());
        data.put("pending_outbox", store.countPendingOutbox());
        data.put("pending_conflicts", store.countPendingConflicts());
        data.put("cross_record", store.crossRecordCount());

        return Api.body("code", 200, "message", "ok", "data", data);
    }

    @GetMapping("/api/admin/sync/outbox")
    public Map<String, Object> outbox(
            HttpServletRequest request,
            @RequestParam(value = "status", required = false) String statusArg,
            @RequestParam(value = "limit", required = false) String limitArg) {

        authGuard.require(request, 3, "无管理员权限");

        Integer status = null;
        if (statusArg != null && !statusArg.isEmpty() && !"all".equals(statusArg)) {
            try {
                status = Integer.parseInt(statusArg.trim());
            } catch (NumberFormatException ignored) {
                status = null;
            }
        }

        int limit = Math.max(1, Math.min(toInt(limitArg == null ? 100 : limitArg, 100), 500));

        Map<String, String> names = config.peerNames();
        List<Map<String, Object>> rows = new ArrayList<>();
        for (Map<String, Object> row : store.listOutbox(status, limit)) {
            Map<String, Object> item = rowToDict(row);
            String targetPeer = DbValues.text(item.get("target_peer"));
            item.put("target_peer_name", names.getOrDefault(targetPeer, targetPeer));
            rows.add(item);
        }

        return Api.body("code", 200, "message", "ok", "data", Map.of("items", rows));
    }

    @PostMapping("/api/admin/sync/outbox/retry")
    public Map<String, Object> outboxRetry(HttpServletRequest request,
                                           @RequestBody(required = false) Map<String, Object> body) {
        authGuard.require(request, 3, "无管理员权限");

        Object rawId = body == null ? null : body.get("id");
        long outboxId;
        try {
            outboxId = Long.parseLong(String.valueOf(rawId).trim());
        } catch (Exception e) {
            throw new ApiException(400, "缺少有效的队列ID");
        }

        int affected = store.retryOutbox(outboxId);
        if (affected == 0) {
            throw new ApiException(404, "队列记录不存在");
        }

        worker.triggerSync();

        return Api.body("code", 200, "message", "已重新入队", "data", Map.of("id", outboxId));
    }

    @GetMapping("/api/admin/sync/conflicts")
    public Map<String, Object> conflicts(
            HttpServletRequest request,
            @RequestParam(value = "state", required = false) String stateArg,
            @RequestParam(value = "keyword", required = false) String keyword,
            @RequestParam(value = "limit", required = false) String limitArg) {

        authGuard.require(request, 3, "无管理员权限");

        int state = toInt(stateArg == null ? String.valueOf(SyncStore.CONFLICT_PENDING) : stateArg,
                SyncStore.CONFLICT_PENDING);
        int limit = Math.max(1, Math.min(toInt(limitArg == null ? 200 : limitArg, 200), 500));
        Integer stateFilter = state >= 0 ? state : null;

        List<Map<String, Object>> rows = new ArrayList<>();

        for (Map<String, Object> row : store.listConflicts(stateFilter, limit, keyword)) {
            Map<String, Object> item = rowToDict(row);

            Object loser = item.get("loser_json");
            if (loser instanceof String text) {
                try {
                    item.put("loser_json", mapper.readValue(text, Map.class));
                } catch (Exception e) {
                    item.put("loser_json", null);
                }
            }

            item.put("winner_site_name", config.siteNameOf(DbValues.text(item.get("winner_site"))));

            if (item.get("loser_json") instanceof Map<?, ?> loserMap) {
                @SuppressWarnings("unchecked")
                Map<String, Object> detail = (Map<String, Object>) loserMap;

                Object entries = detail.get("losers");
                if (entries instanceof List<?> list) {
                    for (Object entry : list) {
                        if (entry instanceof Map<?, ?> map) {
                            @SuppressWarnings("unchecked")
                            Map<String, Object> entryMap = (Map<String, Object>) map;
                            entryMap.put("site_name", config.siteNameOf(DbValues.text(entryMap.get("site"))));
                            entryMap.put("status_text",
                                    SyncContract.STATUS_TEXT.get(DbValues.nullableInt(entryMap.get("attendance_status"))));
                        }
                    }
                }

                Object winner = detail.get("winner");
                if (winner instanceof Map<?, ?> map) {
                    @SuppressWarnings("unchecked")
                    Map<String, Object> winnerMap = (Map<String, Object>) map;
                    winnerMap.put("site_name", config.siteNameOf(DbValues.text(winnerMap.get("site"))));
                }
            }

            rows.add(item);
        }

        Map<String, Object> data = new LinkedHashMap<>();
        data.put("items", rows);
        data.put("total", store.countConflicts(stateFilter, keyword));
        data.put("pending", store.countPendingConflicts());

        return Api.body("code", 200, "message", "ok", "data", data);
    }

    @PostMapping("/api/admin/sync/conflicts/handle")
    public Map<String, Object> conflictHandle(HttpServletRequest request,
                                              @RequestBody(required = false) Map<String, Object> body) {
        AuthGuard.User user = authGuard.require(request, 3, "无管理员权限");

        String conflictId = SyncContract.normalizeText(body == null ? null : body.get("id"));
        String action = SyncContract.normalizeText(body == null ? null : body.get("action"));

        if (conflictId.isEmpty() || !("resolve".equals(action) || "ignore".equals(action))) {
            throw new ApiException(400, "参数不合法");
        }

        int affected = store.handleConflict(conflictId, action, user.userId());
        if (affected == 0) {
            throw new ApiException(404, "冲突记录不存在或已处理");
        }

        Map<String, Object> data = new LinkedHashMap<>();
        data.put("id", conflictId);
        data.put("action", action);

        return Api.body("code", 200, "message", "已处理", "data", data);
    }

    @PostMapping("/api/admin/sync/conflicts/batch")
    public Map<String, Object> conflictBatch(HttpServletRequest request,
                                             @RequestBody(required = false) Map<String, Object> body) {
        AuthGuard.User user = authGuard.require(request, 3, "无管理员权限");

        String action = SyncContract.normalizeText(body == null ? null : body.get("action"));
        Object idsRaw = body == null ? null : body.get("ids");

        if (!("resolve".equals(action) || "ignore".equals(action))) {
            throw new ApiException(400, "参数不合法");
        }

        List<String> ids = new ArrayList<>();
        if (idsRaw == null || "".equals(idsRaw)) {
            // 空数组表示处理全部「待处理」的行
        } else if (idsRaw instanceof List<?> list) {
            for (Object id : list) {
                ids.add(String.valueOf(id));
            }
        } else {
            throw new ApiException(400, "ids 必须是数组");
        }

        int affected = store.handleConflicts(action, user.userId(), ids);

        Map<String, Object> data = new LinkedHashMap<>();
        data.put("affected", affected);
        data.put("action", action);

        return Api.body("code", 200, "message", "已处理 " + affected + " 条", "data", data);
    }

    @PostMapping("/api/admin/sync/trigger")
    public Map<String, Object> trigger(HttpServletRequest request,
                                       @RequestBody(required = false) Map<String, Object> body) {
        authGuard.require(request, 3, "无管理员权限");

        String action = SyncContract.normalizeText(body == null ? null : body.get("action"));
        if (action.isEmpty()) {
            action = "sync";
        }

        if ("reconcile".equals(action)) {
            Map<String, Object> stats;
            try {
                stats = store.reconcile();
            } catch (Exception e) {
                throw new ApiException(500, "对账失败", String.valueOf(e.getMessage()));
            }
            return Api.body("code", 200, "message", "对账完成", "data", stats);
        }

        worker.triggerSync();

        return Api.body("code", 200, "message", "已触发同步，稍后刷新查看结果", "data", Map.of());
    }
}
