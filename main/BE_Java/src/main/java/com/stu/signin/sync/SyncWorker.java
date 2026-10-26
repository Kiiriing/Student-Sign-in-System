package com.stu.signin.sync;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.stu.signin.common.DbValues;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.Semaphore;
import java.util.concurrent.TimeUnit;

/**
 * 后台同步线程，对应 Python sync/worker.py。
 *
 * 一条守护线程承担四件事：快照推送、事件队列推送、增量拉取、对账。
 * 按需触发（本站签到 / 收到对端 push / 管理员手动触发），不做定时轮询。
 */
@Component
public class SyncWorker {

    private static final Logger log = LoggerFactory.getLogger(SyncWorker.class);

    private record OutboxItem(long id, Map<String, Object> event, int retryCount) {
    }

    private record CachedCheck(long time, DuplicateCheck check) {
    }

    public record DuplicateCheck(Map<String, Object> hit, List<String> warnings) {
    }

    private final SyncConfig config;
    private final SyncStore store;
    private final SnapshotService snapshotService;
    private final SyncClient client;
    private final ObjectMapper mapper;

    private final Semaphore wakeup = new Semaphore(0);
    private final Object startLock = new Object();
    private volatile boolean started = false;

    private final Object snapshotLock = new Object();
    private long lastSnapshotAt = 0L;

    private final Map<String, CachedCheck> checkCache = new HashMap<>();
    private final Object checkCacheLock = new Object();

    public SyncWorker(SyncConfig config, SyncStore store, SnapshotService snapshotService,
                      SyncClient client, ObjectMapper mapper) {
        this.config = config;
        this.store = store;
        this.snapshotService = snapshotService;
        this.client = client;
        this.mapper = mapper;
    }

    public void triggerSync() {
        wakeup.release();
    }

    private static void log(String message) {
        log.info(message);
    }

    // ============================================================
    // 出站：事件推送
    // ============================================================

    @SuppressWarnings("unchecked")
    private Map<String, Object> payloadOf(Map<String, Object> row) {
        Object payload = row.get("payload");
        if (payload instanceof Map<?, ?> map) {
            return (Map<String, Object>) map;
        }
        if (payload instanceof String text) {
            try {
                return mapper.readValue(text, Map.class);
            } catch (Exception e) {
                return null;
            }
        }
        return null;
    }

    public Map<String, Object> flushOutbox() {
        Map<String, Object> summary = new LinkedHashMap<>();
        int sent = 0;
        int failed = 0;

        int limit = SyncConfig.PUSH_BATCH_SIZE * Math.max(config.peers().size(), 1);
        List<Map<String, Object>> rows = store.pendingOutbox(limit);

        if (rows.isEmpty()) {
            summary.put("sent", 0);
            summary.put("failed", 0);
            return summary;
        }

        Map<String, List<OutboxItem>> byPeer = new LinkedHashMap<>();

        for (Map<String, Object> row : rows) {
            Map<String, Object> event = payloadOf(row);
            long id = DbValues.longValue(row.get("id"));
            if (event == null) {
                store.markOutboxRejected(id, "事件体无法解析");
                continue;
            }
            byPeer.computeIfAbsent(DbValues.text(row.get("target_peer")), key -> new ArrayList<>())
                    .add(new OutboxItem(id, event, DbValues.intValue(row.get("retry_count"))));
        }

        for (Map.Entry<String, List<OutboxItem>> entry : byPeer.entrySet()) {
            String peerCode = entry.getKey();
            List<OutboxItem> items = entry.getValue();
            SyncConfig.SyncPeer peer = config.getPeer(peerCode);

            if (peer == null) {
                for (OutboxItem item : items) {
                    store.markOutboxRejected(item.id(), "对端配置不存在：" + peerCode);
                }
                failed += items.size();
                continue;
            }

            if (!SyncConfig.PROTOCOL_CONTRACT.equals(config.peerProtocol(peer))) {
                for (OutboxItem item : items) {
                    store.markOutboxRejected(item.id(),
                            "目标站点已切换为快照式协议（" + SyncConfig.PROTOCOL_SNAPSHOT + "）");
                }
                failed += items.size();
                continue;
            }

            String url = SyncClient.joinUrl(peer.baseUrl(), "/api/sync/inbound/push");
            List<Map<String, Object>> events = new ArrayList<>();
            for (OutboxItem item : items) {
                events.add(item.event());
            }

            JsonNode response;
            try {
                response = client.postJson(url, Map.of("events", events), peer.token(), SyncConfig.PUSH_TIMEOUT);
            } catch (Exception e) {
                for (OutboxItem item : items) {
                    store.markOutboxFailed(item.id(), item.retryCount(), errorText(e));
                }
                failed += items.size();
                log("推送到 " + peerCode + " 失败：" + errorText(e));
                continue;
            }

            JsonNode data = response == null ? null : response.get("data");
            java.util.Set<String> accepted = new java.util.HashSet<>();
            java.util.Set<String> duplicated = new java.util.HashSet<>();
            Map<String, String> rejected = new HashMap<>();

            if (data != null && data.isObject()) {
                for (JsonNode item : arrayOf(data.get("accepted"))) {
                    accepted.add(item.path("event_id").asText(""));
                }
                for (JsonNode item : arrayOf(data.get("duplicated"))) {
                    duplicated.add(item.path("event_id").asText(""));
                }
                for (JsonNode item : arrayOf(data.get("rejected"))) {
                    rejected.put(item.path("event_id").asText(""), item.path("reason").asText(""));
                }
            }

            if (accepted.isEmpty() && duplicated.isEmpty() && rejected.isEmpty()) {
                for (OutboxItem item : items) {
                    store.markOutboxFailed(item.id(), item.retryCount(), "对端响应结构异常");
                }
                failed += items.size();
                log("推送到 " + peerCode + " 响应异常：" + response);
                continue;
            }

            for (OutboxItem item : items) {
                String eventId = String.valueOf(item.event().get("event_id"));
                if (accepted.contains(eventId) || duplicated.contains(eventId)) {
                    store.markOutboxSent(item.id());
                    sent++;
                } else if (rejected.containsKey(eventId)) {
                    String reason = rejected.get(eventId);
                    store.markOutboxRejected(item.id(),
                            reason == null || reason.isEmpty() ? "对端拒绝" : reason);
                    failed++;
                } else {
                    store.markOutboxFailed(item.id(), item.retryCount(), "对端未确认该事件");
                    failed++;
                }
            }
        }

        summary.put("sent", sent);
        summary.put("failed", failed);
        return summary;
    }

