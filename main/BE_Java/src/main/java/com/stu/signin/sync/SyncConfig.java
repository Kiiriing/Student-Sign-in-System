package com.stu.signin.sync;

import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * 跨站同步站点配置，对应 Python sync/config.py。
 *
 * 站点标识、对端地址与令牌都优先读环境变量，默认值与 Python 版一致，
 * 保证同一份部署说明在两种后端下通用。
 */
@Component
public class SyncConfig {

    public static final String PROTOCOL_CONTRACT = "contract";
    public static final String PROTOCOL_SNAPSHOT = "snapshot";

    public static final int PUSH_TIMEOUT = 3;
    public static final int PULL_TIMEOUT = 3;
    public static final double CHECK_TIMEOUT = 1.2;
    public static final double CHECK_TOTAL_TIMEOUT = 2.0;

    public static final int PULL_LIMIT = 200;
    public static final int PUSH_BATCH_SIZE = 50;
    public static final int MAX_RETRY = 12;
    public static final int CACHE_TTL = 8;
    public static final int RECONCILE_DAYS = 30;

    public static final int SNAPSHOT_TIMEOUT = 30;
    public static final int SNAPSHOT_MIN_INTERVAL = 30;
    public static final String SNAPSHOT_DEFAULT_ORIGIN = "site_a";
    public static final boolean SNAPSHOT_OPEN = true;

    public record SyncPeer(String code, String name, String protocol, String baseUrl, String token) {
    }

    private final String siteCode;
    private final String siteName;
    private final List<SyncPeer> peers;

    public SyncConfig() {
        this.siteCode = env("SYNC_SITE_CODE", "site_local");
        this.siteName = env("SYNC_SITE_NAME", "本站签到");

        List<SyncPeer> list = new ArrayList<>();
        list.add(new SyncPeer(
                "site_a",
                "A 站",
                PROTOCOL_SNAPSHOT,
                env("SYNC_BASE_URL_SITE_A", "http://10.32.54.172:8000"),
                env("SYNC_TOKEN_SITE_A", "change-me-site-a")));
        list.add(new SyncPeer(
                "site_b",
                "B 站",
                PROTOCOL_CONTRACT,
                env("SYNC_BASE_URL_SITE_B", "http://10.32.54.194:8080"),
                env("SYNC_TOKEN_SITE_B", "change-me-site-b")));
        this.peers = List.copyOf(list);
    }

    private static String env(String key, String fallback) {
        String value = System.getenv(key);
        return value == null || value.isEmpty() ? fallback : value;
    }

    public String siteCode() {
        return siteCode;
    }

    public String siteName() {
        return siteName;
    }

    public List<SyncPeer> peers() {
        return peers;
    }

    public SyncPeer getPeer(String code) {
        for (SyncPeer peer : peers) {
            if (peer.code().equals(code)) {
                return peer;
            }
        }
        return null;
    }

    public String peerProtocol(SyncPeer peer) {
        if (peer == null || peer.protocol() == null || peer.protocol().isBlank()) {
            return PROTOCOL_CONTRACT;
        }
        return peer.protocol();
    }

    public List<SyncPeer> contractPeers() {
        return peers.stream().filter(peer -> PROTOCOL_CONTRACT.equals(peerProtocol(peer))).toList();
    }

    public List<SyncPeer> snapshotPeers() {
        return peers.stream().filter(peer -> PROTOCOL_SNAPSHOT.equals(peerProtocol(peer))).toList();
    }

    public SyncPeer getPeerByToken(String token) {
        if (token == null || token.isEmpty()) {
            return null;
        }
        for (SyncPeer peer : peers) {
            if (peer.token() != null && peer.token().equals(token)) {
                return peer;
            }
        }
        return null;
    }

    public Map<String, String> peerNames() {
        Map<String, String> names = new LinkedHashMap<>();
        for (SyncPeer peer : peers) {
            names.put(peer.code(), peer.name());
        }
        return names;
    }

    public String siteNameOf(String code) {
        if (code == null) {
            return code;
        }
        if (code.equals(siteCode)) {
            return siteName;
        }
        SyncPeer peer = getPeer(code);
        return peer == null ? code : peer.name();
    }
}
