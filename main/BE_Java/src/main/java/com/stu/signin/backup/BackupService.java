package com.stu.signin.backup;

import com.stu.signin.config.AppProperties;
import com.stu.signin.persistence.DbWriteTracker;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.env.Environment;
import org.springframework.stereotype.Service;

import jakarta.annotation.PostConstruct;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Stream;

/**
 * 数据库空闲自动备份，对应 Python core/backup.py。
 *
 * 距最后一次数据改动满 app.backup.idle-seconds 后，用 mysqldump 导出整库
 * 到 app.backup.dir，文件名 student_signin{MMDD}_{HHMM}.sql，每天只留一份。
 */
@Service
public class BackupService {

    private static final Logger log = LoggerFactory.getLogger(BackupService.class);

    private static final DateTimeFormatter DAY = DateTimeFormatter.ofPattern("MMdd");
    private static final DateTimeFormatter CLOCK = DateTimeFormatter.ofPattern("HHmm");

    private static final String DUMP_PREFIX = "student_signin";
    private static final Pattern DUMP_NAME_PATTERN =
            Pattern.compile("^" + DUMP_PREFIX + "(\\d{4})_(\\d{4})\\.sql$");

    private static final String[] MYSQLDUMP_CANDIDATES = {
            "C:\\Program Files\\MySQL\\MySQL Server 8.0\\bin\\mysqldump.exe",
            "C:\\Program Files (x86)\\MySQL\\MySQL Server 8.0\\bin\\mysqldump.exe",
            "C:\\Program Files\\MySQL\\MySQL Workbench 8.0\\mysqldump.exe",
            "C:\\xampp\\mysql\\bin\\mysqldump.exe"
    };

    private static final String[] MYSQLDUMP_GLOB_DIRS = {
            "C:\\Program Files\\MySQL",
            "C:\\Program Files (x86)\\MySQL"
    };

    private final AppProperties properties;
    private final DbWriteTracker writeTracker;
    private final Environment environment;

    private final AtomicBoolean started = new AtomicBoolean(false);

    /** 上次导出对应的「改动时间」，用于判断这之后有没有新改动 */
    private volatile Long lastDumpWriteAt;

    public BackupService(AppProperties properties, DbWriteTracker writeTracker, Environment environment) {
        this.properties = properties;
        this.writeTracker = writeTracker;
        this.environment = environment;
    }

    @PostConstruct
    public void start() {
        if (!started.compareAndSet(false, true)) {
            return;
        }

        AppProperties.Backup config = properties.backup();
        long pollSeconds = config == null || config.pollSeconds() <= 0 ? 60 : config.pollSeconds();

        ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor(runnable -> {
            Thread thread = new Thread(runnable, "db-auto-backup");
            thread.setDaemon(true);
            return thread;
        });

        scheduler.scheduleWithFixedDelay(this::loopOnce, pollSeconds, pollSeconds, TimeUnit.SECONDS);

        log.info("空闲自动备份线程已启动（改动数据后空闲满 30 分钟导出一次）");
    }

    private void loopOnce() {
        try {
            maybeBackup();
        } catch (Exception e) {
            log("导出失败：" + e.getMessage());
        }
    }

    // ============================================================
    // 触发判断
    // ============================================================

    private void maybeBackup() throws Exception {
        AppProperties.Backup config = properties.backup();
        long idleSeconds = config == null || config.idleSeconds() <= 0 ? 1800 : config.idleSeconds();

        Long lastWrite = writeTracker.lastWriteAt();

        // 本进程启动后还没改动过数据 → 没有可备份的新变化
        if (lastWrite == null) {
            return;
        }

        if (System.currentTimeMillis() - lastWrite < idleSeconds * 1000L) {
            return;
        }

        // 上次导出已经把这次改动包含进去了 → 不重复导出
        Long dumped = lastDumpWriteAt;
        if (dumped != null && lastWrite <= dumped) {
            return;
        }

        backupNow();
    }

    // ============================================================
    // 导出
    // ============================================================

    private String backupNow() throws IOException, InterruptedException {
        AppProperties.Backup config = properties.backup();
        Path directory = Paths.get(config == null || config.dir() == null ? "../sql" : config.dir())
                .toAbsolutePath().normalize();
        Files.createDirectories(directory);

        LocalDateTime now = LocalDateTime.now();
        Path finalPath = directory.resolve(fileName(now));
        Path tempPath = directory.resolve(fileName(now) + "." + ProcessHandle.current().pid() + ".tmp");

        try {
            runMysqldump(tempPath);
            Files.move(tempPath, finalPath, StandardCopyOption.REPLACE_EXISTING,
                    StandardCopyOption.ATOMIC_MOVE);
        } catch (Exception e) {
            try {
                Files.deleteIfExists(tempPath);
            } catch (IOException ignored) {
                // 临时文件清理失败不影响主流程
            }
            throw e;
        }

        List<String> removed = cleanupSameDay(directory, finalPath, now);

        lastDumpWriteAt = writeTracker.lastWriteAt();

        long sizeKb = Files.size(finalPath) / 1024;
        String suffix = removed.isEmpty() ? "" : "，已清理旧文件 " + String.join("、", removed);

        log("已导出 " + finalPath.getFileName() + "（" + sizeKb + " KB）" + suffix);

        return finalPath.getFileName().toString();
    }

    private static String fileName(LocalDateTime now) {
        return DUMP_PREFIX + now.format(DAY) + "_" + now.format(CLOCK) + ".sql";
    }