    private static List<JsonNode> arrayOf(JsonNode node) {
        List<JsonNode> items = new ArrayList<>();
        if (node != null && node.isArray()) {
            for (JsonNode item : node) {
                items.add(item);
            }
        }
        return items;
    }

    private static String errorText(Exception e) {
        String message = e.getMessage();
        return message == null || message.isEmpty() ? e.getClass().getSimpleName() : message;
    }

    // ============================================================
    // 出站：快照推送
    // ============================================================

    public Map<String, Object> pushSnapshotToPeers(boolean force) {
        Map<String, Object> result = new LinkedHashMap<>();
        List<SyncConfig.SyncPeer> peers = config.snapshotPeers();

        if (peers.isEmpty()) {
            return result;
        }

        synchronized (snapshotLock) {
            long now = System.currentTimeMillis();
            if (!force && now - lastSnapshotAt < SyncConfig.SNAPSHOT_MIN_INTERVAL * 1000L) {
                for (SyncConfig.SyncPeer peer : peers) {
                    result.put(peer.code(), Map.of(
                            "skipped", "距上次快照推送不足 " + SyncConfig.SNAPSHOT_MIN_INTERVAL + " 秒"));
                }
                return result;
            }
            lastSnapshotAt = now;
        }

        Map<String, Object> snapshot = snapshotService.buildSnapshot();

        for (SyncConfig.SyncPeer peer : peers) {
            String url = SyncClient.joinUrl(peer.baseUrl(), "/api/sync/import");
            JsonNode response;
            try {
                response = client.postJson(url, snapshot, null, SyncConfig.SNAPSHOT_TIMEOUT);
            } catch (Exception e) {
                result.put(peer.code(), Map.of("error", errorText(e)));
                store.saveCursor(peer.code(), 0, false, errorText(e));
                log("快照推送到 " + peer.code() + " 失败：" + errorText(e));
                continue;
            }

            store.saveCursor(peer.code(), 0, true, null);

            Map<String, Object> item = new LinkedHashMap<>();
            item.put("records", response == null ? 0 : response.path("created_records").asInt(0));
            item.put("skipped", response == null ? 0 : response.path("skipped_records").asInt(0));
            item.put("errors", arrayOf(response == null ? null : response.get("errors")).size());
            result.put(peer.code(), item);

            log("快照推送到 " + peer.code() + " 完成：新增 "
                    + item.get("records") + " 条 / 跳过 " + item.get("skipped") + " 条");
        }

        return result;
    }

    // ============================================================
    // 入站：拉取
    // ============================================================

