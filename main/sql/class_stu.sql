-- ============================================================
-- 学生签到系统 · 公共模板库（仅表结构 + 示例数据）
-- 适用环境：MySQL 8.0+，字符集 utf8mb4
-- ------------------------------------------------------------
-- 内容说明：
--   1. 共 13 张表：8 张业务主表 + 4 张跨站同步表 + 1 张更新日志表；
--   2. 仅保留示例基础数据：1 个管理员、1 个教师、1 个学生、1 个班级、2 门课程；
--   3. 考勤任务、签到记录、设备登录、跨站同步、更新日志默认均为空，
--      由使用者自行创建或由系统运行产生；
--   4. 示例账号：admin / tea / 253201304，初始密码均为 123456；
--   5. 示例课程日期使用 CURDATE() 与次日，导入当天即可看到「今日课程」。
-- ------------------------------------------------------------
-- 使用方法：
--   mysql -u root -p < class_stu.sql
--   或在任意 MySQL 客户端中直接执行本文件。
--   如需更换数据库名，请同时修改本文件中的 CREATE DATABASE / USE 与后端配置。
-- ------------------------------------------------------------
-- 安全提醒：
--   1. 本脚本含有 DROP TABLE IF EXISTS，会先删除同名表，请在空库或测试库执行；
--   2. 导入后请立即修改示例账号密码、数据库账号密码与后端 JWT 密钥；
--   3. 本文件仅用于初始化与演示，请勿直接用于生产环境。
-- ============================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

CREATE DATABASE IF NOT EXISTS `student_signin`
  DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `student_signin`;

DROP TABLE IF EXISTS `attendance_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `attendance_record` (
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '签到记录UUID',
  `task_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '签到任务ID',
  `student_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '学生ID',
  `status` tinyint NOT NULL DEFAULT '1' COMMENT '签到状态 1正常 2迟到 3旷课 4早退 5病假 6事假',
  `sign_time` datetime NOT NULL COMMENT '签到时间',
  `ip` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '签到IP',
  `device_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '签到设备ID',
  `location` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '签到位置',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `is_script` tinyint NOT NULL DEFAULT '0' COMMENT '是否脚本签到 0否 1是（如 selenium/puppeteer 自动签到）',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_attendance_record_task_id` (`task_id`) USING BTREE,
  KEY `idx_attendance_record_student_id` (`student_id`) USING BTREE,
  KEY `idx_attendance_record_device_id` (`device_id`) USING BTREE,
  KEY `idx_attendance_record_sign_time` (`sign_time`) USING BTREE,
  KEY `idx_attendance_record_task_student` (`task_id`,`student_id`) USING BTREE,
  KEY `idx_attendance_record_task_device` (`task_id`,`device_id`) USING BTREE,
  CONSTRAINT `fk_attendance_record_student` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_attendance_record_task` FOREIGN KEY (`task_id`) REFERENCES `attendance_task` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='学生签到记录表';
/*!40101 SET character_set_client = @saved_cs_client */;

--

/*!40000 ALTER TABLE `attendance_record` DISABLE KEYS */;
/*!40000 ALTER TABLE `attendance_record` ENABLE KEYS */;

--
-- Table structure for table `attendance_task`
--

