package com.stu.signin.system;

import com.stu.signin.common.Api;
import com.stu.signin.common.ApiException;
import jakarta.annotation.PostConstruct;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * 系统更新日志，对应 Python 版 api/system.py。
 */
@Service
public class SystemService {

    private static final Logger log = LoggerFactory.getLogger(SystemService.class);

    /** 首次部署写入的初始更新日志 */
    private static final String[][] INITIAL_UPDATES = {
            {"新增", "创建课程支持「重复课程」：可在日期区间内，同教师 / 同班级 / 同时间段连续多天创建。"},
            {"新增", "账户管理 · 学生列表新增学号筛选，支持姓名 / 学号 / 用户名 / 班级 / 手机号 / 状态的模糊匹配。"},
            {"新增", "学生列表与已排课程列表加入前端分页（每页 20 条）与搜索，大数据量下更流畅。"},
            {"优化", "全部下拉菜单改为自绘组件：选项样式美化，展开 / 收起带过渡动画与箭头旋转。"},
            {"优化", "筛选栏的下拉框与日期框统一为定长宽度，排列更整齐。"},
            {"优化", "上课时间段改为自定义时 / 分选择，个位数字自动补 0。"},
            {"修复", "修复下拉框滚轮滚动时面板意外消失的问题。"},
            {"修复", "日期选择框支持点击整框弹出原生选择器。"},
            {"修复", "修复筛选后滚动条消失导致页面盒子被拉伸的抖动问题。"},
            {"修复", "修复课堂点名「音色」文字与下拉挤在同一列、学生姓名被迫换行的问题。"}
    };

    private final JdbcTemplate jdbcTemplate;

    public SystemService(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    /**
     * 创建更新日志表并在表为空时写入初始数据；数据库不可用时不影响服务启动。
     */
    @PostConstruct
    public void ensureUpdateTable() {
        try {
            jdbcTemplate.execute("""
                    CREATE TABLE IF NOT EXISTS `update_log` (
                      `update_id` bigint NOT NULL AUTO_INCREMENT COMMENT '更新记录ID',
                      `tag` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '类型：新增/优化/修复',
                      `content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '更新内容',
                      `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                      PRIMARY KEY (`update_id`),
                      INDEX `idx_update_created` (`created_at`)
                    ) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '系统更新日志表'
                    """);

            Long count = jdbcTemplate.queryForObject("SELECT COUNT(*) FROM `update_log`", Long.class);
            if (count == null || count == 0) {
                List<Object[]> batch = new ArrayList<>(INITIAL_UPDATES.length);
                for (String[] row : INITIAL_UPDATES) {
                    batch.add(new Object[]{row[0], row[1]});
                }
                jdbcTemplate.batchUpdate("INSERT INTO `update_log` (`tag`, `content`) VALUES (?, ?)", batch);
            }
        } catch (Exception e) {
            log.warn("更新日志初始化表失败：{}", e.getMessage());
        }
    }

    public Map<String, Object> listUpdates(String pageParam) {
        int page;
        try {
            page = Math.max(Integer.parseInt(pageParam == null ? "1" : pageParam), 1);
        } catch (NumberFormatException e) {
            page = 1;
        }

        Long total = jdbcTemplate.queryForObject("SELECT COUNT(*) FROM `update_log`", Long.class);

        List<String> dates = jdbcTemplate.queryForList("""
                SELECT DATE_FORMAT(`created_at`, '%Y-%m-%d') AS date
                FROM `update_log`
                GROUP BY date
                ORDER BY date DESC
                """, String.class);

        int totalPages = dates.isEmpty() ? 1 : dates.size();
        page = Math.min(page, totalPages);
        String pageDate = dates.isEmpty() ? null : dates.get(page - 1);

        List<Map<String, Object>> rows = new ArrayList<>();
        if (pageDate != null) {
            rows = jdbcTemplate.queryForList("""
                    SELECT `update_id`, `tag`, `content`,
                           DATE_FORMAT(`created_at`, '%Y-%m-%d') AS date,
                           DATE_FORMAT(`created_at`, '%Y-%m-%d %H:%i') AS created_at
                    FROM `update_log`
                    WHERE DATE_FORMAT(`created_at`, '%Y-%m-%d') = ?
                    ORDER BY FIELD(`tag`, '新增', '优化', '修复'),
                             `created_at` DESC, `update_id` DESC
                    """, pageDate);
        }

        Map<String, Object> data = new LinkedHashMap<>();
        data.put("list", rows);
        data.put("total", total == null ? 0 : total);
        data.put("page", page);
        data.put("total_pages", totalPages);

        return Api.body("code", 200, "message", "ok", "data", data);
    }
}