    private Map<String, Object> pullSnapshot(SyncConfig.SyncPeer peer) {
        Map<String, Object> summary = new LinkedHashMap<>();
        long since = store.getCursor(peer.code());
        String url = SyncClient.joinUrl(peer.baseUrl(), "/api/sync/export");

        JsonNode snapshot;
        try {
            snapshot = client.getJson(url, null, SyncConfig.SNAPSHOT_TIMEOUT);
        } catch (Exception e) {
            store.saveCursor(peer.code(), since, false, errorText(e));
            log("从 " + peer.code() + " 拉取快照失败：" + errorText(e));
            summary.put("pulled", 0);
            summary.put("error", errorText(e));
            return summary;
        }

        if (snapshot == null || !snapshot.isObject()) {
            String error = "对端返回的不是快照 JSON 对象";
            store.saveCursor(peer.code(), since, false, error);
            log("从 " + peer.code() + " 拉取快照失败：" + error);
            summary.put("pulled", 0);
            summary.put("error", error);
            return summary;
        }

        Map<String, Object> snapshotMap = client.asMap(snapshot);
        Map<String, Object> ingest = snapshotService.importSnapshot(snapshotMap, peer.code());

        store.saveCursor(peer.code(), since, true, null);

        JsonNode records = snapshot.get("records");
        summary.put("pulled", records != null && records.isArray() ? records.size() : 0);
        summary.put("accepted", ingest.get("created_records"));
        summary.put("duplicated", ingest.get("skipped_records"));
        Object errors = ingest.get("errors");
        summary.put("rejected", errors instanceof List<?> list ? list.size() : 0);
        return summary;
    }

    public Map<String, Object> pullFromPeers() {
        Map<String, Object> result = new LinkedHashMap<>();

        for (SyncConfig.SyncPeer peer : config.peers()) {
            if (SyncConfig.PROTOCOL_SNAPSHOT.equals(config.peerProtocol(peer))) {
                result.put(peer.code(), pullSnapshot(peer));
                continue;
            }

            long since = store.getCursor(peer.code());
            String url = SyncClient.joinUrl(peer.baseUrl(), "/api/sync/inbound/pull")
                    + "?since=" + since + "&limit=" + SyncConfig.PULL_LIMIT;

            JsonNode response;
            try {
                response = client.getJson(url, peer.token(), SyncConfig.PULL_TIMEOUT);
            } catch (Exception e) {
                store.saveCursor(peer.code(), since, false, errorText(e));
                Map<String, Object> item = new LinkedHashMap<>();
                item.put("pulled", 0);
                item.put("error", errorText(e));
                result.put(peer.code(), item);
                log("从 " + peer.code() + " 拉取失败：" + errorText(e));
                continue;
            }

            JsonNode data = response == null ? null : response.get("data");
            List<JsonNode> eventNodes = arrayOf(data == null ? null : data.get("events"));
            long nextCursor = data != null && data.hasNonNull("next_cursor")
                    ? data.get("next_cursor").asLong() : since;

            Map<String, Object> summary = new LinkedHashMap<>();
            summary.put("pulled", 0);
            summary.put("accepted", 0);
            summary.put("duplicated", 0);
            summary.put("rejected", 0);

            if (!eventNodes.isEmpty()) {
                List<Map<String, Object>> events = new ArrayList<>();
                for (JsonNode node : eventNodes) {
                    Map<String, Object> event = client.asMap(node);
                    if (event != null) {
                        events.add(event);
                    }
                }
                SyncStore.IngestResult ingest = store.ingestEvents(events);
                summary.put("pulled", events.size());
                summary.put("accepted", ingest.accepted().size());
                summary.put("duplicated", ingest.duplicated().size());
                summary.put("rejected", ingest.rejected().size());
            }

            store.saveCursor(peer.code(), nextCursor, true, null);
            result.put(peer.code(), summary);
        }

        return result;
    }

    // ============================================================
    // 单轮执行 / 线程
    // ============================================================

    public Map<String, Object> runOnce(boolean withReconcile) {
        Map<String, Object> summary = new LinkedHashMap<>();

        try {
            summary.put("snapshot_push", pushSnapshotToPeers(false));
        } catch (Exception e) {
            summary.put("snapshot_push", Map.of("error", errorText(e)));
            log("快照推送异常：" + e);
        }

        try {
            summary.put("push", flushOutbox());
        } catch (Exception e) {
            summary.put("push", Map.of("error", errorText(e)));
            log("推送异常：" + e);
        }

        try {
            summary.put("pull", pullFromPeers());
        } catch (Exception e) {
            summary.put("pull", Map.of("error", errorText(e)));
            log("拉取异常：" + e);
        }

        if (withReconcile) {
            try {
                summary.put("reconcile", store.reconcile());
            } catch (Exception e) {
                summary.put("reconcile", Map.of("error", errorText(e)));
                log("对账异常：" + e);
            }
        }

        return summary;
    }