DROP TABLE IF EXISTS `attendance_task`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `attendance_task` (
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '签到任务UUID',
  `course_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '课程ID',
  `start_time` datetime NOT NULL COMMENT '签到开始时间',
  `end_time` datetime NOT NULL COMMENT '签到结束时间',
  `status` tinyint NOT NULL DEFAULT '1' COMMENT '签到任务状态 1进行中 0已结束',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_attendance_task_course_id` (`course_id`) USING BTREE,
  KEY `idx_attendance_task_status` (`status`) USING BTREE,
  KEY `idx_attendance_task_time` (`start_time`,`end_time`) USING BTREE,
  CONSTRAINT `fk_attendance_task_course` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='签到任务表';
/*!40101 SET character_set_client = @saved_cs_client */;

--

/*!40000 ALTER TABLE `attendance_task` DISABLE KEYS */;
/*!40000 ALTER TABLE `attendance_task` ENABLE KEYS */;

--
-- Table structure for table `classes`
--

DROP TABLE IF EXISTS `classes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `classes` (
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '班级UUID',
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '班级名称',
  `grade` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '年级',
  `teacher_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '班主任ID',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_classes_name` (`name`) USING BTREE,
  KEY `idx_classes_teacher_id` (`teacher_id`) USING BTREE,
  CONSTRAINT `fk_class_teacher` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='班级表';
/*!40101 SET character_set_client = @saved_cs_client */;

--

/*!40000 ALTER TABLE `classes` DISABLE KEYS */;
/*!40000 ALTER TABLE `classes` ENABLE KEYS */;

--
-- Table structure for table `courses`
--

DROP TABLE IF EXISTS `courses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `courses` (
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '课程UUID',
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '课程名称',
  `teacher_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '授课教师ID',
  `class_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '班级ID',
  `course_date` date DEFAULT NULL COMMENT '上课日期，例如 2026-09-14',
  `time` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '上课时间段，例如 08:00-09:40',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_courses_teacher_id` (`teacher_id`) USING BTREE,
  KEY `idx_courses_class_id` (`class_id`) USING BTREE,
  KEY `idx_courses_course_date` (`course_date`) USING BTREE,
  KEY `idx_courses_class_date` (`class_id`,`course_date`) USING BTREE,
  CONSTRAINT `fk_course_class` FOREIGN KEY (`class_id`) REFERENCES `classes` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_course_teacher` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='课程表';
/*!40101 SET character_set_client = @saved_cs_client */;

--

/*!40000 ALTER TABLE `courses` DISABLE KEYS */;
/*!40000 ALTER TABLE `courses` ENABLE KEYS */;

--
-- Table structure for table `cross_site_conflict`
--

DROP TABLE IF EXISTS `cross_site_conflict`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cross_site_conflict` (
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '冲突ID',
  `align_key` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '归一化对齐键',
  `winner_record_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '胜出记录ID',
  `winner_site` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '胜出记录来源站点',
  `loser_json` json DEFAULT NULL COMMENT '落败记录（本站记录不会被改动，只在此登记）',
  `state` tinyint NOT NULL DEFAULT '0' COMMENT '0待处理 1已裁决 2忽略',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `handled_by` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '处理人用户ID',
  `handled_at` datetime DEFAULT NULL COMMENT '处理时间',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_conflict_align` (`align_key`) USING BTREE,
  KEY `idx_conflict_state` (`state`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='跨站签到冲突登记表';
/*!40101 SET character_set_client = @saved_cs_client */;

--

/*!40000 ALTER TABLE `cross_site_conflict` DISABLE KEYS */;
/*!40000 ALTER TABLE `cross_site_conflict` ENABLE KEYS */;

--
-- Table structure for table `cross_site_record`
--

DROP TABLE IF EXISTS `cross_site_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cross_site_record` (
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '本站记录ID',
  `origin_site` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '来源站点标识',
  `origin_record_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '来源站点的签到记录ID',
  `origin_task_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '来源站点的签到任务ID',
  `student_no` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '学号',
  `student_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '学生姓名',
  `class_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '班级名',
  `course_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '课程名',
  `course_date` date DEFAULT NULL COMMENT '课程日期',
  `period` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '时段档 morning/afternoon（对齐键组成部分）',
  `time_slot` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '时间段',
  `align_key` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '归一化对齐键',
  `attendance_status` tinyint DEFAULT NULL COMMENT '签到状态 1正常 2迟到 3旷课 4早退 5病假 6事假',
  `sign_time` datetime DEFAULT NULL COMMENT '异地签到时间',
  `device_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '签到设备ID',
  `ip` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '签到IP',
  `location` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '签到位置',
  `is_script` tinyint NOT NULL DEFAULT '0' COMMENT '是否脚本签到',
  `task_start_time` datetime DEFAULT NULL COMMENT '来源站点任务开始时间',
  `task_end_time` datetime DEFAULT NULL COMMENT '来源站点任务结束时间',
  `raw_json` json DEFAULT NULL COMMENT '原始事件留档',
  `resolve_state` tinyint NOT NULL DEFAULT '1' COMMENT '0待裁决 1有效 2作废',
  `is_duplicate` tinyint NOT NULL DEFAULT '0' COMMENT '是否被判为重复',
  `duplicate_of` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '重复指向的有效记录ID',
  `ingest_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '入库时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uk_cross_origin` (`origin_site`,`origin_record_id`) USING BTREE,
  KEY `idx_cross_align` (`student_no`,`class_name`,`course_name`,`course_date`,`time_slot`) USING BTREE,
  KEY `idx_cross_sign_time` (`sign_time`) USING BTREE,
  KEY `idx_cross_state` (`resolve_state`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='跨站签到同步表';
/*!40101 SET character_set_client = @saved_cs_client */;

--

/*!40000 ALTER TABLE `cross_site_record` DISABLE KEYS */;
/*!40000 ALTER TABLE `cross_site_record` ENABLE KEYS */;

--
-- Table structure for table `device_login_record`
--

DROP TABLE IF EXISTS `device_login_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `device_login_record` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '记录ID',
  `device_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '设备唯一标识',
  `user_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '当天登录的用户ID',
  `login_date` date NOT NULL COMMENT '登录日期',
  `login_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '首次登录时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uk_device_login_date` (`device_id`,`login_date`) USING BTREE,
  KEY `idx_device_login_user_id` (`user_id`) USING BTREE,
  KEY `idx_device_login_date` (`login_date`) USING BTREE,
  CONSTRAINT `fk_device_login_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='每日设备登录记录表';
/*!40101 SET character_set_client = @saved_cs_client */;

--

/*!40000 ALTER TABLE `device_login_record` DISABLE KEYS */;
/*!40000 ALTER TABLE `device_login_record` ENABLE KEYS */;

--
-- Table structure for table `students`
--

DROP TABLE IF EXISTS `students`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `students` (
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '学生UUID',
  `user_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '关联用户ID',
  `student_no` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '学生学号',
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '学生姓名',
  `class_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '班级ID',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uk_students_user_id` (`user_id`) USING BTREE,
  UNIQUE KEY `uk_students_student_no` (`student_no`) USING BTREE,
  KEY `idx_students_class_id` (`class_id`) USING BTREE,
  KEY `idx_students_name` (`name`) USING BTREE,
  CONSTRAINT `fk_student_class` FOREIGN KEY (`class_id`) REFERENCES `classes` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_student_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='学生表';
/*!40101 SET character_set_client = @saved_cs_client */;

--

/*!40000 ALTER TABLE `students` DISABLE KEYS */;
/*!40000 ALTER TABLE `students` ENABLE KEYS */;

--
-- Table structure for table `sync_cursor`
--

DROP TABLE IF EXISTS `sync_cursor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sync_cursor` (
  `peer_code` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '对端站点标识',
  `last_seq` bigint NOT NULL DEFAULT '0' COMMENT '已拉取到的对端 outbox 序号',
  `last_pull_at` datetime DEFAULT NULL COMMENT '最近一次拉取时间',
  `last_success_at` datetime DEFAULT NULL COMMENT '最近一次拉取成功时间',
  `fail_count` int NOT NULL DEFAULT '0' COMMENT '连续失败次数',
  `last_error` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '最近一次错误',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`peer_code`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='跨站同步游标表';
/*!40101 SET character_set_client = @saved_cs_client */;

--

/*!40000 ALTER TABLE `sync_cursor` DISABLE KEYS */;
/*!40000 ALTER TABLE `sync_cursor` ENABLE KEYS */;

--
-- Table structure for table `sync_outbox`
--

DROP TABLE IF EXISTS `sync_outbox`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sync_outbox` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '队列序号（同时作为 pull 游标）',
  `target_peer` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '目标站点标识',
  `event_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '事件ID',
  `event_type` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '事件类型',
  `payload` json NOT NULL COMMENT '完整事件信封',
  `status` tinyint NOT NULL DEFAULT '0' COMMENT '0待发 1已发 2失败',
  `retry_count` int NOT NULL DEFAULT '0' COMMENT '已重试次数',
  `next_retry_at` datetime DEFAULT NULL COMMENT '下次重试时间',
  `last_error` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '最近一次错误',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '入队时间',
  `sent_at` datetime DEFAULT NULL COMMENT '发送成功时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uk_outbox_event` (`target_peer`,`event_id`) USING BTREE,
  KEY `idx_outbox_pending` (`status`,`next_retry_at`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='跨站同步发送队列表';
/*!40101 SET character_set_client = @saved_cs_client */;

--

/*!40000 ALTER TABLE `sync_outbox` DISABLE KEYS */;
/*!40000 ALTER TABLE `sync_outbox` ENABLE KEYS */;

--
-- Table structure for table `teachers`
--

DROP TABLE IF EXISTS `teachers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `teachers` (
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '教师UUID',
  `user_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '关联用户ID',
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '教师姓名',
  `department` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '所属院系',
  `class_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '所属班级ID',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uk_teachers_user_id` (`user_id`) USING BTREE,
  KEY `idx_teachers_name` (`name`) USING BTREE,
  KEY `idx_teachers_class_id` (`class_id`) USING BTREE,
  CONSTRAINT `fk_teacher_class` FOREIGN KEY (`class_id`) REFERENCES `classes` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_teacher_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='教师表';
/*!40101 SET character_set_client = @saved_cs_client */;

--

/*!40000 ALTER TABLE `teachers` DISABLE KEYS */;
/*!40000 ALTER TABLE `teachers` ENABLE KEYS */;

--
-- Table structure for table `update_log`
--

DROP TABLE IF EXISTS `update_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `update_log` (
  `update_id` bigint NOT NULL AUTO_INCREMENT COMMENT '更新记录ID',
  `tag` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '类型：新增/优化/修复',
  `content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '更新内容',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`update_id`) USING BTREE,
  KEY `idx_update_created` (`created_at`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='系统更新日志表';
/*!40101 SET character_set_client = @saved_cs_client */;

--

/*!40000 ALTER TABLE `update_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `update_log` ENABLE KEYS */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户UUID',
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户名',
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Werkzeug密码哈希',
  `role` tinyint NOT NULL COMMENT '角色 1学生 2教师 3管理员',
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '手机号',
  `status` tinyint NOT NULL DEFAULT '1' COMMENT '账号状态 1正常 0禁用',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uk_users_username` (`username`) USING BTREE,
  KEY `idx_users_role` (`role`) USING BTREE,
  KEY `idx_users_status` (`status`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC COMMENT='用户表';
/*!40101 SET character_set_client = @saved_cs_client */;

--

/*!40000 ALTER TABLE `users` DISABLE KEYS */;
/*!40000 ALTER TABLE `users` ENABLE KEYS */;

--

--



-- ---------------------------- 示例数据 ----------------------------
INSERT INTO `users` (`id`,`username`,`password`,`role`,`phone`,`status`,`create_time`) VALUES
('0b9c3572-a450-45c8-b858-df9c9b67d299','tea','scrypt:32768:8:1$kWevw35UmNhYsCQF$dc129dedc0465b7dd53d311bc7ee0f1d0aa9b8f05e99047fd67abff6c0d77413a475cbc2e6b20b3afd761f439d6cd92188474770bcce9268a4ad0455d90ae868',2,NULL,1,'2026-09-15 00:55:46'),
('10000000-0000-0000-0000-000000000001','admin','scrypt:32768:8:1$kWevw35UmNhYsCQF$dc129dedc0465b7dd53d311bc7ee0f1d0aa9b8f05e99047fd67abff6c0d77413a475cbc2e6b20b3afd761f439d6cd92188474770bcce9268a4ad0455d90ae868',3,'13800000001',1,'2026-09-15 00:37:02'),
('1082a22c-0041-42ad-865f-013a37e0e32c','253201304','scrypt:32768:8:1$kWevw35UmNhYsCQF$dc129dedc0465b7dd53d311bc7ee0f1d0aa9b8f05e99047fd67abff6c0d77413a475cbc2e6b20b3afd761f439d6cd92188474770bcce9268a4ad0455d90ae868',1,NULL,1,'2026-09-15 00:50:49');

INSERT INTO `classes` (`id`,`name`,`grade`,`teacher_id`) VALUES
('abfb5cae-84d4-4aff-b893-40cd42666d18','大数据2532013','2025级',NULL);

INSERT INTO `teachers` (`id`,`user_id`,`name`,`department`,`class_id`) VALUES
('f9cc3f0b-4dee-4ba3-81da-982c8dd41642','0b9c3572-a450-45c8-b858-df9c9b67d299','刘老师','人工智能学院','abfb5cae-84d4-4aff-b893-40cd42666d18');

INSERT INTO `students` (`id`,`user_id`,`student_no`,`name`,`class_id`) VALUES
('1aedebb6-c172-4e7c-ac46-7c3d4ddb956b','1082a22c-0041-42ad-865f-013a37e0e32c','253201304','冯载轩','abfb5cae-84d4-4aff-b893-40cd42666d18');

INSERT INTO `courses` (`id`,`name`,`teacher_id`,`class_id`,`course_date`,`time`) VALUES
('1cd70b04-4e9d-4bba-8fc5-3c101d8d4a77','生产性实训','f9cc3f0b-4dee-4ba3-81da-982c8dd41642','abfb5cae-84d4-4aff-b893-40cd42666d18',CURDATE(),'13:30-17:00'),
('22647393-b33a-4992-8645-fbb205c4fe9b','生产性实训','f9cc3f0b-4dee-4ba3-81da-982c8dd41642','abfb5cae-84d4-4aff-b893-40cd42666d18',DATE_ADD(CURDATE(), INTERVAL 1 DAY),'13:30-17:00');


SET FOREIGN_KEY_CHECKS = 1;

-- 模板库导入完成：可启动后端与前端，使用示例账号登录。
