package com.stu.signin.logging;

import com.fasterxml.jackson.databind.JsonNode;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.stereotype.Component;

import java.util.ArrayDeque;
import java.util.Deque;
import java.util.Iterator;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * 爬虫检测，逻辑与 Python 版 main.py 的 detect_crawler 保持一致。
 *
 * 检测特征：
 *   1. User-Agent 命中爬虫库关键字
 *   2. User-Agent 为空或过短
 *   3. 前端浏览器指纹 client_fp 命中
 *   4. 请求体中出现爬虫关键字
 *   5. 缺少浏览器核心请求头
 *   6. 同一 IP + 路径短时高频
 *   7. 已标记的爬虫会话（同一 IP 后续请求）
 *
 * 检测结果只用于日志标注，不影响请求处理。
 */
@Component
public class CrawlerDetector {

    public static final String SYNC_API_PREFIX = "/api/sync/";

    private static final long BURST_WINDOW_MILLIS = 10_000L;
    private static final int BURST_THRESHOLD = 20;
    private static final long SESSION_TTL_MILLIS = 3_600_000L;

    private static final String[] BROWSER_CORE_HEADERS = {"Accept", "Accept-Language", "Accept-Encoding"};

    private static final Pattern CRAWLER_UA_REGEX = Pattern.compile(
            "python-requests|python-urllib|scrapy|curl|wget|postman|insomnia|httpclient|okhttp|java/|"
                    + "go-http-client|node-fetch|axios|bot|spider|crawler|scraper|headless|selenium|"
                    + "phantomjs|puppeteer|playwright|aiohttp|httpx|mechanize|googlehttpclient|webdriver",
            Pattern.CASE_INSENSITIVE);

    private static final Pattern BROWSER_UA_REGEX = Pattern.compile(
            "Mozilla|Chrome|Safari|Edge|Firefox|OPR|Opera|MSIE|Trident",
            Pattern.CASE_INSENSITIVE);

    private static final Pattern CRAWLER_BODY_REGEX = Pattern.compile(
            "scraper|spider|crawler|selenium|puppeteer|playwright|headless|phantomjs|mechanize|scrapy|aiohttp|httpx",
            Pattern.CASE_INSENSITIVE);

    private record Session(String flag, long time) {
    }

    private final Map<String, Deque<Long>> burstWindow = new ConcurrentHashMap<>();
    private final Map<String, Session> crawlerSessions = new ConcurrentHashMap<>();

    /**
     * @param parsedBody 已解析的请求体（可为 null，调用方复用解析结果）
     * @return 空串表示未检测到爬虫
     */
    public String detect(String ip, String path, String ua, String body,
                        JsonNode parsedBody, HttpServletRequest request) {

        if (path.startsWith(SYNC_API_PREFIX)) {
            return "";
        }

        gcSessions();

        long now = System.currentTimeMillis();
        boolean isLogin = "/api/auth/login".equals(path);

        // ---------- 1. 本次请求的实时特征 ----------
        String currentFlag = "";

        // 1.1 User-Agent 关键字
        if (ua != null && !ua.isEmpty()) {
            Matcher matcher = CRAWLER_UA_REGEX.matcher(ua);
            if (matcher.find()) {
                currentFlag = "UA:" + matcher.group().toLowerCase();
            }
        }

        // 1.2 User-Agent 为空或过短
        if (currentFlag.isEmpty() && (ua == null || ua.length() < 20)) {
            currentFlag = "EMPTY-UA";
        }

        // 1.3 前端浏览器指纹
        if (currentFlag.isEmpty() && parsedBody != null && parsedBody.isObject()) {
            JsonNode fp = parsedBody.get("client_fp");
            if (fp != null && !fp.isNull()) {
                String clientFp = fp.asText("").trim();
                if (!clientFp.isEmpty()) {
                    currentFlag = "FP:" + clientFp;
                }
            }
        }

        // 1.4 请求体爬虫关键字
        if (currentFlag.isEmpty() && body != null && !body.isEmpty() && !"-".equals(body)) {
            Matcher matcher = CRAWLER_BODY_REGEX.matcher(body);
            if (matcher.find()) {
                currentFlag = "BODY:" + matcher.group().toLowerCase();
            }
        }

        // 1.5 缺少浏览器核心头（仅当 UA 不像浏览器时）
        if (currentFlag.isEmpty() && (ua == null || !BROWSER_UA_REGEX.matcher(ua).find())) {
            StringBuilder missing = new StringBuilder();
            int missingCount = 0;
            for (String header : BROWSER_CORE_HEADERS) {
                if (request.getHeader(header) == null) {
                    if (missingCount > 0) {
                        missing.append(',');
                    }
                    missing.append(header);
                    missingCount++;
                }
            }
            if (missingCount >= 2) {
                currentFlag = "MISS-HEADERS(" + missing + ")";
            }
        }

        // 1.6 同一 IP + 路径短时高频
        if (currentFlag.isEmpty()) {
            String key = ip + "|" + path;
            Deque<Long> window = burstWindow.computeIfAbsent(key, k -> new ArrayDeque<>());
            synchronized (window) {
                window.addLast(now);
                while (!window.isEmpty() && window.peekFirst() < now - BURST_WINDOW_MILLIS) {
                    window.pollFirst();
                }
                if (window.size() >= BURST_THRESHOLD) {
                    currentFlag = "BURST(" + window.size() + "/" + (BURST_WINDOW_MILLIS / 1000) + "s)";
                }
            }
        }

        // ---------- 2. 会话追踪 ----------
        if (!currentFlag.isEmpty()) {
            crawlerSessions.put(ip, new Session(currentFlag, now));
            return currentFlag;
        }

        Session session = crawlerSessions.get(ip);
        if (session != null) {
            if (isLogin) {
                crawlerSessions.remove(ip);
                return "";
            }
            crawlerSessions.put(ip, new Session(session.flag(), now));
            return "SESSION:" + session.flag();
        }

        return "";
    }

    /** 该 IP 是否已被标记为爬虫会话（学生签到脚本检测使用，不改变会话状态） */
    public boolean isCrawlerSession(String ip) {
        if (ip == null) {
            return false;
        }
        return crawlerSessions.containsKey(ip);
    }

    private void gcSessions() {
        long now = System.currentTimeMillis();
        Iterator<Map.Entry<String, Session>> iterator = crawlerSessions.entrySet().iterator();
        while (iterator.hasNext()) {
            Map.Entry<String, Session> entry = iterator.next();
            if (now - entry.getValue().time() > SESSION_TTL_MILLIS) {
                iterator.remove();
            }
        }
    }
}