    public void start() {
        synchronized (startLock) {
            if (started) {
                return;
            }
            started = true;
        }

        Thread thread = new Thread(this::loop, "cross-site-sync");
        thread.setDaemon(true);
        thread.start();
    }

    private void loop() {
        log("同步线程已启动（按需触发，无定时轮询），站点标识=" + config.siteCode()
                + "，对端=" + config.peers().stream().map(SyncConfig.SyncPeer::code).toList());

        while (true) {
            try {
                wakeup.acquire();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return;
            }
            // 合并同一时间窗内的多次唤醒
            wakeup.drainPermits();

            try {
                runOnce(true);
            } catch (Exception e) {
                log("同步异常：" + e);
            }
        }
    }

    // ============================================================
    // 签到时的实时跨站查重
    // ============================================================

    public DuplicateCheck checkDuplicateOnPeers(String studentNo, String alignKey) {
        List<SyncConfig.SyncPeer> peers = config.contractPeers();

        if (peers.isEmpty() || studentNo == null || studentNo.isEmpty()
                || alignKey == null || alignKey.isEmpty()) {
            return new DuplicateCheck(null, List.of());
        }

        String cacheKey = studentNo + "|" + alignKey;
        long now = System.currentTimeMillis();

        synchronized (checkCacheLock) {
            CachedCheck cached = checkCache.get(cacheKey);
            if (cached != null && now - cached.time() < SyncConfig.CACHE_TTL * 1000L) {
                return cached.check();
            }
        }

        Map<String, Object> payload = Map.of("student_no", studentNo, "align_key", alignKey);
        Map<String, Object> hit = null;
        List<String> warnings = new ArrayList<>();

        ExecutorService pool = Executors.newFixedThreadPool(peers.size());
        try {
            Map<Future<JsonNode>, SyncConfig.SyncPeer> futures = new LinkedHashMap<>();
            for (SyncConfig.SyncPeer peer : peers) {
                String url = SyncClient.joinUrl(peer.baseUrl(), "/api/sync/check-dup");
                futures.put(pool.submit(() -> client.postJson(url, payload, peer.token(),
                        SyncConfig.CHECK_TIMEOUT)), peer);
            }

            long deadline = now + (long) (SyncConfig.CHECK_TOTAL_TIMEOUT * 1000);

            for (Map.Entry<Future<JsonNode>, SyncConfig.SyncPeer> entry : futures.entrySet()) {
                long remaining = Math.max(deadline - System.currentTimeMillis(), 0);
                SyncConfig.SyncPeer peer = entry.getValue();

                JsonNode response;
                try {
                    response = entry.getKey().get(remaining, TimeUnit.MILLISECONDS);
                } catch (Exception e) {
                    warnings.add(peer.name() + " " + shortError(e));
                    continue;
                }

                JsonNode data = response == null ? null : response.get("data");
                if (data != null && data.path("duplicated").asBoolean(false) && hit == null) {
                    hit = new LinkedHashMap<>();
                    hit.put("source_site", data.get("source_site") == null
                            || data.get("source_site").isNull() ? null : data.get("source_site").asText());
                    hit.put("sign_time", data.get("sign_time") == null
                            || data.get("sign_time").isNull() ? null : data.get("sign_time").asText());
                    hit.put("course_name", data.get("course_name") == null
                            || data.get("course_name").isNull() ? null : data.get("course_name").asText());
                }
            }
        } finally {
            // 不等待未完成的任务，避免拖住签到请求
            pool.shutdown();
        }

        DuplicateCheck result = new DuplicateCheck(hit, warnings);

        synchronized (checkCacheLock) {
            checkCache.put(cacheKey, new CachedCheck(System.currentTimeMillis(), result));

            if (checkCache.size() > 500) {
                long expireBefore = System.currentTimeMillis() - SyncConfig.CACHE_TTL * 1000L;
                checkCache.entrySet().removeIf(entry -> entry.getValue().time() < expireBefore);
            }
        }

        return result;
    }

    private static String shortError(Exception error) {
        String text = String.valueOf(error.getMessage() == null ? error : error.getMessage()).toLowerCase(Locale.ROOT);

        if (text.contains("超时") || text.contains("timed out") || text.contains("timeout")) {
            return "响应超时";
        }
        if (text.contains("不可达")) {
            return "不可达";
        }
        return "校验失败";
    }
}
