-- =========================================
-- 学生签到系统数据库
-- =========================================

-- -----------------------------------------
-- 升级提示（重要）
-- -----------------------------------------
-- 如果你已部署过本系统且 attendance_record 表有数据不想丢失，
-- 请勿直接运行下面的 DROP DATABASE，改为手动执行如下升级语句：
--
--   USE student_signin;
--   ALTER TABLE attendance_record
--       ADD COLUMN is_script TINYINT NOT NULL DEFAULT 0
--       COMMENT '是否脚本签到 0否 1是（如 selenium/puppeteer 自动签到）';
--
-- 若 MySQL 版本 >= 8.0.13 / MariaDB 10.5+ 支持 ADD COLUMN IF NOT EXISTS，
-- 可加上 IF NOT EXISTS 关键字以便重复执行不报错；低版本请直接去掉。
-- 新增的 attendance_record.is_script 列默认值为 0，历史记录视为非脚本签到。

DROP DATABASE IF EXISTS student_signin;

CREATE DATABASE IF NOT EXISTS student_signin
DEFAULT CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE student_signin;


-- =========================================
-- 关闭外键检查
-- =========================================

SET FOREIGN_KEY_CHECKS = 0;


-- =========================================
-- 用户表
-- =========================================

CREATE TABLE users
(
    id CHAR(36) NOT NULL COMMENT '用户UUID',

    username VARCHAR(50) NOT NULL COMMENT '用户名',

    password VARCHAR(255) NOT NULL
        COMMENT 'Werkzeug密码哈希',

    role TINYINT NOT NULL
        COMMENT '角色 1学生 2教师 3管理员',

    phone VARCHAR(20) DEFAULT NULL
        COMMENT '手机号',

    status TINYINT NOT NULL DEFAULT 1
        COMMENT '账号状态 1正常 0禁用',

    create_time TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP
        COMMENT '创建时间',

    PRIMARY KEY (id),

    UNIQUE KEY uk_users_username (username),

    KEY idx_users_role (role),
    KEY idx_users_status (status)
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci
COMMENT='用户表';


-- =========================================
-- 教师表
-- =========================================

CREATE TABLE teachers
(
    id CHAR(36) NOT NULL COMMENT '教师UUID',

    user_id CHAR(36) NOT NULL
        COMMENT '关联用户ID',

    name VARCHAR(50) NOT NULL
        COMMENT '教师姓名',

    department VARCHAR(50) DEFAULT NULL
        COMMENT '所属院系',

    PRIMARY KEY (id),

    UNIQUE KEY uk_teachers_user_id (user_id),

    KEY idx_teachers_name (name),

    CONSTRAINT fk_teacher_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci
COMMENT='教师表';


-- =========================================
-- 班级表
-- =========================================

CREATE TABLE classes
(
    id CHAR(36) NOT NULL COMMENT '班级UUID',

    name VARCHAR(50) NOT NULL
        COMMENT '班级名称',

    grade VARCHAR(50) DEFAULT NULL
        COMMENT '年级',

    teacher_id CHAR(36) DEFAULT NULL
        COMMENT '班主任ID',

    PRIMARY KEY (id),

    KEY idx_classes_name (name),
    KEY idx_classes_teacher_id (teacher_id),

    CONSTRAINT fk_class_teacher
        FOREIGN KEY (teacher_id)
        REFERENCES teachers(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci
COMMENT='班级表';


-- =========================================
-- 学生表
-- =========================================

CREATE TABLE students
(
    id CHAR(36) NOT NULL COMMENT '学生UUID',

    user_id CHAR(36) NOT NULL
        COMMENT '关联用户ID',

    student_no VARCHAR(32) NOT NULL
        COMMENT '学生学号',

    name VARCHAR(50) NOT NULL
        COMMENT '学生姓名',

    class_id CHAR(36) DEFAULT NULL
        COMMENT '班级ID',

    PRIMARY KEY (id),

    UNIQUE KEY uk_students_user_id (user_id),

    UNIQUE KEY uk_students_student_no (student_no),

    KEY idx_students_class_id (class_id),
    KEY idx_students_name (name),

    CONSTRAINT fk_student_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_student_class
        FOREIGN KEY (class_id)
        REFERENCES classes(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci
COMMENT='学生表';


-- =========================================
-- 课程表
-- =========================================

CREATE TABLE courses
(
    id CHAR(36) NOT NULL COMMENT '课程UUID',

    name VARCHAR(100) NOT NULL
        COMMENT '课程名称',

    teacher_id CHAR(36) NOT NULL
        COMMENT '授课教师ID',

    class_id CHAR(36) NOT NULL
        COMMENT '班级ID',

    course_date DATE DEFAULT NULL
        COMMENT '上课日期，例如 2026-09-14',

    time VARCHAR(50) DEFAULT NULL
        COMMENT '上课时间段，例如 08:00-09:40',

    PRIMARY KEY (id),

    KEY idx_courses_teacher_id (teacher_id),
    KEY idx_courses_class_id (class_id),
    KEY idx_courses_course_date (course_date),

    CONSTRAINT fk_course_teacher
        FOREIGN KEY (teacher_id)
        REFERENCES teachers(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_course_class
        FOREIGN KEY (class_id)
        REFERENCES classes(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci
COMMENT='课程表';


-- =========================================
-- 签到任务表
-- =========================================

CREATE TABLE attendance_task
(
    id CHAR(36) NOT NULL COMMENT '签到任务UUID',

    course_id CHAR(36) NOT NULL
        COMMENT '课程ID',

    start_time DATETIME NOT NULL
        COMMENT '签到开始时间',

    end_time DATETIME NOT NULL
        COMMENT '签到结束时间',

    status TINYINT NOT NULL DEFAULT 1
        COMMENT '签到任务状态 1进行中 0已结束',

    create_time TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP
        COMMENT '创建时间',

    PRIMARY KEY (id),

    KEY idx_attendance_task_course_id (course_id),

    KEY idx_attendance_task_status (status),

    KEY idx_attendance_task_time (start_time, end_time),

    CONSTRAINT fk_attendance_task_course
        FOREIGN KEY (course_id)
        REFERENCES courses(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci
COMMENT='签到任务表';


-- =========================================
-- 签到记录表
-- =========================================

CREATE TABLE attendance_record
(
    id CHAR(36) NOT NULL COMMENT '签到记录UUID',

    task_id CHAR(36) NOT NULL
        COMMENT '签到任务ID',

    student_id CHAR(36) NOT NULL
        COMMENT '学生ID',

    status TINYINT NOT NULL DEFAULT 1
        COMMENT '签到状态 1正常 2迟到 3旷课 4早退 5病假 6事假',

    sign_time DATETIME NOT NULL
        COMMENT '签到时间',

    ip VARCHAR(45) DEFAULT NULL
        COMMENT '签到IP',

    device_id VARCHAR(255) DEFAULT NULL
        COMMENT '签到设备ID',

    location VARCHAR(255) DEFAULT NULL
        COMMENT '签到位置',

    is_script TINYINT NOT NULL DEFAULT 0
        COMMENT '是否脚本签到 0否 1是（如 selenium/puppeteer 自动签到）',

    create_time TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP
        COMMENT '创建时间',

    PRIMARY KEY (id),

    KEY idx_attendance_record_task_id (task_id),

    KEY idx_attendance_record_student_id (student_id),

    KEY idx_attendance_record_device_id (device_id),

    KEY idx_attendance_record_sign_time (sign_time),

    CONSTRAINT fk_attendance_record_task
        FOREIGN KEY (task_id)
        REFERENCES attendance_task(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_attendance_record_student
        FOREIGN KEY (student_id)
        REFERENCES students(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci
COMMENT='学生签到记录表';


-- =========================================
-- 每日设备登录记录表
-- =========================================
--
-- 功能：
-- 同一台设备一天只能登录一个账号。
--
-- 例如：
--
-- 2026-09-11
-- 设备 A -> 张三    ✅
-- 设备 A -> 张三    ✅
-- 设备 A -> 李四    ❌
--
-- 2026-09-12
-- 设备 A -> 李四    ✅
--
-- 第二天因为 login_date 不同，
-- 所以设备限制自动重新开始。
--
-- 注意：
-- 这个限制只用于登录接口。
-- 不代表账号永久绑定设备。
--
-- =========================================

CREATE TABLE device_login_record
(
    id BIGINT NOT NULL AUTO_INCREMENT
        COMMENT '记录ID',

    device_id VARCHAR(255) NOT NULL
        COMMENT '设备唯一标识',

    user_id CHAR(36) NOT NULL
        COMMENT '当天登录的用户ID',

    login_date DATE NOT NULL
        COMMENT '登录日期',

    login_time DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP
        COMMENT '首次登录时间',

    PRIMARY KEY (id),

    -- 同一设备同一天只能存在一条登录记录
    UNIQUE KEY uk_device_login_date
        (device_id, login_date),

    -- 根据用户查询当天设备登录记录
    KEY idx_device_login_user_id
        (user_id),

    -- 根据日期查询设备登录记录
    KEY idx_device_login_date
        (login_date),

    CONSTRAINT fk_device_login_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci
COMMENT='每日设备登录记录表';


-- =========================================
-- 恢复外键检查
-- =========================================

SET FOREIGN_KEY_CHECKS = 1;


-- =========================================================
-- 初始化测试账号
-- =========================================================

USE student_signin;

SET FOREIGN_KEY_CHECKS = 0;

-- =========================================
-- 清空旧测试数据
-- =========================================

TRUNCATE TABLE attendance_record;
TRUNCATE TABLE attendance_task;
TRUNCATE TABLE courses;
TRUNCATE TABLE students;
TRUNCATE TABLE classes;
TRUNCATE TABLE teachers;
TRUNCATE TABLE users;

SET FOREIGN_KEY_CHECKS = 1;


-- =========================================
-- 1. 用户表
-- 密码均为 Werkzeug 密码哈希
-- =========================================

INSERT INTO users
(
    id,
    username,
    password,
    role,
    phone,
    status
)
VALUES

-- 管理员
(
    '10000000-0000-0000-0000-000000000001',
    'admin',
    'scrypt:32768:8:1$testadmin$6d7b8e3b3a2a0e4a0c7e2e8d3f1a9b8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1',
    3,
    '13800000001',
    1
),

-- 教师
(
    '10000000-0000-0000-0000-000000000002',
    'teacher01',
    'scrypt:32768:8:1$testteacher1$6d7b8e3b3a2a0e4a0c7e2e8d3f1a9b8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1',
    2,
    '13800000002',
    1
),

(
    '10000000-0000-0000-0000-000000000003',
    'teacher02',
    'scrypt:32768:8:1$testteacher2$6d7b8e3b3a2a0e4a0c7e2e8d3f1a9b8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1',
    2,
    '13800000003',
    1
),

-- 学生
(
    '10000000-0000-0000-0000-000000000011',
    'student01',
    'scrypt:32768:8:1$teststudent2$1a5a4dcdfc6714a3171c31ce0da6198866e493ff75791b9c95776dbda46b20598f198958b5787f916dbad5c252b4febeaad667ca80bc81a3c9a250a0df6a986c',
    1,
    '13900000001',
    1
),

(
    '10000000-0000-0000-0000-000000000012',
    'student02',
    'scrypt:32768:8:1$teststudent2$6d7b8e3b3a2a0e4a0c7e2e8d3f1a9b8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1',
    1,
    '13900000002',
    1
),

(
    '10000000-0000-0000-0000-000000000013',
    'student03',
    'scrypt:32768:8:1$teststudent3$6d7b8e3b3a2a0e4a0c7e2e8d3f1a9b8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1',
    1,
    '13900000003',
    1
),

(
    '10000000-0000-0000-0000-000000000014',
    'student04',
    'scrypt:32768:8:1$teststudent4$6d7b8e3b3a2a0e4a0c7e2e8d3f1a9b8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1',
    1,
    '13900000004',
    1
),

(
    '10000000-0000-0000-0000-000000000015',
    'student05',
    'scrypt:32768:8:1$teststudent5$6d7b8e3b3a2a0e4a0c7e2e8d3f1a9b8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1',
    1,
    '13900000005',
    1
),

(
    '10000000-0000-0000-0000-000000000016',
    'student06',
    'scrypt:32768:8:1$teststudent6$6d7b8e3b3a2a0e4a0c7e2e8d3f1a9b8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1',
    1,
    '13900000006',
    1
);


-- =========================================
-- 2. 教师
-- =========================================

INSERT INTO teachers
(
    id,
    user_id,
    name,
    department
)
VALUES
(
    '20000000-0000-0000-0000-000000000001',
    '10000000-0000-0000-0000-000000000002',
    '王老师',
    '计算机学院'
),
(
    '20000000-0000-0000-0000-000000000002',
    '10000000-0000-0000-0000-000000000003',
    '李老师',
    '软件工程学院'
);


-- =========================================
-- 3. 班级
-- =========================================

INSERT INTO classes
(
    id,
    name,
    grade,
    teacher_id
)
VALUES
(
    '30000000-0000-0000-0000-000000000001',
    '软件2401班',
    '2024级',
    '20000000-0000-0000-0000-000000000001'
),
(
    '30000000-0000-0000-0000-000000000002',
    '软件2402班',
    '2024级',
    '20000000-0000-0000-0000-000000000001'
),
(
    '30000000-0000-0000-0000-000000000003',
    '计算机2401班',
    '2024级',
    '20000000-0000-0000-0000-000000000002'
);


-- =========================================
-- 4. 学生
-- =========================================

INSERT INTO students
(
    id,
    user_id,
    student_no,
    name,
    class_id
)
VALUES
(
    '40000000-0000-0000-0000-000000000001',
    '10000000-0000-0000-0000-000000000011',
    '20240001',
    '张三',
    '30000000-0000-0000-0000-000000000001'
),
(
    '40000000-0000-0000-0000-000000000002',
    '10000000-0000-0000-0000-000000000012',
    '20240002',
    '李四',
    '30000000-0000-0000-0000-000000000001'
),
(
    '40000000-0000-0000-0000-000000000003',
    '10000000-0000-0000-0000-000000000013',
    '20240003',
    '王五',
    '30000000-0000-0000-0000-000000000001'
),
(
    '40000000-0000-0000-0000-000000000004',
    '10000000-0000-0000-0000-000000000014',
    '20240004',
    '赵六',
    '30000000-0000-0000-0000-000000000002'
),
(
    '40000000-0000-0000-0000-000000000005',
    '10000000-0000-0000-0000-000000000015',
    '20240005',
    '孙七',
    '30000000-0000-0000-0000-000000000002'
),
(
    '40000000-0000-0000-0000-000000000006',
    '10000000-0000-0000-0000-000000000016',
    '20240006',
    '周八',
    '30000000-0000-0000-0000-000000000003'
);


-- =========================================
-- 5. 课程
--
-- 说明：
--   course_date 存储具体上课日期，用于按天过滤
--   time        存储当天的时间段，不再包含星期
--
-- 软件2401班（张三/李四/王五）：
--   今天 2 门课：Web前端开发、Python程序设计
--   昨天 1 门课：Java程序设计（跨班复用class_id=2给示例，实际2401班按需求设置）
--   明天 1 门课：数据库原理（软件2402班，演示date过滤不同）
-- 计算机2401班（周八）：
--   今天 1 门课：计算机网络
--   后天 1 门课：软件工程
-- =========================================

INSERT INTO courses
(
    id,
    name,
    teacher_id,
    class_id,
    course_date,
    time
)
VALUES

-- ---- 软件2401班：今天 08:00 ----
(
    '50000000-0000-0000-0000-000000000001',
    'Web前端开发',
    '20000000-0000-0000-0000-000000000001',
    '30000000-0000-0000-0000-000000000001',
    CURDATE(),
    '08:00-09:40'
),

-- ---- 软件2401班：今天 10:00 ----
(
    '50000000-0000-0000-0000-000000000002',
    'Python程序设计',
    '20000000-0000-0000-0000-000000000001',
    '30000000-0000-0000-0000-000000000001',
    CURDATE(),
    '10:00-11:40'
),

-- ---- 软件2402班：明天 ----
(
    '50000000-0000-0000-0000-000000000003',
    '数据库原理',
    '20000000-0000-0000-0000-000000000001',
    '30000000-0000-0000-0000-000000000002',
    DATE_ADD(CURDATE(), INTERVAL 1 DAY),
    '08:00-09:40'
),

-- ---- 软件2402班：昨天 ----
(
    '50000000-0000-0000-0000-000000000004',
    'Java程序设计',
    '20000000-0000-0000-0000-000000000002',
    '30000000-0000-0000-0000-000000000002',
    DATE_SUB(CURDATE(), INTERVAL 1 DAY),
    '14:00-15:40'
),

-- ---- 计算机2401班：今天 ----
(
    '50000000-0000-0000-0000-000000000005',
    '计算机网络',
    '20000000-0000-0000-0000-000000000002',
    '30000000-0000-0000-0000-000000000003',
    CURDATE(),
    '08:00-09:40'
),

-- ---- 计算机2401班：后天 ----
(
    '50000000-0000-0000-0000-000000000006',
    '软件工程',
    '20000000-0000-0000-0000-000000000002',
    '30000000-0000-0000-0000-000000000003',
    DATE_ADD(CURDATE(), INTERVAL 2 DAY),
    '14:00-15:40'
);


-- =========================================
-- 6. 签到任务
-- =========================================

-- 当前进行中的签到任务
INSERT INTO attendance_task
(
    id,
    course_id,
    start_time,
    end_time,
    status
)
VALUES
(
    '60000000-0000-0000-0000-000000000001',
    '50000000-0000-0000-0000-000000000001',
    DATE_SUB(NOW(), INTERVAL 5 MINUTE),
    DATE_ADD(NOW(), INTERVAL 25 MINUTE),
    1
);

-- 另一个当前进行中的签到任务
INSERT INTO attendance_task
(
    id,
    course_id,
    start_time,
    end_time,
    status
)
VALUES
(
    '60000000-0000-0000-0000-000000000002',
    '50000000-0000-0000-0000-000000000003',
    DATE_SUB(NOW(), INTERVAL 15 MINUTE),
    DATE_ADD(NOW(), INTERVAL 15 MINUTE),
    1
);

-- 已结束签到任务
INSERT INTO attendance_task
(
    id,
    course_id,
    start_time,
    end_time,
    status
)
VALUES
(
    '60000000-0000-0000-0000-000000000003',
    '50000000-0000-0000-0000-000000000002',
    DATE_SUB(NOW(), INTERVAL 2 DAY),
    DATE_SUB(NOW(), INTERVAL 2 DAY) + INTERVAL 30 MINUTE,
    0
);

-- 更早的一次签到任务
INSERT INTO attendance_task
(
    id,
    course_id,
    start_time,
    end_time,
    status
)
VALUES
(
    '60000000-0000-0000-0000-000000000004',
    '50000000-0000-0000-0000-000000000005',
    DATE_SUB(NOW(), INTERVAL 5 DAY),
    DATE_SUB(NOW(), INTERVAL 5 DAY) + INTERVAL 30 MINUTE,
    0
);


-- =========================================
-- 7. 签到记录
-- =========================================

-- -----------------------------------------
-- 当前任务：Web前端开发
-- -----------------------------------------

-- 张三：正常签到
INSERT INTO attendance_record
(
    id,
    task_id,
    student_id,
    status,
    sign_time,
    ip,
    device_id,
    location
)
VALUES
(
    '70000000-0000-0000-0000-000000000001',
    '60000000-0000-0000-0000-000000000001',
    '40000000-0000-0000-0000-000000000001',
    1,
    DATE_SUB(NOW(), INTERVAL 3 MINUTE),
    '192.168.1.101',
    'DEVICE-STUDENT-001',
    '教学楼A栋 301'
);

-- 李四：正常签到
INSERT INTO attendance_record
(
    id,
    task_id,
    student_id,
    status,
    sign_time,
    ip,
    device_id,
    location
)
VALUES
(
    '70000000-0000-0000-0000-000000000002',
    '60000000-0000-0000-0000-000000000001',
    '40000000-0000-0000-0000-000000000002',
    1,
    DATE_SUB(NOW(), INTERVAL 2 MINUTE),
    '192.168.1.102',
    'DEVICE-STUDENT-002',
    '教学楼A栋 301'
);

-- 王五：迟到签到
INSERT INTO attendance_record
(
    id,
    task_id,
    student_id,
    status,
    sign_time,
    ip,
    device_id,
    location
)
VALUES
(
    '70000000-0000-0000-0000-000000000003',
    '60000000-0000-0000-0000-000000000001',
    '40000000-0000-0000-0000-000000000003',
    2,
    NOW(),
    '192.168.1.103',
    'DEVICE-STUDENT-003',
    '教学楼A栋 301'
);


-- -----------------------------------------
-- 当前任务：数据库原理
-- -----------------------------------------

-- 赵六：正常签到
INSERT INTO attendance_record
(
    id,
    task_id,
    student_id,
    status,
    sign_time,
    ip,
    device_id,
    location
)
VALUES
(
    '70000000-0000-0000-0000-000000000004',
    '60000000-0000-0000-0000-000000000002',
    '40000000-0000-0000-0000-000000000004',
    1,
    DATE_SUB(NOW(), INTERVAL 5 MINUTE),
    '192.168.1.104',
    'DEVICE-STUDENT-004',
    '教学楼B栋 205'
);


-- -----------------------------------------
-- 历史任务：Python程序设计
-- -----------------------------------------

-- 张三：正常
INSERT INTO attendance_record
(
    id,
    task_id,
    student_id,
    status,
    sign_time,
    ip,
    device_id,
    location
)
VALUES
(
    '70000000-0000-0000-0000-000000000005',
    '60000000-0000-0000-0000-000000000003',
    '40000000-0000-0000-0000-000000000001',
    1,
    DATE_SUB(NOW(), INTERVAL 2 DAY) + INTERVAL 5 MINUTE,
    '192.168.1.101',
    'DEVICE-STUDENT-001',
    '教学楼A栋 302'
);

-- 李四：迟到
INSERT INTO attendance_record
(
    id,
    task_id,
    student_id,
    status,
    sign_time,
    ip,
    device_id,
    location
)
VALUES
(
    '70000000-0000-0000-0000-000000000006',
    '60000000-0000-0000-0000-000000000003',
    '40000000-0000-0000-0000-000000000002',
    2,
    DATE_SUB(NOW(), INTERVAL 2 DAY) + INTERVAL 20 MINUTE,
    '192.168.1.102',
    'DEVICE-STUDENT-002',
    '教学楼A栋 302'
);

-- 王五：正常
INSERT INTO attendance_record
(
    id,
    task_id,
    student_id,
    status,
    sign_time,
    ip,
    device_id,
    location
)
VALUES
(
    '70000000-0000-0000-0000-000000000007',
    '60000000-0000-0000-0000-000000000003',
    '40000000-0000-0000-0000-000000000003',
    1,
    DATE_SUB(NOW(), INTERVAL 2 DAY) + INTERVAL 8 MINUTE,
    '192.168.1.103',
    'DEVICE-STUDENT-003',
    '教学楼A栋 302'
);


-- -----------------------------------------
-- 历史任务：计算机网络
-- -----------------------------------------

INSERT INTO attendance_record
(
    id,
    task_id,
    student_id,
    status,
    sign_time,
    ip,
    device_id,
    location
)
VALUES
(
    '70000000-0000-0000-0000-000000000008',
    '60000000-0000-0000-0000-000000000004',
    '40000000-0000-0000-0000-000000000006',
    1,
    DATE_SUB(NOW(), INTERVAL 5 DAY) + INTERVAL 6 MINUTE,
    '192.168.1.106',
    'DEVICE-STUDENT-006',
    '教学楼C栋 102'
);

INSERT INTO attendance_record
(
    id,
    task_id,
    student_id,
    status,
    sign_time,
    ip,
    device_id,
    location
)
VALUES
(
    '70000000-0000-0000-0000-000000000009',
    '60000000-0000-0000-0000-000000000004',
    '40000000-0000-0000-0000-000000000005',
    1,
    DATE_SUB(NOW(), INTERVAL 5 DAY) + INTERVAL 7 MINUTE,
    '192.168.1.105',
    'DEVICE-STUDENT-005',
    '教学楼C栋 102'
);


-- =========================================
-- 完成
-- =========================================

SELECT '测试数据插入完成' AS message;

-- =========================================
-- 检查数据
-- =========================================

SELECT
    id,
    username,
    role,
    status
FROM users
ORDER BY role, username;

SELECT
    s.student_no,
    s.name,
    c.name AS class_name,
    u.username
FROM students s
JOIN users u ON s.user_id = u.id
LEFT JOIN classes c ON s.class_id = c.id
ORDER BY s.student_no;

SELECT
    co.name AS course_name,
    t.name AS teacher_name,
    c.name AS class_name,
    co.time
FROM courses co
JOIN teachers t ON co.teacher_id = t.id
JOIN classes c ON co.class_id = c.id;

SELECT
    co.name AS course_name,
    at.start_time,
    at.end_time,
    at.status
FROM attendance_task at
JOIN courses co ON at.course_id = co.id
ORDER BY at.start_time DESC;

SELECT
    s.student_no,
    s.name AS student_name,
    co.name AS course_name,
    ar.status,
    ar.sign_time,
    ar.device_id,
    ar.ip,
    ar.location
FROM attendance_record ar
JOIN students s ON ar.student_id = s.id
JOIN attendance_task at ON ar.task_id = at.id
JOIN courses co ON at.course_id = co.id
ORDER BY ar.sign_time DESC;

-- ============================================================
-- 学生签到系统 - 课程日期字段迁移脚本
--
-- 场景：数据库已经存在，courses 表只有 time 字段
--       现在需要新增 course_date 字段并拆分 time 数据
--
-- 使用方法：
--   Windows:
--     mysql -u root -p < d:\stu_v2\main\sql\migrate_add_course_date.sql
--   或在 Navicat / DBeaver 中打开本文件直接执行
--
-- 注意：
--   脚本幂等，重复执行不会报错。
-- ============================================================

USE student_signin;

SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================
-- 1. 新增 course_date 列（如果不存在）
-- ============================================================

SET @col_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'student_signin'
      AND TABLE_NAME = 'courses'
      AND COLUMN_NAME = 'course_date'
);

SET @sql = IF(
    @col_exists = 0,
    'ALTER TABLE courses ADD COLUMN course_date DATE DEFAULT NULL COMMENT ''上课日期，例如 2026-09-14'' AFTER class_id',
    'SELECT ''[跳过] course_date 列已存在'' AS message'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ============================================================
-- 2. 新增索引（如果不存在）
-- ============================================================

SET @idx_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.STATISTICS
    WHERE TABLE_SCHEMA = 'student_signin'
      AND TABLE_NAME = 'courses'
      AND INDEX_NAME = 'idx_courses_course_date'
);

SET @sql = IF(
    @idx_exists = 0,
    'ALTER TABLE courses ADD INDEX idx_courses_course_date (course_date)',
    'SELECT ''[跳过] idx_courses_course_date 索引已存在'' AS message'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ============================================================
-- 3. 拆分原 time 字段（格式如 "周一 08:00-09:40"）
--    - 如果 time 包含空格，取空格后面的部分作为新时间段
--    - 否则保留原样（已经是纯时间段）
-- ============================================================

UPDATE courses
SET time = SUBSTRING_INDEX(time, ' ', -1)
WHERE time LIKE '% %';

-- ============================================================
-- 4. 根据每条课程的 id，给示例数据填入今天/明天/昨天的日期
--    （和 class_stu.sql 完整导入时的分配保持一致）
-- ============================================================

-- 软件2401班：今天两门
UPDATE courses SET course_date = CURDATE()
WHERE id = '50000000-0000-0000-0000-000000000001'
   OR id = '50000000-0000-0000-0000-000000000002';

-- 软件2402班：明天一门 / 昨天一门
UPDATE courses SET course_date = DATE_ADD(CURDATE(), INTERVAL 1 DAY)
WHERE id = '50000000-0000-0000-0000-000000000003';

UPDATE courses SET course_date = DATE_SUB(CURDATE(), INTERVAL 1 DAY)
WHERE id = '50000000-0000-0000-0000-000000000004';

-- 计算机2401班：今天一门 / 后天一门
UPDATE courses SET course_date = CURDATE()
WHERE id = '50000000-0000-0000-0000-000000000005';

UPDATE courses SET course_date = DATE_ADD(CURDATE(), INTERVAL 2 DAY)
WHERE id = '50000000-0000-0000-0000-000000000006';

-- ============================================================
-- 5. 为没有设置日期的自定义课程兜底（未来新增数据）
--    如果是本地/测试环境：把剩余无日期课程统一设为今天
-- ============================================================

UPDATE courses SET course_date = CURDATE() WHERE course_date IS NULL;

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- 6. 验证结果
-- ============================================================

SELECT
    id,
    name,
    course_date,
    time,
    CASE
        WHEN course_date = CURDATE() THEN '今日课程'
        WHEN course_date < CURDATE() THEN CONCAT('已过 (', DATEDIFF(CURDATE(), course_date), ' 天前)')
        ELSE CONCAT('未到 (还有 ', DATEDIFF(course_date, CURDATE()), ' 天)')
    END AS date_status
FROM courses
ORDER BY course_date, time;

SELECT '迁移完成：已新增 course_date 字段并拆分 time 时间段' AS message;


-- ============================================================
-- 学生签到系统 - 教师绑定班级迁移脚本
--
-- 场景：
--   teachers 表原本没有 class_id，管理员无法将教师分配到班级。
--   本脚本为 teachers 表新增 class_id 列（可空，外键关联 classes.id）。
--
-- 使用方法：
--   mysql -u root -p < d:\stu_v2\main\sql\migrate_teacher_class_id.sql
--   或在 Navicat / DBeaver 中打开本文件直接执行
--
-- 注意：
--   脚本幂等，重复执行不会报错。
-- ============================================================

USE student_signin;

SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================
-- 1. 新增 teachers.class_id 列（如果不存在）
-- ============================================================

SET @col_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'student_signin'
      AND TABLE_NAME = 'teachers'
      AND COLUMN_NAME = 'class_id'
);

SET @sql = IF(
    @col_exists = 0,
    'ALTER TABLE teachers ADD COLUMN class_id CHAR(36) DEFAULT NULL COMMENT ''所属班级ID'' AFTER department',
    'SELECT ''[跳过] teachers.class_id 列已存在'' AS message'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ============================================================
-- 2. 新增索引（如果不存在）
-- ============================================================

SET @idx_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.STATISTICS
    WHERE TABLE_SCHEMA = 'student_signin'
      AND TABLE_NAME = 'teachers'
      AND INDEX_NAME = 'idx_teachers_class_id'
);

SET @sql = IF(
    @idx_exists = 0,
    'ALTER TABLE teachers ADD INDEX idx_teachers_class_id (class_id)',
    'SELECT ''[跳过] idx_teachers_class_id 索引已存在'' AS message'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ============================================================
-- 3. 新增外键（如果不存在）
--    班级被删除时，教师的 class_id 置空，不级联删除教师
-- ============================================================

SET @fk_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
    WHERE CONSTRAINT_SCHEMA = 'student_signin'
      AND TABLE_NAME = 'teachers'
      AND CONSTRAINT_NAME = 'fk_teacher_class'
);

SET @sql = IF(
    @fk_exists = 0,
    'ALTER TABLE teachers ADD CONSTRAINT fk_teacher_class FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE SET NULL ON UPDATE CASCADE',
    'SELECT ''[跳过] fk_teacher_class 外键已存在'' AS message'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- 4. 验证结果
-- ============================================================

SELECT
    t.id,
    t.name,
    t.department,
    t.class_id,
    c.name AS class_name
FROM teachers t
LEFT JOIN classes c ON c.id = t.class_id
ORDER BY t.name;

SELECT '迁移完成：teachers 表已新增 class_id 列' AS message;