    private void runMysqldump(Path target) throws IOException, InterruptedException {
        Path executable = findMysqldump();
        if (executable == null) {
            throw new IOException("找不到 mysqldump.exe，无法导出（请把它所在目录加入 PATH）");
        }

        String url = environment.getProperty("spring.datasource.url", "");
        String user = environment.getProperty("spring.datasource.username", "root");
        String password = environment.getProperty("spring.datasource.password", "");
        String database = databaseFromUrl(url);

        List<String> command = new ArrayList<>();
        command.add(executable.toString());
        command.add("-h");
        command.add(hostFromUrl(url));
        command.add("-P");
        command.add(portFromUrl(url));
        command.add("-u");
        command.add(user);
        command.add("--password=" + password);
        command.add("--single-transaction");
        command.add("--default-character-set=utf8mb4");
        command.add("--routines");
        command.add("--triggers");
        command.add("--events");
        command.add("--hex-blob");
        command.add("--databases");
        command.add(database);

        ProcessBuilder builder = new ProcessBuilder(command);
        builder.redirectOutput(target.toFile());
        Process process = builder.start();

        String stderr;
        try (InputStream stream = process.getErrorStream()) {
            stderr = new String(stream.readAllBytes(), StandardCharsets.UTF_8);
        }

        int exitCode = process.waitFor();

        if (exitCode != 0) {
            String detail = stderr.length() > 300 ? stderr.substring(stderr.length() - 300) : stderr;
            throw new IOException("mysqldump 退出码 " + exitCode + "：" + detail);
        }

        if (Files.size(target) == 0) {
            throw new IOException("mysqldump 输出为空文件");
        }
    }

    private List<String> cleanupSameDay(Path directory, Path keepPath, LocalDateTime now) {
        String day = now.format(DAY);
        List<String> removed = new ArrayList<>();

        try (Stream<Path> stream = Files.list(directory)) {
            for (Path path : stream.toList()) {
                String name = path.getFileName().toString();
                Matcher matcher = DUMP_NAME_PATTERN.matcher(name);
                if (!matcher.matches() || !matcher.group(1).equals(day)) {
                    continue;
                }
                if (path.toAbsolutePath().normalize().equals(keepPath.toAbsolutePath().normalize())) {
                    continue;
                }
                try {
                    Files.delete(path);
                    removed.add(name);
                } catch (IOException e) {
                    log("删除旧备份失败 " + name + "：" + e.getMessage());
                }
            }
        } catch (IOException e) {
            log("扫描备份目录失败：" + e.getMessage());
        }

        return removed;
    }

    // ============================================================
    // 工具
    // ============================================================

    private Path findMysqldump() {
        String path = System.getenv("PATH");
        if (path != null) {
            for (String entry : path.split(";")) {
                if (entry.isBlank()) {
                    continue;
                }
                Path candidate = Paths.get(entry.trim(), "mysqldump.exe");
                if (Files.isRegularFile(candidate)) {
                    return candidate;
                }
            }
        }

        for (String candidate : MYSQLDUMP_CANDIDATES) {
            Path file = Paths.get(candidate);
            if (Files.isRegularFile(file)) {
                return file;
            }
        }

        // C:\Program Files\MySQL\MySQL Server *\bin\mysqldump.exe（反向排序，8.0 优先于 5.7）
        for (String root : MYSQLDUMP_GLOB_DIRS) {
            Path rootPath = Paths.get(root);
            if (!Files.isDirectory(rootPath)) {
                continue;
            }
            List<Path> versions;
            try (Stream<Path> stream = Files.list(rootPath)) {
                versions = stream
                        .filter(Files::isDirectory)
                        .sorted(Comparator.comparing(Path::toString).reversed())
                        .toList();
            } catch (IOException e) {
                continue;
            }
            for (Path version : versions) {
                Path file = version.resolve("bin").resolve("mysqldump.exe");
                if (Files.isRegularFile(file)) {
                    return file;
                }
            }
        }

        return null;
    }

    private static String hostFromUrl(String url) {
        int start = url.indexOf("//");
        if (start < 0) {
            return "127.0.0.1";
        }
        String rest = url.substring(start + 2);
        int colon = rest.indexOf(':');
        int slash = rest.indexOf('/');
        int end = colon >= 0 && (slash < 0 || colon < slash) ? colon : slash;
        return end < 0 ? rest : rest.substring(0, end);
    }

    private static String portFromUrl(String url) {
        int start = url.indexOf("//");
        if (start < 0) {
            return "3306";
        }
        String rest = url.substring(start + 2);
        int colon = rest.indexOf(':');
        int slash = rest.indexOf('/');
        if (colon < 0 || (slash >= 0 && colon > slash)) {
            return "3306";
        }
        int end = rest.indexOf('/', colon);
        String port = end < 0 ? rest.substring(colon + 1) : rest.substring(colon + 1, end);
        int question = port.indexOf('?');
        return question < 0 ? port : port.substring(0, question);
    }

    private static String databaseFromUrl(String url) {
        int slash = url.indexOf('/', url.indexOf("//") + 2);
        if (slash < 0) {
            return "student_signin";
        }
        String rest = url.substring(slash + 1);
        int question = rest.indexOf('?');
        return question < 0 ? rest : rest.substring(0, question);
    }

    private static void log(String message) {
        log.info(message);
    }
}
