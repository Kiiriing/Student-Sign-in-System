/*
 Navicat Premium Data Transfer

 Source Server         : localhost_3306
 Source Server Type    : MySQL
 Source Server Version : 80027
 Source Host           : localhost:3306
 Source Schema         : student_signin

 Target Server Type    : MySQL
 Target Server Version : 80027
 File Encoding         : 65001

 Date: 17/09/2026 15:07:43
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

CREATE DATABASE IF NOT EXISTS student_signin
DEFAULT CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE student_signin;

-- ----------------------------
-- Table structure for attendance_record
-- ----------------------------
DROP TABLE IF EXISTS `attendance_record`;
CREATE TABLE `attendance_record`  (
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '签到记录UUID',
  `task_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '签到任务ID',
  `student_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '学生ID',
  `status` tinyint(0) NOT NULL DEFAULT 1 COMMENT '签到状态 1正常 2迟到 3旷课 4早退 5病假 6事假',
  `sign_time` datetime(0) NOT NULL COMMENT '签到时间',
  `ip` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '签到IP',
  `device_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '签到设备ID',
  `location` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '签到位置',
  `create_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0) COMMENT '创建时间',
  `is_script` tinyint(0) NOT NULL DEFAULT 0 COMMENT '是否脚本签到 0否 1是（如 selenium/puppeteer 自动签到）',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_attendance_record_task_id`(`task_id`) USING BTREE,
  INDEX `idx_attendance_record_student_id`(`student_id`) USING BTREE,
  INDEX `idx_attendance_record_device_id`(`device_id`) USING BTREE,
  INDEX `idx_attendance_record_sign_time`(`sign_time`) USING BTREE,
  INDEX `idx_attendance_record_task_student`(`task_id`, `student_id`) USING BTREE,
  INDEX `idx_attendance_record_task_device`(`task_id`, `device_id`) USING BTREE,
  CONSTRAINT `fk_attendance_record_student` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_attendance_record_task` FOREIGN KEY (`task_id`) REFERENCES `attendance_task` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '学生签到记录表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of attendance_record
-- ----------------------------
INSERT INTO `attendance_record` VALUES ('0233633b-6de2-4d3e-b097-61ded565bdfb', '10a7481f-f632-401d-bfd3-582098c0ba2e', 'd4c430f1-f17e-4a9c-bb14-38b0dedc3620', 1, '2026-09-17 08:47:38', '10.32.54.189', '6c9b73f7-8cd2-4075-aa96-d68fb7535714', '', '2026-09-17 08:47:38', 1);
INSERT INTO `attendance_record` VALUES ('044e545a-22c4-40e2-acd2-94eb49282042', '3da50e8a-2624-4194-9158-2fd830ddc1e7', 'd53a5de6-fe03-4d94-9a03-bd0657d3d16c', 1, '2026-09-16 13:34:14', '10.32.54.182', '45baa313-f46f-42ef-9433-0930e19d7adf', '', '2026-09-16 13:34:14', 0);
INSERT INTO `attendance_record` VALUES ('08906b99-2e85-4f12-b57b-7890e1e43e0d', '3da50e8a-2624-4194-9158-2fd830ddc1e7', '43ab2c74-6013-437d-a4ea-18bd61e0555c', 1, '2026-09-16 13:40:06', '10.32.54.190', '7a389b25-99b4-4b26-bd29-64bd7298cd25', '', '2026-09-16 13:40:06', 1);
INSERT INTO `attendance_record` VALUES ('0a157cf0-4e98-4cd0-89d9-221bdf2b0376', '3da50e8a-2624-4194-9158-2fd830ddc1e7', '72f4bedc-e405-41ef-83e1-370fbf6ee8e4', 1, '2026-09-16 13:44:23', '10.32.54.178', 'd40f5142-5d8b-4091-aa61-8234846443b7', '', '2026-09-16 13:44:23', 1);
INSERT INTO `attendance_record` VALUES ('0a1b7642-e2d4-474b-a7ae-909ee410ef9c', '3da50e8a-2624-4194-9158-2fd830ddc1e7', 'ea8c876a-6da1-491c-9b0f-4e3fdbcaae85', 1, '2026-09-16 13:44:58', '10.32.54.178', '46e170a9-970a-482c-9b66-a219fafad6ad', '', '2026-09-16 13:44:58', 1);
INSERT INTO `attendance_record` VALUES ('0a6cf7a2-8864-46cf-ac92-95b272697aa8', 'bcef9cae-b9cb-407f-8eaa-2183af26b65b', 'd53a5de6-fe03-4d94-9a03-bd0657d3d16c', 1, '2026-09-17 13:36:09', '10.32.54.182', 'c2298e76-4efa-4485-a613-159cd65cb6b0', '', '2026-09-17 13:36:09', 0);
INSERT INTO `attendance_record` VALUES ('0ce1ae8c-e43c-4917-b425-ae71b83b4942', '10a7481f-f632-401d-bfd3-582098c0ba2e', '88f956e7-5584-4ab9-9400-f9c3f8630a1e', 1, '2026-09-17 10:34:42', '10.32.54.185', '97e1ce3e-c80b-4aef-bbe4-5c6fd5266bf6', '', '2026-09-17 10:34:42', 0);
INSERT INTO `attendance_record` VALUES ('0e56d310-19d2-461d-b3f0-47f442a60a33', '62b72c43-77de-4a08-a122-2de039afcda6', 'dc65aa73-09d5-44a6-8e6a-28a8c7ccf3cc', 1, '2026-09-16 09:09:25', '10.32.54.172', '38ddfe9f-bcf3-45dc-920f-a54e8f77c782', '', '2026-09-16 09:09:25', 0);
INSERT INTO `attendance_record` VALUES ('0f89382d-e060-407a-ac0e-69b6fd0ac03c', '62b72c43-77de-4a08-a122-2de039afcda6', '72f4bedc-e405-41ef-83e1-370fbf6ee8e4', 1, '2026-09-16 10:41:01', '10.32.54.178', 'e2ecaff0-3e26-4de5-9bef-8252ff6a7dd5', '', '2026-09-16 10:41:01', 1);
INSERT INTO `attendance_record` VALUES ('110d18fe-1430-4702-9f27-45830ce29ea6', '3da50e8a-2624-4194-9158-2fd830ddc1e7', '043ad3fe-7b96-4999-81d9-abb3bbee0b2d', 1, '2026-09-16 13:30:02', '10.32.54.186', '53642840-6c05-48b8-8996-947c955cd07c', '', '2026-09-16 13:30:02', 0);
INSERT INTO `attendance_record` VALUES ('115137ff-624e-420c-a929-13d9deb5ddcb', '10a7481f-f632-401d-bfd3-582098c0ba2e', 'f4200def-d5d1-4acf-96d3-13a9e2e8e1cf', 1, '2026-09-17 09:07:03', '10.32.54.174', '46f44e94-d787-416e-aeaf-f1def1e2d761', '', '2026-09-17 09:07:03', 1);
INSERT INTO `attendance_record` VALUES ('12d7bee2-df0e-4815-bfe5-5dcfbcea5f03', '7ab44183-c982-41db-bdec-6b7df542b544', '80465933-04d0-4aa2-b5cc-4b6bf73cff5a', 1, '2026-09-15 09:10:55', '10.32.54.153', '37e5ac5b-712b-43ca-9b53-b906bb31693c', '', '2026-09-15 09:10:55', 0);
INSERT INTO `attendance_record` VALUES ('155c47de-eac6-46f0-9f1e-7426165ba389', 'bcef9cae-b9cb-407f-8eaa-2183af26b65b', '7185bac0-000b-4aec-bde1-a60b751239e6', 1, '2026-09-17 13:38:04', NULL, NULL, NULL, '2026-09-17 13:38:04', 0);
INSERT INTO `attendance_record` VALUES ('17c6f6db-b460-4bdb-a07e-f611f64ee70b', 'bcef9cae-b9cb-407f-8eaa-2183af26b65b', 'ea5b11f1-54eb-43c5-bb2b-1522b11b39b7', 1, '2026-09-17 13:37:58', NULL, NULL, NULL, '2026-09-17 13:37:58', 0);
INSERT INTO `attendance_record` VALUES ('18d797b9-a9de-46b6-8764-4204a1bac2a2', '3da50e8a-2624-4194-9158-2fd830ddc1e7', 'fc9cf5b8-6c70-40ce-af3f-95dc5e747d77', 1, '2026-09-16 13:33:25', '10.32.54.184', 'cbcf2c59-8faf-4e70-9151-32a652e61167', '', '2026-09-16 13:33:25', 0);
INSERT INTO `attendance_record` VALUES ('1c77da0e-f86b-4a7b-9f4f-eb3be62263eb', '3da50e8a-2624-4194-9158-2fd830ddc1e7', '604bd35e-15ac-45a5-b074-e4c1ff3a640a', 1, '2026-09-16 13:32:40', '10.32.54.187', 'ef3afaea-cf3b-4ea6-88d2-7604dc078b48', '', '2026-09-16 13:32:40', 0);
INSERT INTO `attendance_record` VALUES ('1dd50296-073e-44ff-b45b-3ba354ab7eb2', '62b72c43-77de-4a08-a122-2de039afcda6', '604bd35e-15ac-45a5-b074-e4c1ff3a640a', 1, '2026-09-16 10:03:27', '10.32.54.187', '76fce6b3-ca1f-459a-b30e-77e049a5c1e7', '', '2026-09-16 10:03:27', 0);
INSERT INTO `attendance_record` VALUES ('1fcd2465-748f-4ca0-96b9-b3247d56b8e3', 'f63ed65e-9e31-486e-a894-44d851b7ff46', 'fc9cf5b8-6c70-40ce-af3f-95dc5e747d77', 1, '2026-09-15 13:30:41', '10.32.54.184', '6624f10b-090f-44dd-b748-5d9149c5f980', '', '2026-09-15 13:30:41', 0);
INSERT INTO `attendance_record` VALUES ('232ee332-8171-4a8e-ad23-ad5cbc92c086', '7ab44183-c982-41db-bdec-6b7df542b544', '880cbd99-d6a7-4f33-85d0-c1f871f365f1', 1, '2026-09-15 09:21:57', '10.32.54.168', 'c93bbca7-1cc5-4a78-b761-132dfc94c6e3', '', '2026-09-15 09:21:57', 0);
INSERT INTO `attendance_record` VALUES ('238cef47-ef56-4b9f-aa17-b2c7ac4388c2', '10a7481f-f632-401d-bfd3-582098c0ba2e', 'ade1ab22-f524-4292-bef4-712f162c6ca4', 1, '2026-09-17 09:48:45', '10.32.54.194', '7f6eccbd-448e-4feb-a83f-27c0c7169730', '', '2026-09-17 09:48:45', 0);
INSERT INTO `attendance_record` VALUES ('260ced0d-1c91-4385-978a-38be283c991d', 'f63ed65e-9e31-486e-a894-44d851b7ff46', 'd4c430f1-f17e-4a9c-bb14-38b0dedc3620', 1, '2026-09-15 13:31:36', '10.32.54.189', '02838f4e-546b-44ec-b1be-9bc4d68e83b9', '', '2026-09-15 13:31:36', 0);
INSERT INTO `attendance_record` VALUES ('2a5e5114-47fe-4d68-ab8e-58b28dee50fc', 'f63ed65e-9e31-486e-a894-44d851b7ff46', 'd53a5de6-fe03-4d94-9a03-bd0657d3d16c', 1, '2026-09-15 13:33:16', '10.32.54.182', '8121f2b9-b5b6-4731-b296-0129fb39f4c3', '', '2026-09-15 13:33:16', 0);
INSERT INTO `attendance_record` VALUES ('30a32925-029f-4b76-9bea-9ad7d28432c3', 'f63ed65e-9e31-486e-a894-44d851b7ff46', '604bd35e-15ac-45a5-b074-e4c1ff3a640a', 1, '2026-09-15 14:25:16', '10.32.54.187', 'd96d7558-c63a-4c72-a6fb-0c8001c747ba', '', '2026-09-15 14:25:16', 0);
INSERT INTO `attendance_record` VALUES ('31df90c7-58e5-4da8-85b3-bd1ba784de00', 'bcef9cae-b9cb-407f-8eaa-2183af26b65b', '79bbe579-4eac-4742-ada1-88d076b75e58', 1, '2026-09-17 13:37:37', NULL, NULL, NULL, '2026-09-17 13:37:37', 0);
INSERT INTO `attendance_record` VALUES ('32366165-6ea5-4018-a069-3293b76cac9b', '3da50e8a-2624-4194-9158-2fd830ddc1e7', 'dc65aa73-09d5-44a6-8e6a-28a8c7ccf3cc', 1, '2026-09-16 15:03:05', '10.32.54.195', '7aeb9f88-b72d-42c6-801a-13a4bcd2095c', '', '2026-09-16 15:03:05', 1);
INSERT INTO `attendance_record` VALUES ('3579f170-fd2d-478c-bd1e-0800eabdd244', '10a7481f-f632-401d-bfd3-582098c0ba2e', 'fc9cf5b8-6c70-40ce-af3f-95dc5e747d77', 1, '2026-09-17 09:14:20', '10.32.54.184', 'b427758a-340e-4575-b7b3-9d3db4fba59c', '', '2026-09-17 09:14:20', 0);
INSERT INTO `attendance_record` VALUES ('35b0e035-71f5-4fe5-8d32-ab938cd45bc8', 'f63ed65e-9e31-486e-a894-44d851b7ff46', '03ad6187-14f2-479c-98e4-a65778edbede', 1, '2026-09-15 14:21:26', '10.32.54.159', '397892f4-319e-4db2-8702-5eb7dab40ec9', '', '2026-09-15 14:21:26', 0);
INSERT INTO `attendance_record` VALUES ('3d9ed456-04a1-4b15-92e6-4a71234f2ef0', '3da50e8a-2624-4194-9158-2fd830ddc1e7', 'ade1ab22-f524-4292-bef4-712f162c6ca4', 1, '2026-09-16 15:09:39', '10.32.54.195', 'd08ea885-aba5-4def-8bbd-bd77b7a77ebf', '', '2026-09-16 15:09:39', 1);
INSERT INTO `attendance_record` VALUES ('3e826861-a0e4-484e-aace-c4327e21e830', 'bcef9cae-b9cb-407f-8eaa-2183af26b65b', '80465933-04d0-4aa2-b5cc-4b6bf73cff5a', 1, '2026-09-17 13:37:59', NULL, NULL, NULL, '2026-09-17 13:37:59', 0);
INSERT INTO `attendance_record` VALUES ('40737b48-ce32-4fba-af72-8c654e0bf49c', 'bcef9cae-b9cb-407f-8eaa-2183af26b65b', '604bd35e-15ac-45a5-b074-e4c1ff3a640a', 1, '2026-09-17 13:37:10', NULL, NULL, NULL, '2026-09-17 13:37:10', 0);
INSERT INTO `attendance_record` VALUES ('40fa0daa-423c-4e5e-b768-97e4e71eb1bd', 'bcef9cae-b9cb-407f-8eaa-2183af26b65b', 'fc9cf5b8-6c70-40ce-af3f-95dc5e747d77', 1, '2026-09-17 13:37:16', NULL, NULL, NULL, '2026-09-17 13:37:16', 0);
INSERT INTO `attendance_record` VALUES ('41dd1f75-0f49-4223-a1ce-a4a0d4df80d1', '7ab44183-c982-41db-bdec-6b7df542b544', '72f4bedc-e405-41ef-83e1-370fbf6ee8e4', 1, '2026-09-15 09:12:58', '10.32.54.178', 'fcd59f16-d7ce-41f8-a6f5-edddfb5e5cd8', '', '2026-09-15 09:12:58', 0);
INSERT INTO `attendance_record` VALUES ('421c039b-2684-4362-8efc-91b64125d7e1', '62b72c43-77de-4a08-a122-2de039afcda6', '7185bac0-000b-4aec-bde1-a60b751239e6', 1, '2026-09-16 10:28:03', '10.32.54.193', '7f83e4e5-17fc-4bc6-8b0a-64923796388b', '', '2026-09-16 10:28:03', 0);
INSERT INTO `attendance_record` VALUES ('44fd572c-93d9-4ac8-b0c3-3e1f89788cac', '62b72c43-77de-4a08-a122-2de039afcda6', '833ba07e-d3b8-49ac-a63a-d6f78f3160ec', 1, '2026-09-16 09:38:07', '10.32.54.173', '6c26d765-281a-4859-9593-5d21289b862e', '', '2026-09-16 09:38:07', 0);
INSERT INTO `attendance_record` VALUES ('47653938-6fd4-43bf-b018-209628310357', '62b72c43-77de-4a08-a122-2de039afcda6', '88f956e7-5584-4ab9-9400-f9c3f8630a1e', 1, '2026-09-16 09:09:18', '10.32.54.185', 'c1ad10a7-a537-40f0-aba8-a78948e16506', '', '2026-09-16 09:09:18', 0);
INSERT INTO `attendance_record` VALUES ('4ae0536d-f0e3-40d3-b540-e50866575522', 'f63ed65e-9e31-486e-a894-44d851b7ff46', '043ad3fe-7b96-4999-81d9-abb3bbee0b2d', 1, '2026-09-15 16:19:46', '10.32.54.186', 'c5ebbf0b-ee23-45cf-a68f-813006a8b00c', '', '2026-09-15 16:19:46', 0);
INSERT INTO `attendance_record` VALUES ('4d889da6-9c5f-4dc0-bf5c-9a419febab28', 'bcef9cae-b9cb-407f-8eaa-2183af26b65b', 'ea8c876a-6da1-491c-9b0f-4e3fdbcaae85', 1, '2026-09-17 13:38:16', NULL, NULL, NULL, '2026-09-17 13:38:16', 0);
INSERT INTO `attendance_record` VALUES ('4f3c9e95-212c-479f-b4b6-3b6e4fc89bfa', '7ab44183-c982-41db-bdec-6b7df542b544', 'fc9cf5b8-6c70-40ce-af3f-95dc5e747d77', 1, '2026-09-15 09:15:12', '10.32.54.184', '6624f10b-090f-44dd-b748-5d9149c5f980', '', '2026-09-15 09:15:12', 0);
INSERT INTO `attendance_record` VALUES ('57a0477b-3c87-49bc-9687-1f511c53b180', '3da50e8a-2624-4194-9158-2fd830ddc1e7', '32e210d2-ffe0-4c6c-a11f-787e9f86eb7c', 1, '2026-09-16 15:01:34', '10.32.54.152', '36bc8439-e858-4dbb-ad41-951ce2ea8439', '', '2026-09-16 15:01:34', 0);
INSERT INTO `attendance_record` VALUES ('58812281-301f-4ce7-a2fa-93997235411b', 'bcef9cae-b9cb-407f-8eaa-2183af26b65b', 'f4200def-d5d1-4acf-96d3-13a9e2e8e1cf', 1, '2026-09-17 13:38:26', NULL, NULL, NULL, '2026-09-17 13:38:26', 0);
INSERT INTO `attendance_record` VALUES ('596af533-d003-43d1-bf64-14961507ff49', 'bcef9cae-b9cb-407f-8eaa-2183af26b65b', '043ad3fe-7b96-4999-81d9-abb3bbee0b2d', 1, '2026-09-17 13:37:05', NULL, NULL, NULL, '2026-09-17 13:37:05', 0);
INSERT INTO `attendance_record` VALUES ('59fc92b2-c6ba-468c-8213-9875732a8abd', '7ab44183-c982-41db-bdec-6b7df542b544', '63247c60-41db-4a48-817d-2028251dce81', 1, '2026-09-15 13:05:00', '10.32.54.167', '8050e729-a646-48eb-8895-7510a67451cd', '', '2026-09-15 13:05:00', 0);
INSERT INTO `attendance_record` VALUES ('5cc3e679-1cf2-4631-8df7-1ab5be419d13', '62b72c43-77de-4a08-a122-2de039afcda6', 'd4c430f1-f17e-4a9c-bb14-38b0dedc3620', 1, '2026-09-16 09:12:45', '10.32.54.189', '9bccd882-8df4-4b4e-8749-442539bf073a', '', '2026-09-16 09:12:45', 0);
INSERT INTO `attendance_record` VALUES ('5cca57ac-ed8a-407a-8c99-d156af03c47d', 'f63ed65e-9e31-486e-a894-44d851b7ff46', '1aedebb6-c172-4e7c-ac46-7c3d4ddb956b', 1, '2026-09-15 13:58:29', '10.32.54.188', '5dcaed4c-3b87-4f7c-ac08-1e0ba4e6d8d5', '', '2026-09-15 13:58:29', 0);
INSERT INTO `attendance_record` VALUES ('5e058617-73e3-4b7f-8a5a-6c71cabc5ea8', 'bcef9cae-b9cb-407f-8eaa-2183af26b65b', '63247c60-41db-4a48-817d-2028251dce81', 1, '2026-09-17 13:37:28', NULL, NULL, NULL, '2026-09-17 13:37:28', 0);
INSERT INTO `attendance_record` VALUES ('5ec2684f-9c7e-42ea-9c0a-316455a8b0bb', '3da50e8a-2624-4194-9158-2fd830ddc1e7', '03ad6187-14f2-479c-98e4-a65778edbede', 1, '2026-09-16 14:21:15', '10.32.54.159', '6af31e0f-a54a-46cc-8d93-c6f95b71149a', '', '2026-09-16 14:21:15', 0);
INSERT INTO `attendance_record` VALUES ('612c067d-8efd-4a56-9a94-f68b7409e91f', '62b72c43-77de-4a08-a122-2de039afcda6', '1aedebb6-c172-4e7c-ac46-7c3d4ddb956b', 1, '2026-09-16 09:54:01', '10.32.54.188', 'fdd656b4-e923-4992-a8cc-6f3f3fac4fb1', '', '2026-09-16 09:54:01', 0);
INSERT INTO `attendance_record` VALUES ('61bedec9-e9a4-41cd-a276-ea51fe4b490e', '10a7481f-f632-401d-bfd3-582098c0ba2e', 'd53a5de6-fe03-4d94-9a03-bd0657d3d16c', 1, '2026-09-17 08:49:00', '10.32.54.182', 'c2298e76-4efa-4485-a613-159cd65cb6b0', '', '2026-09-17 08:49:00', 0);
INSERT INTO `attendance_record` VALUES ('621f3250-bb48-4ade-9aa1-ab8a05bd1ae5', '7ab44183-c982-41db-bdec-6b7df542b544', '43ab2c74-6013-437d-a4ea-18bd61e0555c', 1, '2026-09-15 10:08:41', '10.32.54.190', '418c249e-8f40-4625-9b1f-fddecd6940f1', '', '2026-09-15 10:08:41', 0);
INSERT INTO `attendance_record` VALUES ('665ba0d1-4d73-4815-98c9-31cf9a152261', '3da50e8a-2624-4194-9158-2fd830ddc1e7', 'b4170bdf-3fa6-40aa-8711-045e5b7dda0c', 1, '2026-09-16 14:24:54', '10.32.54.169', 'e60e36c1-9363-49ce-a9ab-221de7885fd6', '', '2026-09-16 14:24:54', 1);
INSERT INTO `attendance_record` VALUES ('67069506-cf7b-4996-83ef-43860c5c122c', '7ab44183-c982-41db-bdec-6b7df542b544', '4fa2c113-6ba1-4387-b3d4-cf70be9e2ce1', 1, '2026-09-15 10:56:51', '10.32.54.174', '068aee0f-e7d5-41a5-8f71-1e73accafa29', '', '2026-09-15 10:56:51', 0);
INSERT INTO `attendance_record` VALUES ('67f22bbc-83cc-49d2-a77b-5b5d5a15f5c4', 'bcef9cae-b9cb-407f-8eaa-2183af26b65b', '72f4bedc-e405-41ef-83e1-370fbf6ee8e4', 1, '2026-09-17 13:31:32', '10.32.54.178', '1ee24e03-305c-4425-a0f5-0d2fbf2a020a', '', '2026-09-17 13:31:32', 0);
INSERT INTO `attendance_record` VALUES ('688b3a1a-0b73-4464-b6a0-7b9b469c5a29', '10a7481f-f632-401d-bfd3-582098c0ba2e', '43ab2c74-6013-437d-a4ea-18bd61e0555c', 1, '2026-09-17 08:51:58', '10.32.54.190', '7a3f995d-0aad-47db-999e-aa05a24d9fce', '', '2026-09-17 08:51:58', 1);
INSERT INTO `attendance_record` VALUES ('6974160e-e790-4771-ae4a-5eafef3c84a4', 'bcef9cae-b9cb-407f-8eaa-2183af26b65b', '43ab2c74-6013-437d-a4ea-18bd61e0555c', 1, '2026-09-17 13:37:08', NULL, NULL, NULL, '2026-09-17 13:37:08', 0);
INSERT INTO `attendance_record` VALUES ('69df9d41-e899-4787-865c-94adc72a27f9', 'bcef9cae-b9cb-407f-8eaa-2183af26b65b', 'dc65aa73-09d5-44a6-8e6a-28a8c7ccf3cc', 1, '2026-09-17 13:35:05', '10.32.54.172', '97a1e604-e54a-4373-a004-892f09b33371', '', '2026-09-17 13:35:05', 0);
INSERT INTO `attendance_record` VALUES ('6bc3e43b-ab16-42c9-9508-25561e80e68d', '3da50e8a-2624-4194-9158-2fd830ddc1e7', 'd4c430f1-f17e-4a9c-bb14-38b0dedc3620', 1, '2026-09-16 13:31:49', '10.32.54.189', '31b3ae8c-c5f3-4dc4-bcb8-dedf284997c9', '', '2026-09-16 13:31:49', 0);
INSERT INTO `attendance_record` VALUES ('6d7b2cd0-77c8-4896-b718-8bea76e6f464', 'bcef9cae-b9cb-407f-8eaa-2183af26b65b', 'a0cec1ce-5644-46ad-9870-6fa77fde7ffe', 1, '2026-09-17 13:38:31', NULL, NULL, NULL, '2026-09-17 13:38:31', 0);
INSERT INTO `attendance_record` VALUES ('6fefcae6-a8b2-4f2c-9f21-22c0d773a05c', '10a7481f-f632-401d-bfd3-582098c0ba2e', '4fa2c113-6ba1-4387-b3d4-cf70be9e2ce1', 1, '2026-09-17 09:02:50', '10.32.54.174', '2f0efbb6-79c2-4ce1-ac7d-92810c31ae7d', '', '2026-09-17 09:02:50', 1);
INSERT INTO `attendance_record` VALUES ('7012393d-30bc-4bfd-a69f-962168bf71df', '7ab44183-c982-41db-bdec-6b7df542b544', 'dc65aa73-09d5-44a6-8e6a-28a8c7ccf3cc', 1, '2026-09-15 08:59:31', '10.32.54.195', '7ddc4685-bbe4-480d-ade9-93d60a2f2d74', '', '2026-09-15 08:59:31', 0);
INSERT INTO `attendance_record` VALUES ('711ac9c2-09f9-46c1-88bb-ba2595aa5924', 'bcef9cae-b9cb-407f-8eaa-2183af26b65b', 'd4c430f1-f17e-4a9c-bb14-38b0dedc3620', 1, '2026-09-17 13:35:04', '10.32.54.189', 'b2b2dca9-c082-46bc-af35-895831916e6d', '', '2026-09-17 13:35:04', 0);
INSERT INTO `attendance_record` VALUES ('7369ddda-3aa4-46e7-826e-b9afd0e0f0be', '3da50e8a-2624-4194-9158-2fd830ddc1e7', '88f956e7-5584-4ab9-9400-f9c3f8630a1e', 1, '2026-09-16 13:30:11', '10.32.54.185', 'c1ad10a7-a537-40f0-aba8-a78948e16506', '', '2026-09-16 13:30:11', 0);
INSERT INTO `attendance_record` VALUES ('75484d01-4989-4ce0-aee6-e454c0223e3c', '7ab44183-c982-41db-bdec-6b7df542b544', '604bd35e-15ac-45a5-b074-e4c1ff3a640a', 1, '2026-09-15 09:07:25', '10.32.54.187', 'd96d7558-c63a-4c72-a6fb-0c8001c747ba', '', '2026-09-15 09:07:25', 0);
INSERT INTO `attendance_record` VALUES ('7891d88c-267a-4b82-958d-58a45f98186c', '62b72c43-77de-4a08-a122-2de039afcda6', '043ad3fe-7b96-4999-81d9-abb3bbee0b2d', 1, '2026-09-16 09:08:32', '10.32.54.186', '53642840-6c05-48b8-8996-947c955cd07c', '', '2026-09-16 09:08:32', 0);
INSERT INTO `attendance_record` VALUES ('7c094e23-a854-4aa1-acb5-a9418dbbfc92', '10a7481f-f632-401d-bfd3-582098c0ba2e', '72f4bedc-e405-41ef-83e1-370fbf6ee8e4', 1, '2026-09-17 09:06:29', '10.32.54.178', '7766ca94-7963-40c6-807c-7b00131eee4a', '', '2026-09-17 09:06:29', 1);
INSERT INTO `attendance_record` VALUES ('7c205696-fddb-4f18-a650-dad9323a4b1e', '3da50e8a-2624-4194-9158-2fd830ddc1e7', '80465933-04d0-4aa2-b5cc-4b6bf73cff5a', 1, '2026-09-16 15:06:58', '10.32.54.153', '37e5ac5b-712b-43ca-9b53-b906bb31693c', '', '2026-09-16 15:06:58', 0);
INSERT INTO `attendance_record` VALUES ('7c4ab3da-d024-4b68-98a1-53476b72fd96', '62b72c43-77de-4a08-a122-2de039afcda6', '43ab2c74-6013-437d-a4ea-18bd61e0555c', 1, '2026-09-16 09:49:49', '10.32.54.190', 'f48c7aa5-b466-4523-b40a-ccc795f59202', '', '2026-09-16 09:49:49', 0);
INSERT INTO `attendance_record` VALUES ('7c551e0b-cce4-4eef-acc4-9023984694cc', 'bcef9cae-b9cb-407f-8eaa-2183af26b65b', 'b4170bdf-3fa6-40aa-8711-045e5b7dda0c', 1, '2026-09-17 13:37:04', NULL, NULL, NULL, '2026-09-17 13:37:04', 0);
INSERT INTO `attendance_record` VALUES ('7d36bf5a-1a4b-4614-ac32-28fb29b9d1aa', '7ab44183-c982-41db-bdec-6b7df542b544', '87922d2d-600c-4a17-ac2e-50a1f5dd217c', 1, '2026-09-15 10:53:51', '10.32.54.173', '66864167-bb7b-4791-8f3e-debcc00a6581', '', '2026-09-15 10:53:51', 0);
INSERT INTO `attendance_record` VALUES ('7f4974c0-3e09-4461-a9f7-dfbb4ef52b30', '3da50e8a-2624-4194-9158-2fd830ddc1e7', '63247c60-41db-4a48-817d-2028251dce81', 1, '2026-09-16 13:32:33', '10.32.54.167', '83287560-5e69-4a24-ab82-6f78acd1dae8', '', '2026-09-16 13:32:33', 0);
INSERT INTO `attendance_record` VALUES ('83dd14c1-7c8d-4d67-9ba6-684fb141d33b', '7ab44183-c982-41db-bdec-6b7df542b544', '7185bac0-000b-4aec-bde1-a60b751239e6', 1, '2026-09-15 09:11:28', '10.32.54.193', '75644e7a-ab37-47db-9122-5f5719fe28f1', '', '2026-09-15 09:11:28', 0);
INSERT INTO `attendance_record` VALUES ('85b9c9bd-64fe-4ce3-9083-c2131fa8e3b0', '10a7481f-f632-401d-bfd3-582098c0ba2e', 'dc65aa73-09d5-44a6-8e6a-28a8c7ccf3cc', 1, '2026-09-17 09:01:55', '10.32.54.172', '3df74e08-343a-4826-9da5-66b7186a2d63', '', '2026-09-17 09:01:55', 1);
INSERT INTO `attendance_record` VALUES ('85baace4-1b9e-40fb-ba8e-c2251cc47299', 'f63ed65e-9e31-486e-a894-44d851b7ff46', '63247c60-41db-4a48-817d-2028251dce81', 1, '2026-09-15 14:29:40', '10.32.54.167', '8050e729-a646-48eb-8895-7510a67451cd', '', '2026-09-15 14:29:40', 0);
INSERT INTO `attendance_record` VALUES ('86804cec-8801-4534-9a72-4e14559d03d3', 'bcef9cae-b9cb-407f-8eaa-2183af26b65b', 'a18e8e26-8752-4c9e-b6fb-a25457eca40a', 1, '2026-09-17 13:37:24', NULL, NULL, NULL, '2026-09-17 13:37:24', 0);
INSERT INTO `attendance_record` VALUES ('87c5b9a7-52ce-4e7b-900d-c3c93faee55d', '62b72c43-77de-4a08-a122-2de039afcda6', 'ade1ab22-f524-4292-bef4-712f162c6ca4', 1, '2026-09-16 10:30:03', '10.32.54.193', 'e735f280-51ef-439c-85bf-aa41ed05d8f0', '', '2026-09-16 10:30:03', 1);
INSERT INTO `attendance_record` VALUES ('88ed859b-482c-4c1a-bc65-78c43fc572ca', '3da50e8a-2624-4194-9158-2fd830ddc1e7', '1aedebb6-c172-4e7c-ac46-7c3d4ddb956b', 1, '2026-09-16 13:34:14', '10.32.54.188', 'fdd656b4-e923-4992-a8cc-6f3f3fac4fb1', '', '2026-09-16 13:34:14', 0);
INSERT INTO `attendance_record` VALUES ('8bb228f8-ccce-48a5-a18f-712411e7d28d', 'bcef9cae-b9cb-407f-8eaa-2183af26b65b', '277aadad-a0c0-4ce1-8cb6-f826ad252538', 1, '2026-09-17 13:38:00', NULL, NULL, NULL, '2026-09-17 13:38:00', 0);
INSERT INTO `attendance_record` VALUES ('8e38ae10-3e9c-46b2-9fa3-fbd6c76ac404', '10a7481f-f632-401d-bfd3-582098c0ba2e', '1aedebb6-c172-4e7c-ac46-7c3d4ddb956b', 1, '2026-09-17 09:12:35', '10.32.54.188', '06e741c1-8ec8-44ad-a8d6-f08a6da5aa60', '', '2026-09-17 09:12:35', 1);
INSERT INTO `attendance_record` VALUES ('8f30ef7c-75cc-4537-8e72-c839e4ff001e', 'bcef9cae-b9cb-407f-8eaa-2183af26b65b', '1aedebb6-c172-4e7c-ac46-7c3d4ddb956b', 1, '2026-09-17 13:37:06', NULL, NULL, NULL, '2026-09-17 13:37:06', 0);
INSERT INTO `attendance_record` VALUES ('904d4fbd-7cf6-4d69-ac46-4113a84623f9', '3da50e8a-2624-4194-9158-2fd830ddc1e7', '7185bac0-000b-4aec-bde1-a60b751239e6', 1, '2026-09-16 14:34:47', '10.32.54.193', '7f83e4e5-17fc-4bc6-8b0a-64923796388b', '', '2026-09-16 14:34:47', 0);
INSERT INTO `attendance_record` VALUES ('9321c778-8756-4c68-b51c-fb7ce632b888', 'bcef9cae-b9cb-407f-8eaa-2183af26b65b', '833ba07e-d3b8-49ac-a63a-d6f78f3160ec', 1, '2026-09-17 13:38:46', NULL, NULL, NULL, '2026-09-17 13:38:46', 0);
INSERT INTO `attendance_record` VALUES ('9ceb00ae-db65-4b1e-8f22-32855e596c73', '62b72c43-77de-4a08-a122-2de039afcda6', 'b4170bdf-3fa6-40aa-8711-045e5b7dda0c', 1, '2026-09-16 11:16:36', '10.32.54.169', '1b1cfbbc-a8c2-4e53-89a7-117f5f787038', '', '2026-09-16 11:16:36', 1);
INSERT INTO `attendance_record` VALUES ('9d560206-d860-4e85-ac11-558703c6d190', 'bcef9cae-b9cb-407f-8eaa-2183af26b65b', '880cbd99-d6a7-4f33-85d0-c1f871f365f1', 1, '2026-09-17 13:37:30', NULL, NULL, NULL, '2026-09-17 13:37:30', 0);
INSERT INTO `attendance_record` VALUES ('a2144489-d679-4b09-b1e8-6f4213df52a6', 'f63ed65e-9e31-486e-a894-44d851b7ff46', '88f956e7-5584-4ab9-9400-f9c3f8630a1e', 1, '2026-09-15 16:17:22', '10.32.54.185', 'c1108b33-c9a4-45f7-98d5-37bea6e3a31e', '', '2026-09-15 16:17:22', 0);
INSERT INTO `attendance_record` VALUES ('a450a478-91e5-42d9-829f-a3ef3e1975fc', '3da50e8a-2624-4194-9158-2fd830ddc1e7', '79bbe579-4eac-4742-ada1-88d076b75e58', 1, '2026-09-16 14:29:24', '10.32.54.170', '1148b82a-cbe5-4fd9-9799-76dc32fbd289', '', '2026-09-16 14:29:24', 1);
INSERT INTO `attendance_record` VALUES ('a5ec1592-f302-4639-85fa-c97732d180b3', 'bcef9cae-b9cb-407f-8eaa-2183af26b65b', '323d5575-b163-4af6-a702-7634f354bb64', 1, '2026-09-17 13:38:45', NULL, NULL, NULL, '2026-09-17 13:38:45', 0);
INSERT INTO `attendance_record` VALUES ('a71d16d7-85ec-4f4b-a41a-4e448997e74b', '7ab44183-c982-41db-bdec-6b7df542b544', '1aedebb6-c172-4e7c-ac46-7c3d4ddb956b', 1, '2026-09-15 09:09:04', '10.32.54.188', '5dcaed4c-3b87-4f7c-ac08-1e0ba4e6d8d5', '', '2026-09-15 09:09:04', 0);
INSERT INTO `attendance_record` VALUES ('a8ab0210-e6bf-41e8-8005-456cc6a09304', 'f63ed65e-9e31-486e-a894-44d851b7ff46', '7185bac0-000b-4aec-bde1-a60b751239e6', 1, '2026-09-15 14:38:39', '10.32.54.193', '75644e7a-ab37-47db-9122-5f5719fe28f1', '', '2026-09-15 14:38:39', 0);
INSERT INTO `attendance_record` VALUES ('a936a9a0-3211-4fbc-bcb0-0d948aebffef', '7ab44183-c982-41db-bdec-6b7df542b544', 'd53a5de6-fe03-4d94-9a03-bd0657d3d16c', 1, '2026-09-15 09:12:31', '10.32.54.182', '8121f2b9-b5b6-4731-b296-0129fb39f4c3', '', '2026-09-15 09:12:31', 0);
INSERT INTO `attendance_record` VALUES ('a9b1d229-f5e1-4f1c-9d99-28252ff36656', '7ab44183-c982-41db-bdec-6b7df542b544', 'ea8c876a-6da1-491c-9b0f-4e3fdbcaae85', 1, '2026-09-15 09:13:07', '10.32.54.179', 'f9478743-0249-4470-9131-ff795658e041', '', '2026-09-15 09:13:07', 0);
INSERT INTO `attendance_record` VALUES ('ac1c5416-7a7c-4976-ae53-f86d439a8769', '10a7481f-f632-401d-bfd3-582098c0ba2e', '805aab46-33c1-46e2-b902-ca30607e5fac', 1, '2026-09-17 10:41:59', '10.32.54.165', 'ee622b00-40ab-44a4-9b45-09c88fbd1844', '', '2026-09-17 10:41:59', 0);
INSERT INTO `attendance_record` VALUES ('ae892a22-e159-4443-8625-dd3917153c76', '62b72c43-77de-4a08-a122-2de039afcda6', 'd53a5de6-fe03-4d94-9a03-bd0657d3d16c', 1, '2026-09-16 09:08:18', '10.32.54.182', 'daba772a-0a75-4fd8-9871-27e665ad4022', '', '2026-09-16 09:08:18', 0);
INSERT INTO `attendance_record` VALUES ('b059f891-cdcd-43b0-b7fe-eef7c25e7a3f', 'bcef9cae-b9cb-407f-8eaa-2183af26b65b', '595af00f-652f-4780-b256-e4ab875e5b7b', 1, '2026-09-17 13:38:03', NULL, NULL, NULL, '2026-09-17 13:38:03', 0);
INSERT INTO `attendance_record` VALUES ('bc4c5a48-923b-4f76-8579-3f2d5cf18142', 'f63ed65e-9e31-486e-a894-44d851b7ff46', '80465933-04d0-4aa2-b5cc-4b6bf73cff5a', 1, '2026-09-15 13:34:01', '10.32.54.153', '37e5ac5b-712b-43ca-9b53-b906bb31693c', '', '2026-09-15 13:34:01', 0);
INSERT INTO `attendance_record` VALUES ('bcfd6b2f-107a-48fa-9f4c-356c8ac99a48', '7ab44183-c982-41db-bdec-6b7df542b544', '79bbe579-4eac-4742-ada1-88d076b75e58', 1, '2026-09-15 09:43:18', '10.32.54.170', '0a3dd5fa-4469-4792-baf3-c0c66dccb8f7', '', '2026-09-15 09:43:18', 0);
INSERT INTO `attendance_record` VALUES ('c227e2e2-55c3-484b-96be-374a1b543b81', '7ab44183-c982-41db-bdec-6b7df542b544', 'd4c430f1-f17e-4a9c-bb14-38b0dedc3620', 1, '2026-09-15 09:06:58', '10.32.54.189', '02838f4e-546b-44ec-b1be-9bc4d68e83b9', '', '2026-09-15 09:06:58', 0);
INSERT INTO `attendance_record` VALUES ('c2f1ff89-8c64-4f18-8cd2-95816c04560f', '10a7481f-f632-401d-bfd3-582098c0ba2e', '043ad3fe-7b96-4999-81d9-abb3bbee0b2d', 1, '2026-09-17 09:25:00', '10.32.54.186', 'de237557-d117-4975-ac1e-8db8040f1c0c', '', '2026-09-17 09:25:00', 1);
INSERT INTO `attendance_record` VALUES ('c3131cb5-a2b2-4089-8faa-3bad4558d77b', 'bcef9cae-b9cb-407f-8eaa-2183af26b65b', '88f956e7-5584-4ab9-9400-f9c3f8630a1e', 1, '2026-09-17 13:38:47', NULL, NULL, NULL, '2026-09-17 13:38:47', 0);
INSERT INTO `attendance_record` VALUES ('c33ccde4-e908-4481-900d-d9ce761898c2', 'bcef9cae-b9cb-407f-8eaa-2183af26b65b', '32e210d2-ffe0-4c6c-a11f-787e9f86eb7c', 1, '2026-09-17 13:39:04', NULL, NULL, NULL, '2026-09-17 13:39:04', 0);
INSERT INTO `attendance_record` VALUES ('c39b39f7-42f5-46a5-bcd8-cfbc1c1255e6', 'bcef9cae-b9cb-407f-8eaa-2183af26b65b', 'd9c1c663-0678-4018-8952-61c8d10c8c8b', 1, '2026-09-17 13:38:04', NULL, NULL, NULL, '2026-09-17 13:38:04', 0);
INSERT INTO `attendance_record` VALUES ('c62c5605-3eb2-47b2-ae49-d56054c9671a', 'bcef9cae-b9cb-407f-8eaa-2183af26b65b', '87922d2d-600c-4a17-ac2e-50a1f5dd217c', 1, '2026-09-17 13:38:48', NULL, NULL, NULL, '2026-09-17 13:38:48', 0);
INSERT INTO `attendance_record` VALUES ('c878b58b-3541-4006-9c2e-3022f18ab44d', '7ab44183-c982-41db-bdec-6b7df542b544', 'b4170bdf-3fa6-40aa-8711-045e5b7dda0c', 1, '2026-09-15 09:21:17', '10.32.54.169', '5f150189-2124-4de7-8fc6-e2dcb295f950', '', '2026-09-15 09:21:17', 0);
INSERT INTO `attendance_record` VALUES ('ca40914c-0771-4613-aea1-9c6d59ad6c65', '10a7481f-f632-401d-bfd3-582098c0ba2e', '833ba07e-d3b8-49ac-a63a-d6f78f3160ec', 1, '2026-09-17 08:55:34', '10.32.54.173', '7924e227-6a06-4202-92b3-6604fca31fb1', '', '2026-09-17 08:55:34', 1);
INSERT INTO `attendance_record` VALUES ('ce5e9130-2f7c-46c3-bc52-71a9c9e915c0', '3da50e8a-2624-4194-9158-2fd830ddc1e7', '87922d2d-600c-4a17-ac2e-50a1f5dd217c', 1, '2026-09-16 14:20:00', '10.32.54.158', '08b274ab-4c86-433a-b9c8-1a3e5aaad74a', '', '2026-09-16 14:20:00', 0);
INSERT INTO `attendance_record` VALUES ('d152a104-0f48-4cf7-8f15-fcf681fc11a6', '62b72c43-77de-4a08-a122-2de039afcda6', 'ad72f7e1-4742-44a3-86c9-6d9e3c41cdf9', 1, '2026-09-16 09:05:58', '10.32.54.195', '7fd2a67e-e296-40b2-9d63-460c35b7ba51', '', '2026-09-16 09:05:58', 0);
INSERT INTO `attendance_record` VALUES ('d48c4f5a-3eff-43b4-8f2d-a5e06ff94868', 'f63ed65e-9e31-486e-a894-44d851b7ff46', '43ab2c74-6013-437d-a4ea-18bd61e0555c', 1, '2026-09-15 13:30:53', '10.32.54.190', '418c249e-8f40-4625-9b1f-fddecd6940f1', '', '2026-09-15 13:30:53', 0);
INSERT INTO `attendance_record` VALUES ('d5b306e0-6f58-4fd4-85fe-b71d5efff2fa', 'f63ed65e-9e31-486e-a894-44d851b7ff46', '72f4bedc-e405-41ef-83e1-370fbf6ee8e4', 1, '2026-09-15 15:14:49', '10.32.54.178', '9173ea5c-6a0f-4753-a451-d2dccb91d089', '', '2026-09-15 15:14:49', 0);
INSERT INTO `attendance_record` VALUES ('d66ddc11-4bc1-4b3d-ac5d-36935874b87e', 'bcef9cae-b9cb-407f-8eaa-2183af26b65b', 'ad72f7e1-4742-44a3-86c9-6d9e3c41cdf9', 1, '2026-09-17 13:35:54', NULL, NULL, NULL, '2026-09-17 13:35:54', 0);
INSERT INTO `attendance_record` VALUES ('d99b1d86-f9ef-4cce-9a86-323655600330', 'bcef9cae-b9cb-407f-8eaa-2183af26b65b', 'ade1ab22-f524-4292-bef4-712f162c6ca4', 1, '2026-09-17 13:38:49', NULL, NULL, NULL, '2026-09-17 13:38:49', 0);
INSERT INTO `attendance_record` VALUES ('d9eff77c-3b48-48b5-b29c-c9948408489b', 'bcef9cae-b9cb-407f-8eaa-2183af26b65b', '805aab46-33c1-46e2-b902-ca30607e5fac', 1, '2026-09-17 13:37:56', NULL, NULL, NULL, '2026-09-17 13:37:56', 0);
INSERT INTO `attendance_record` VALUES ('e15fc64f-8f0d-4843-b7b6-32de49b56a91', 'f63ed65e-9e31-486e-a894-44d851b7ff46', '880cbd99-d6a7-4f33-85d0-c1f871f365f1', 1, '2026-09-15 14:32:53', '10.32.54.168', 'c1db304a-e4a3-4d33-b76d-391b53dbf16b', '', '2026-09-15 14:32:53', 0);
INSERT INTO `attendance_record` VALUES ('e5ebec37-404e-4d12-bba5-83299b9495bb', 'bcef9cae-b9cb-407f-8eaa-2183af26b65b', 'b9ffafa9-c0af-4bd4-acb5-a5f9d9ba84ca', 1, '2026-09-17 13:38:51', NULL, NULL, NULL, '2026-09-17 13:38:51', 0);
INSERT INTO `attendance_record` VALUES ('e95d885d-394e-41ef-bf32-86a355b9ac61', '62b72c43-77de-4a08-a122-2de039afcda6', '79bbe579-4eac-4742-ada1-88d076b75e58', 1, '2026-09-16 11:05:02', '10.32.54.170', '7a861ee1-bce1-4ae6-8ea3-b13a1a17b55b', '', '2026-09-16 11:05:02', 0);
INSERT INTO `attendance_record` VALUES ('ebd05657-3da8-4de6-9584-9a7ec5175f3b', '10a7481f-f632-401d-bfd3-582098c0ba2e', '7185bac0-000b-4aec-bde1-a60b751239e6', 1, '2026-09-17 08:48:21', '10.32.54.193', 'e634918b-d99a-44f6-a447-48c7374afde5', '', '2026-09-17 08:48:21', 0);
INSERT INTO `attendance_record` VALUES ('ee9f1f89-ab4e-434a-b309-603691dfe4b7', '10a7481f-f632-401d-bfd3-582098c0ba2e', '79bbe579-4eac-4742-ada1-88d076b75e58', 1, '2026-09-17 09:39:47', '10.32.54.170', '6632ab9c-aaa6-4591-a2a6-43c8d373503b', '', '2026-09-17 09:39:47', 1);
INSERT INTO `attendance_record` VALUES ('ef58a151-b540-44af-97f5-03a337ce4461', 'f63ed65e-9e31-486e-a894-44d851b7ff46', 'ea8c876a-6da1-491c-9b0f-4e3fdbcaae85', 1, '2026-09-15 15:14:31', '10.32.54.179', '8725da14-df60-45de-a748-cbba1578ea03', '', '2026-09-15 15:14:31', 0);
INSERT INTO `attendance_record` VALUES ('effd067a-b8c2-4bf2-9fce-5f842b16c70e', '3da50e8a-2624-4194-9158-2fd830ddc1e7', '880cbd99-d6a7-4f33-85d0-c1f871f365f1', 1, '2026-09-16 14:25:33', '10.32.54.168', '91ea6117-a778-43b9-9390-94c8f02e7e6d', '', '2026-09-16 14:25:33', 0);
INSERT INTO `attendance_record` VALUES ('f2bd70d2-0a1e-4209-9eb9-68d3fdb968d7', 'bcef9cae-b9cb-407f-8eaa-2183af26b65b', 'f1745c3f-3ceb-49bd-9caa-47f7314178cb', 1, '2026-09-17 13:37:59', NULL, NULL, NULL, '2026-09-17 13:37:59', 0);
INSERT INTO `attendance_record` VALUES ('f9f76e18-f09a-499a-a162-6719f936cbf0', 'bcef9cae-b9cb-407f-8eaa-2183af26b65b', 'be6f193a-af0e-4165-ad33-3d999b5f6dad', 1, '2026-09-17 13:38:15', NULL, NULL, NULL, '2026-09-17 13:38:15', 0);
INSERT INTO `attendance_record` VALUES ('fb563c58-e898-45a6-b8ed-3076fd918554', '10a7481f-f632-401d-bfd3-582098c0ba2e', '604bd35e-15ac-45a5-b074-e4c1ff3a640a', 1, '2026-09-17 08:54:14', '10.32.54.187', '170b51ae-c6c9-47d8-b4c0-711ed0d11472', '', '2026-09-17 08:54:14', 1);
INSERT INTO `attendance_record` VALUES ('fbb443bb-d791-4669-9d57-a886e47118d0', 'bcef9cae-b9cb-407f-8eaa-2183af26b65b', '9a0838ed-ee1b-4644-b39a-67db34bc8e2d', 1, '2026-09-17 13:39:01', NULL, NULL, NULL, '2026-09-17 13:39:01', 0);
INSERT INTO `attendance_record` VALUES ('fcf14d7c-6f4e-45c9-99f0-34fe4c16e5ae', 'bcef9cae-b9cb-407f-8eaa-2183af26b65b', 'c5bb83cc-c8af-4fe6-a782-220676b6af08', 1, '2026-09-17 13:37:20', NULL, NULL, NULL, '2026-09-17 13:37:20', 0);

-- ----------------------------
-- Table structure for attendance_task
-- ----------------------------
DROP TABLE IF EXISTS `attendance_task`;
CREATE TABLE `attendance_task`  (
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '签到任务UUID',
  `course_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '课程ID',
  `start_time` datetime(0) NOT NULL COMMENT '签到开始时间',
  `end_time` datetime(0) NOT NULL COMMENT '签到结束时间',
  `status` tinyint(0) NOT NULL DEFAULT 1 COMMENT '签到任务状态 1进行中 0已结束',
  `create_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0) COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_attendance_task_course_id`(`course_id`) USING BTREE,
  INDEX `idx_attendance_task_status`(`status`) USING BTREE,
  INDEX `idx_attendance_task_time`(`start_time`, `end_time`) USING BTREE,
  CONSTRAINT `fk_attendance_task_course` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '签到任务表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of attendance_task
-- ----------------------------
INSERT INTO `attendance_task` VALUES ('10a7481f-f632-401d-bfd3-582098c0ba2e', '93cfe390-b0cd-11f1-b67d-186024adaeb4', '2026-09-17 08:30:00', '2026-09-17 11:50:00', 1, '2026-09-17 08:47:29');
INSERT INTO `attendance_task` VALUES ('3da50e8a-2624-4194-9158-2fd830ddc1e7', '22647393-b33a-4992-8645-fbb205c4fe9b', '2026-09-16 13:30:00', '2026-09-16 17:00:00', 1, '2026-09-16 13:29:41');
INSERT INTO `attendance_task` VALUES ('62b72c43-77de-4a08-a122-2de039afcda6', '6faeca60-7d7d-4158-8fea-ea9c71bff11d', '2026-09-16 08:30:00', '2026-09-16 11:50:00', 1, '2026-09-16 09:04:16');
INSERT INTO `attendance_task` VALUES ('7ab44183-c982-41db-bdec-6b7df542b544', 'fd93ed87-70c8-48f0-9581-27afcadb54c2', '2026-09-15 08:30:00', '2026-09-15 13:30:00', 1, '2026-09-15 08:59:04');
INSERT INTO `attendance_task` VALUES ('bcef9cae-b9cb-407f-8eaa-2183af26b65b', '93cff7c8-b0cd-11f1-b67d-186024adaeb4', '2026-09-17 13:30:00', '2026-09-17 15:10:00', 1, '2026-09-17 13:23:52');
INSERT INTO `attendance_task` VALUES ('f63ed65e-9e31-486e-a894-44d851b7ff46', 'cbeef8b1-4855-4a75-b9af-f6efa5d143b8', '2026-09-15 13:30:00', '2026-09-15 17:10:00', 1, '2026-09-15 13:24:43');

-- ----------------------------
-- Table structure for classes
-- ----------------------------
DROP TABLE IF EXISTS `classes`;
CREATE TABLE `classes`  (
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '班级UUID',
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '班级名称',
  `grade` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '年级',
  `teacher_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '班主任ID',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_classes_name`(`name`) USING BTREE,
  INDEX `idx_classes_teacher_id`(`teacher_id`) USING BTREE,
  CONSTRAINT `fk_class_teacher` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '班级表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of classes
-- ----------------------------
INSERT INTO `classes` VALUES ('30000000-0000-0000-0000-000000000001', '软件2401班', '2024级', NULL);
INSERT INTO `classes` VALUES ('30000000-0000-0000-0000-000000000002', '软件2402班', '2024级', NULL);
INSERT INTO `classes` VALUES ('30000000-0000-0000-0000-000000000003', '计算机2401班', '2024级', NULL);
INSERT INTO `classes` VALUES ('abfb5cae-84d4-4aff-b893-40cd42666d18', '大数据2532013', '2025级', NULL);

-- ----------------------------
-- Table structure for courses
-- ----------------------------
DROP TABLE IF EXISTS `courses`;
CREATE TABLE `courses`  (
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '课程UUID',
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '课程名称',
  `teacher_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '授课教师ID',
  `class_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '班级ID',
  `course_date` date NULL DEFAULT NULL COMMENT '上课日期，例如 2026-09-14',
  `time` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '上课时间段，例如 08:00-09:40',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_courses_teacher_id`(`teacher_id`) USING BTREE,
  INDEX `idx_courses_class_id`(`class_id`) USING BTREE,
  INDEX `idx_courses_course_date`(`course_date`) USING BTREE,
  INDEX `idx_courses_class_date`(`class_id`, `course_date`) USING BTREE,
  CONSTRAINT `fk_course_class` FOREIGN KEY (`class_id`) REFERENCES `classes` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_course_teacher` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '课程表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of courses
-- ----------------------------
INSERT INTO `courses` VALUES ('22647393-b33a-4992-8645-fbb205c4fe9b', '生产性实训', 'f9cc3f0b-4dee-4ba3-81da-982c8dd41642', 'abfb5cae-84d4-4aff-b893-40cd42666d18', '2026-09-16', '13:30-17:00');
INSERT INTO `courses` VALUES ('6faeca60-7d7d-4158-8fea-ea9c71bff11d', '生产性实训', 'f9cc3f0b-4dee-4ba3-81da-982c8dd41642', 'abfb5cae-84d4-4aff-b893-40cd42666d18', '2026-09-16', '08:30-11:50');
INSERT INTO `courses` VALUES ('93cfe390-b0cd-11f1-b67d-186024adaeb4', '生产性实训', 'f9cc3f0b-4dee-4ba3-81da-982c8dd41642', 'abfb5cae-84d4-4aff-b893-40cd42666d18', '2026-09-17', '08:30-11:50');
INSERT INTO `courses` VALUES ('93cff7c8-b0cd-11f1-b67d-186024adaeb4', '生产性实训', 'f9cc3f0b-4dee-4ba3-81da-982c8dd41642', 'abfb5cae-84d4-4aff-b893-40cd42666d18', '2026-09-17', '13:30-15:10');
INSERT INTO `courses` VALUES ('93db647c-b0cd-11f1-b67d-186024adaeb4', '生产性实训', 'f9cc3f0b-4dee-4ba3-81da-982c8dd41642', 'abfb5cae-84d4-4aff-b893-40cd42666d18', '2026-09-21', '08:30-11:50');
INSERT INTO `courses` VALUES ('93db6dd4-b0cd-11f1-b67d-186024adaeb4', '生产性实训', 'f9cc3f0b-4dee-4ba3-81da-982c8dd41642', 'abfb5cae-84d4-4aff-b893-40cd42666d18', '2026-09-21', '13:30-15:10');
INSERT INTO `courses` VALUES ('93db7108-b0cd-11f1-b67d-186024adaeb4', '生产性实训', 'f9cc3f0b-4dee-4ba3-81da-982c8dd41642', 'abfb5cae-84d4-4aff-b893-40cd42666d18', '2026-09-22', '08:30-11:50');
INSERT INTO `courses` VALUES ('93db736a-b0cd-11f1-b67d-186024adaeb4', '生产性实训', 'f9cc3f0b-4dee-4ba3-81da-982c8dd41642', 'abfb5cae-84d4-4aff-b893-40cd42666d18', '2026-09-22', '13:30-17:00');
INSERT INTO `courses` VALUES ('93db75e7-b0cd-11f1-b67d-186024adaeb4', '生产性实训', 'f9cc3f0b-4dee-4ba3-81da-982c8dd41642', 'abfb5cae-84d4-4aff-b893-40cd42666d18', '2026-09-23', '08:30-11:50');
INSERT INTO `courses` VALUES ('93db7854-b0cd-11f1-b67d-186024adaeb4', '生产性实训', 'f9cc3f0b-4dee-4ba3-81da-982c8dd41642', 'abfb5cae-84d4-4aff-b893-40cd42666d18', '2026-09-23', '13:30-17:00');
INSERT INTO `courses` VALUES ('93db7ab9-b0cd-11f1-b67d-186024adaeb4', '生产性实训', 'f9cc3f0b-4dee-4ba3-81da-982c8dd41642', 'abfb5cae-84d4-4aff-b893-40cd42666d18', '2026-09-24', '08:30-11:50');
INSERT INTO `courses` VALUES ('93db7cec-b0cd-11f1-b67d-186024adaeb4', '生产性实训', 'f9cc3f0b-4dee-4ba3-81da-982c8dd41642', 'abfb5cae-84d4-4aff-b893-40cd42666d18', '2026-09-24', '13:30-15:10');
INSERT INTO `courses` VALUES ('cbeef8b1-4855-4a75-b9af-f6efa5d143b8', '生产性实训', 'f9cc3f0b-4dee-4ba3-81da-982c8dd41642', 'abfb5cae-84d4-4aff-b893-40cd42666d18', '2026-09-15', '13:30-17:00');
INSERT INTO `courses` VALUES ('fd93ed87-70c8-48f0-9581-27afcadb54c2', '生产性实训', 'f9cc3f0b-4dee-4ba3-81da-982c8dd41642', 'abfb5cae-84d4-4aff-b893-40cd42666d18', '2026-09-15', '08:30-11:50');

-- ----------------------------
-- Table structure for device_login_record
-- ----------------------------
DROP TABLE IF EXISTS `device_login_record`;
CREATE TABLE `device_login_record`  (
  `id` bigint(0) NOT NULL AUTO_INCREMENT COMMENT '记录ID',
  `device_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '设备唯一标识',
  `user_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '当天登录的用户ID',
  `login_date` date NOT NULL COMMENT '登录日期',
  `login_time` datetime(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0) COMMENT '首次登录时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_device_login_date`(`device_id`, `login_date`) USING BTREE,
  INDEX `idx_device_login_user_id`(`user_id`) USING BTREE,
  INDEX `idx_device_login_date`(`login_date`) USING BTREE,
  CONSTRAINT `fk_device_login_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 198 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '每日设备登录记录表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of device_login_record
-- ----------------------------
INSERT INTO `device_login_record` VALUES (210, '46f44e94-d787-416e-aeaf-f1def1e2d761', '04fd5084-7d3e-4f5a-8f02-b80c356e9ea7', '2026-09-17', '2026-09-17 09:07:00');
INSERT INTO `device_login_record` VALUES (211, 'e634918b-d99a-44f6-a447-48c7374afde5', '24f5bbe6-30cd-45d9-bf9e-e26aa46ad099', '2026-09-17', '2026-09-17 09:07:06');
INSERT INTO `device_login_record` VALUES (212, '06e741c1-8ec8-44ad-a8d6-f08a6da5aa60', '1082a22c-0041-42ad-865f-013a37e0e32c', '2026-09-17', '2026-09-17 09:12:32');
INSERT INTO `device_login_record` VALUES (213, 'b427758a-340e-4575-b7b3-9d3db4fba59c', 'ecd3b094-d6e7-49cb-bd7a-4700091a5276', '2026-09-17', '2026-09-17 09:14:18');
INSERT INTO `device_login_record` VALUES (214, 'de237557-d117-4975-ac1e-8db8040f1c0c', 'f40de929-ca2a-4381-a62a-c34b43ba2ae9', '2026-09-17', '2026-09-17 09:24:57');
INSERT INTO `device_login_record` VALUES (215, 'f0454566-38c3-4364-bd17-aa55db32c523', 'f40de929-ca2a-4381-a62a-c34b43ba2ae9', '2026-09-17', '2026-09-17 09:25:54');
INSERT INTO `device_login_record` VALUES (216, 'fda15b2e-e9cd-47b2-bf61-c5043228993a', 'f40de929-ca2a-4381-a62a-c34b43ba2ae9', '2026-09-17', '2026-09-17 09:26:24');
INSERT INTO `device_login_record` VALUES (217, '233ab20e-6faf-4015-8897-2b1658a75a86', 'f40de929-ca2a-4381-a62a-c34b43ba2ae9', '2026-09-17', '2026-09-17 09:27:53');
INSERT INTO `device_login_record` VALUES (218, '674b8fd2-773c-4546-ae58-727aad8ea466', 'f40de929-ca2a-4381-a62a-c34b43ba2ae9', '2026-09-17', '2026-09-17 09:28:49');
INSERT INTO `device_login_record` VALUES (219, '7d86ce19-d0cf-4ed0-8462-d2eb0840432f', 'f40de929-ca2a-4381-a62a-c34b43ba2ae9', '2026-09-17', '2026-09-17 09:30:57');
INSERT INTO `device_login_record` VALUES (220, 'c52c7371-69ae-45ed-bdf4-8d13295a4168', '1082a22c-0041-42ad-865f-013a37e0e32c', '2026-09-17', '2026-09-17 09:35:36');
INSERT INTO `device_login_record` VALUES (221, '6689c46a-5a84-473f-b740-21d9e415519a', '51871058-4655-410e-8d90-fd3e4191e5ef', '2026-09-17', '2026-09-17 09:36:32');
INSERT INTO `device_login_record` VALUES (222, 'f41f0b70-fce7-4d44-9481-bf4006476e53', 'f40de929-ca2a-4381-a62a-c34b43ba2ae9', '2026-09-17', '2026-09-17 09:37:11');
INSERT INTO `device_login_record` VALUES (223, 'd975ff1d-bcfc-4def-96d5-add92d4393f4', 'f40de929-ca2a-4381-a62a-c34b43ba2ae9', '2026-09-17', '2026-09-17 09:37:58');
INSERT INTO `device_login_record` VALUES (224, '2ad1d3c8-ea20-4640-a9e1-200e5c4c24c1', '51871058-4655-410e-8d90-fd3e4191e5ef', '2026-09-17', '2026-09-17 09:38:00');
INSERT INTO `device_login_record` VALUES (225, '6632ab9c-aaa6-4591-a2a6-43c8d373503b', '6f3a524d-efac-492b-b80c-1fbcd1b66b94', '2026-09-17', '2026-09-17 09:39:44');
INSERT INTO `device_login_record` VALUES (226, 'bf99f031-1197-4a85-95a9-7ccf0b84e411', '51871058-4655-410e-8d90-fd3e4191e5ef', '2026-09-17', '2026-09-17 09:39:51');
INSERT INTO `device_login_record` VALUES (227, 'ea225ce5-f513-4c5b-82c3-1d0fe1c3d8a2', '51871058-4655-410e-8d90-fd3e4191e5ef', '2026-09-17', '2026-09-17 09:41:52');
INSERT INTO `device_login_record` VALUES (228, '195c3da6-58c3-4045-90a4-6ff523e22e4f', '51871058-4655-410e-8d90-fd3e4191e5ef', '2026-09-17', '2026-09-17 09:42:58');
INSERT INTO `device_login_record` VALUES (229, 'bc52f07f-ae26-4d9e-ad94-c83c6b9efab2', '51871058-4655-410e-8d90-fd3e4191e5ef', '2026-09-17', '2026-09-17 09:44:37');
INSERT INTO `device_login_record` VALUES (230, '7f6eccbd-448e-4feb-a83f-27c0c7169730', 'ad1e1079-926d-4f6f-a795-35a66292f809', '2026-09-17', '2026-09-17 09:48:41');
INSERT INTO `device_login_record` VALUES (231, 'a17e52aa-38bc-42e0-8e4d-3c46e5529b34', '51871058-4655-410e-8d90-fd3e4191e5ef', '2026-09-17', '2026-09-17 10:20:43');
INSERT INTO `device_login_record` VALUES (232, '19b3ea1f-bce2-492f-af7a-87908494d6c9', '51871058-4655-410e-8d90-fd3e4191e5ef', '2026-09-17', '2026-09-17 10:27:58');
INSERT INTO `device_login_record` VALUES (233, '95842988-1ba7-4d66-ae13-eb9c56979a16', '51871058-4655-410e-8d90-fd3e4191e5ef', '2026-09-17', '2026-09-17 10:28:50');
INSERT INTO `device_login_record` VALUES (234, '97e1ce3e-c80b-4aef-bbe4-5c6fd5266bf6', '51871058-4655-410e-8d90-fd3e4191e5ef', '2026-09-17', '2026-09-17 10:34:37');
INSERT INTO `device_login_record` VALUES (235, '89a49271-15e1-4b52-af43-fbd67acad7dd', '51871058-4655-410e-8d90-fd3e4191e5ef', '2026-09-17', '2026-09-17 10:36:58');
INSERT INTO `device_login_record` VALUES (236, '84fd3096-e868-4756-ba2c-17be32893c93', '51871058-4655-410e-8d90-fd3e4191e5ef', '2026-09-17', '2026-09-17 10:41:26');
INSERT INTO `device_login_record` VALUES (237, 'ee622b00-40ab-44a4-9b45-09c88fbd1844', 'e44a9d76-1dfd-495d-8db5-4108a40386ad', '2026-09-17', '2026-09-17 10:41:55');
INSERT INTO `device_login_record` VALUES (238, 'e3078786-d631-4cc7-a862-01005df08760', '51871058-4655-410e-8d90-fd3e4191e5ef', '2026-09-17', '2026-09-17 10:48:24');
INSERT INTO `device_login_record` VALUES (239, 'bf4f9a7d-9c6e-4815-b99c-96fef9b080cc', '51871058-4655-410e-8d90-fd3e4191e5ef', '2026-09-17', '2026-09-17 10:49:54');
INSERT INTO `device_login_record` VALUES (240, '7a9f95f8-7a43-42ac-b16f-1556cbd3ed99', '51871058-4655-410e-8d90-fd3e4191e5ef', '2026-09-17', '2026-09-17 10:53:46');
INSERT INTO `device_login_record` VALUES (241, 'ec812fa3-fa77-42b8-b389-e6029fbe1b8f', '51871058-4655-410e-8d90-fd3e4191e5ef', '2026-09-17', '2026-09-17 11:04:51');
INSERT INTO `device_login_record` VALUES (242, '160d8c13-6582-4860-94c0-d9521c12dc0f', '51871058-4655-410e-8d90-fd3e4191e5ef', '2026-09-17', '2026-09-17 11:12:07');
INSERT INTO `device_login_record` VALUES (243, 'fc3fd893-a47c-4027-8606-8e5103aa29e7', '51871058-4655-410e-8d90-fd3e4191e5ef', '2026-09-17', '2026-09-17 11:13:58');
INSERT INTO `device_login_record` VALUES (244, '2ccc0e3f-2a05-4037-87a0-9835b0e142af', '51871058-4655-410e-8d90-fd3e4191e5ef', '2026-09-17', '2026-09-17 11:15:54');
INSERT INTO `device_login_record` VALUES (245, 'a64939e7-ab7f-41bc-a80a-d0b8bf26f610', '51871058-4655-410e-8d90-fd3e4191e5ef', '2026-09-17', '2026-09-17 11:20:10');
INSERT INTO `device_login_record` VALUES (246, '137fc670-9dda-499a-829b-0075d6f3daae', '51871058-4655-410e-8d90-fd3e4191e5ef', '2026-09-17', '2026-09-17 11:22:17');
INSERT INTO `device_login_record` VALUES (247, '5c86ff4c-1f4e-4475-9405-fdb479e0d8b0', '51871058-4655-410e-8d90-fd3e4191e5ef', '2026-09-17', '2026-09-17 11:31:58');
INSERT INTO `device_login_record` VALUES (248, '31860b13-484a-46ed-a28e-bd4eaa1d5376', '1082a22c-0041-42ad-865f-013a37e0e32c', '2026-09-17', '2026-09-17 11:32:27');
INSERT INTO `device_login_record` VALUES (249, '44cc2865-33e8-4eed-a1eb-f4765a3e9953', '51871058-4655-410e-8d90-fd3e4191e5ef', '2026-09-17', '2026-09-17 11:37:22');
INSERT INTO `device_login_record` VALUES (250, 'c44ea9ac-b36f-4c3a-a25e-f7c726cda15c', '1082a22c-0041-42ad-865f-013a37e0e32c', '2026-09-17', '2026-09-17 11:41:36');
INSERT INTO `device_login_record` VALUES (251, '36e210cc-2ef2-45a2-8fc5-a1b080468442', '1082a22c-0041-42ad-865f-013a37e0e32c', '2026-09-17', '2026-09-17 11:46:22');
INSERT INTO `device_login_record` VALUES (252, '14e44057-4a52-4674-b17c-146702293ab1', '1082a22c-0041-42ad-865f-013a37e0e32c', '2026-09-17', '2026-09-17 11:57:59');
INSERT INTO `device_login_record` VALUES (253, '3104ed57-ecd4-4f95-a390-cc370cf1e53a', '1082a22c-0041-42ad-865f-013a37e0e32c', '2026-09-17', '2026-09-17 12:11:52');
INSERT INTO `device_login_record` VALUES (254, '2449ee0a-e665-43f5-b140-a8f83d1f0a68', '1082a22c-0041-42ad-865f-013a37e0e32c', '2026-09-17', '2026-09-17 12:22:09');
INSERT INTO `device_login_record` VALUES (255, '1ad76c9a-beba-462a-b6da-ac8a652bdb10', '1082a22c-0041-42ad-865f-013a37e0e32c', '2026-09-17', '2026-09-17 12:31:44');
INSERT INTO `device_login_record` VALUES (256, '1ee24e03-305c-4425-a0f5-0d2fbf2a020a', 'ae6bd056-119e-4bdb-8f48-f0edc3ee9946', '2026-09-17', '2026-09-17 13:31:29');
INSERT INTO `device_login_record` VALUES (257, 'b2b2dca9-c082-46bc-af35-895831916e6d', '45414aea-79f0-4528-a986-5d461f0016ca', '2026-09-17', '2026-09-17 13:35:02');
INSERT INTO `device_login_record` VALUES (258, 'c52a30fc-c899-43fa-b85e-dd91335dc656', 'a5bab97b-1ff0-4267-9308-c4dc61805d5c', '2026-09-17', '2026-09-17 13:35:21');
INSERT INTO `device_login_record` VALUES (259, 'c2298e76-4efa-4485-a613-159cd65cb6b0', 'e6604e57-d41d-4530-9ee5-eb8bc6944142', '2026-09-17', '2026-09-17 13:36:07');
INSERT INTO `device_login_record` VALUES (260, '2b569fe7-0dfa-443e-afed-a6033ed2aa7d', '2ae006a3-2b07-4a2a-8abc-e97bd8b2214e', '2026-09-17', '2026-09-17 13:40:33');
INSERT INTO `device_login_record` VALUES (261, 'abce002d-5379-46bd-9c86-f2e93fcef5dc', '2ae006a3-2b07-4a2a-8abc-e97bd8b2214e', '2026-09-17', '2026-09-17 13:41:27');
INSERT INTO `device_login_record` VALUES (262, 'f42c7618-73b4-4e34-b935-677a843578f2', '2ae006a3-2b07-4a2a-8abc-e97bd8b2214e', '2026-09-17', '2026-09-17 13:53:32');
INSERT INTO `device_login_record` VALUES (263, '405c1e35-8679-4c12-838a-17b7c258870a', '51871058-4655-410e-8d90-fd3e4191e5ef', '2026-09-17', '2026-09-17 13:56:46');
INSERT INTO `device_login_record` VALUES (264, '4acec8fb-32c9-4e36-8c07-c30a81445cd4', '31b2109d-c855-4c9d-873d-f15a816a2494', '2026-09-17', '2026-09-17 13:58:59');
INSERT INTO `device_login_record` VALUES (265, '342b3c67-00f7-479f-83ee-b077063497fe', 'f40de929-ca2a-4381-a62a-c34b43ba2ae9', '2026-09-17', '2026-09-17 14:01:33');
INSERT INTO `device_login_record` VALUES (266, '0b6760d1-a59d-4f97-a239-d89fea5bef69', '1082a22c-0041-42ad-865f-013a37e0e32c', '2026-09-17', '2026-09-17 14:06:28');
INSERT INTO `device_login_record` VALUES (267, '41e588bc-7714-479b-9752-98186000dcaa', '1082a22c-0041-42ad-865f-013a37e0e32c', '2026-09-17', '2026-09-17 14:10:44');
INSERT INTO `device_login_record` VALUES (268, '889a67e9-08bc-41b9-9711-4c1496c7a243', '1082a22c-0041-42ad-865f-013a37e0e32c', '2026-09-17', '2026-09-17 14:11:28');
INSERT INTO `device_login_record` VALUES (269, 'c5e02c0e-fca1-4a26-96a1-8ec2d8c8690e', '1082a22c-0041-42ad-865f-013a37e0e32c', '2026-09-17', '2026-09-17 14:16:38');
INSERT INTO `device_login_record` VALUES (270, '0347a578-e907-48cd-88ea-bed89505f360', '1082a22c-0041-42ad-865f-013a37e0e32c', '2026-09-17', '2026-09-17 14:19:03');

-- ----------------------------
-- Table structure for students
-- ----------------------------
DROP TABLE IF EXISTS `students`;
CREATE TABLE `students`  (
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '学生UUID',
  `user_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '关联用户ID',
  `student_no` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '学生学号',
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '学生姓名',
  `class_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '班级ID',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_students_user_id`(`user_id`) USING BTREE,
  UNIQUE INDEX `uk_students_student_no`(`student_no`) USING BTREE,
  INDEX `idx_students_class_id`(`class_id`) USING BTREE,
  INDEX `idx_students_name`(`name`) USING BTREE,
  CONSTRAINT `fk_student_class` FOREIGN KEY (`class_id`) REFERENCES `classes` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_student_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '学生表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of students
-- ----------------------------
INSERT INTO `students` VALUES ('03ad6187-14f2-479c-98e4-a65778edbede', '83a94444-0242-490c-9ea8-b3d6d3ddc3ab', '253201314', '宋新宇', 'abfb5cae-84d4-4aff-b893-40cd42666d18');
INSERT INTO `students` VALUES ('043ad3fe-7b96-4999-81d9-abb3bbee0b2d', 'f40de929-ca2a-4381-a62a-c34b43ba2ae9', '253201303', '刘旭', 'abfb5cae-84d4-4aff-b893-40cd42666d18');
INSERT INTO `students` VALUES ('1aedebb6-c172-4e7c-ac46-7c3d4ddb956b', '1082a22c-0041-42ad-865f-013a37e0e32c', '253201304', '冯载轩', 'abfb5cae-84d4-4aff-b893-40cd42666d18');
INSERT INTO `students` VALUES ('277aadad-a0c0-4ce1-8cb6-f826ad252538', 'e762dcf3-a434-448f-b3f4-d35a87bd5b66', '253201321', '龙子河', 'abfb5cae-84d4-4aff-b893-40cd42666d18');
INSERT INTO `students` VALUES ('323d5575-b163-4af6-a702-7634f354bb64', 'b94bfa9c-fd43-42a6-a82a-ddd39f483d78', '253201334', '王鹏宇', 'abfb5cae-84d4-4aff-b893-40cd42666d18');
INSERT INTO `students` VALUES ('32e210d2-ffe0-4c6c-a11f-787e9f86eb7c', '6c1c817f-cbd9-40a8-a26a-0a2c8adc453a', '253201342', '徐嘉嘉', 'abfb5cae-84d4-4aff-b893-40cd42666d18');
INSERT INTO `students` VALUES ('43ab2c74-6013-437d-a4ea-18bd61e0555c', '2ae006a3-2b07-4a2a-8abc-e97bd8b2214e', '253201305', '王至轩', 'abfb5cae-84d4-4aff-b893-40cd42666d18');
INSERT INTO `students` VALUES ('4fa2c113-6ba1-4387-b3d4-cf70be9e2ce1', 'ba069f7b-72df-41dd-ba4e-c4ef74977602', '253201332', '芦睿', 'abfb5cae-84d4-4aff-b893-40cd42666d18');
INSERT INTO `students` VALUES ('595af00f-652f-4780-b256-e4ab875e5b7b', '5fcc1444-d090-4660-8eef-e892f7455011', '253201322', '陈茂杰', 'abfb5cae-84d4-4aff-b893-40cd42666d18');
INSERT INTO `students` VALUES ('5a110403-6c13-4332-bd55-a876b7c814de', '0478ea5f-bba8-4f8a-994f-99dda551ddbe', '253201325', '陈羽泽', 'abfb5cae-84d4-4aff-b893-40cd42666d18');
INSERT INTO `students` VALUES ('604bd35e-15ac-45a5-b074-e4c1ff3a640a', 'a077f60a-9945-414b-a1d9-544e4b1c11a8', '253201306', '贾澎博', 'abfb5cae-84d4-4aff-b893-40cd42666d18');
INSERT INTO `students` VALUES ('63247c60-41db-4a48-817d-2028251dce81', '20c4a91a-3a17-47c5-a735-9bc6b159a499', '253201312', '肖文宇', 'abfb5cae-84d4-4aff-b893-40cd42666d18');
INSERT INTO `students` VALUES ('6d93307f-cf7b-4f71-82c0-c4ef2e45ef0b', '9be85242-989a-432a-9c4e-38596e96bb7e', '253201309', '王浩宇', 'abfb5cae-84d4-4aff-b893-40cd42666d18');
INSERT INTO `students` VALUES ('7185bac0-000b-4aec-bde1-a60b751239e6', '24f5bbe6-30cd-45d9-bf9e-e26aa46ad099', '253201323', '刘佳博', 'abfb5cae-84d4-4aff-b893-40cd42666d18');
INSERT INTO `students` VALUES ('72f4bedc-e405-41ef-83e1-370fbf6ee8e4', 'ae6bd056-119e-4bdb-8f48-f0edc3ee9946', '253201329', '张鑫睿', 'abfb5cae-84d4-4aff-b893-40cd42666d18');
INSERT INTO `students` VALUES ('79bbe579-4eac-4742-ada1-88d076b75e58', '6f3a524d-efac-492b-b80c-1fbcd1b66b94', '253201315', '石卓烁', 'abfb5cae-84d4-4aff-b893-40cd42666d18');
INSERT INTO `students` VALUES ('80465933-04d0-4aa2-b5cc-4b6bf73cff5a', 'b97d1d7f-9129-4422-9a7b-3564ab48afae', '253201320', '周语轩', 'abfb5cae-84d4-4aff-b893-40cd42666d18');
INSERT INTO `students` VALUES ('805aab46-33c1-46e2-b902-ca30607e5fac', 'e44a9d76-1dfd-495d-8db5-4108a40386ad', '253201316', '王鸿儒', 'abfb5cae-84d4-4aff-b893-40cd42666d18');
INSERT INTO `students` VALUES ('833ba07e-d3b8-49ac-a63a-d6f78f3160ec', '8294e534-234f-4b17-b7ff-14b6eaece39d', '253201335', '康济恩', 'abfb5cae-84d4-4aff-b893-40cd42666d18');
INSERT INTO `students` VALUES ('87922d2d-600c-4a17-ac2e-50a1f5dd217c', '4692df2c-3fe9-4e36-be1d-c4f85c4b5beb', '253201337', '雷俊颖', 'abfb5cae-84d4-4aff-b893-40cd42666d18');
INSERT INTO `students` VALUES ('880cbd99-d6a7-4f33-85d0-c1f871f365f1', '5ef0b5a2-549f-4e46-a0bf-0d582a725df5', '253201313', '赵亦寒', 'abfb5cae-84d4-4aff-b893-40cd42666d18');
INSERT INTO `students` VALUES ('88f956e7-5584-4ab9-9400-f9c3f8630a1e', '51871058-4655-410e-8d90-fd3e4191e5ef', '253201336', '施思年', 'abfb5cae-84d4-4aff-b893-40cd42666d18');
INSERT INTO `students` VALUES ('9a0838ed-ee1b-4644-b39a-67db34bc8e2d', 'ccfc2a08-b412-4c2a-a52a-42f460bf6e9e', '253201341', '李晔霞', 'abfb5cae-84d4-4aff-b893-40cd42666d18');
INSERT INTO `students` VALUES ('a0cec1ce-5644-46ad-9870-6fa77fde7ffe', 'd164ecc2-5d9b-44a1-bb98-84080d926a93', '253201333', '李宗岳', 'abfb5cae-84d4-4aff-b893-40cd42666d18');
INSERT INTO `students` VALUES ('a18e8e26-8752-4c9e-b6fb-a25457eca40a', '5a50a366-ac19-4605-8b49-f8b426ae213b', '253201311', '高政煜', 'abfb5cae-84d4-4aff-b893-40cd42666d18');
INSERT INTO `students` VALUES ('ad72f7e1-4742-44a3-86c9-6d9e3c41cdf9', '5cd0cc45-8067-4958-9317-362125413388', '253201301', '吕嘉兴', 'abfb5cae-84d4-4aff-b893-40cd42666d18');
INSERT INTO `students` VALUES ('ade1ab22-f524-4292-bef4-712f162c6ca4', 'ad1e1079-926d-4f6f-a795-35a66292f809', '253201338', '库锦芸', 'abfb5cae-84d4-4aff-b893-40cd42666d18');
INSERT INTO `students` VALUES ('b4170bdf-3fa6-40aa-8711-045e5b7dda0c', '31b2109d-c855-4c9d-873d-f15a816a2494', '253201302', '杨承瑞', 'abfb5cae-84d4-4aff-b893-40cd42666d18');
INSERT INTO `students` VALUES ('b9ffafa9-c0af-4bd4-acb5-a5f9d9ba84ca', '9bf8006a-085f-431f-9620-a10c41156e94', '253201339', '高璟怡', 'abfb5cae-84d4-4aff-b893-40cd42666d18');
INSERT INTO `students` VALUES ('be6f193a-af0e-4165-ad33-3d999b5f6dad', '815e10bc-356f-4763-945f-1070a2103200', '253201326', '王思源', 'abfb5cae-84d4-4aff-b893-40cd42666d18');
INSERT INTO `students` VALUES ('c26f6c2f-7c8f-4791-864a-341ed6e7d8d1', '7bfb5f43-8087-4902-b942-1d6fbb715be8', '253201340', '田嘉慧', 'abfb5cae-84d4-4aff-b893-40cd42666d18');
INSERT INTO `students` VALUES ('c5bb83cc-c8af-4fe6-a782-220676b6af08', 'e1fc93fc-ed05-4b9c-96b4-547d36bc2e04', '253201310', '闫霄同', 'abfb5cae-84d4-4aff-b893-40cd42666d18');
INSERT INTO `students` VALUES ('d4c430f1-f17e-4a9c-bb14-38b0dedc3620', '45414aea-79f0-4528-a986-5d461f0016ca', '253201308', '张铠鹏', 'abfb5cae-84d4-4aff-b893-40cd42666d18');
INSERT INTO `students` VALUES ('d53a5de6-fe03-4d94-9a03-bd0657d3d16c', 'e6604e57-d41d-4530-9ee5-eb8bc6944142', '253201328', '刘敬坤', 'abfb5cae-84d4-4aff-b893-40cd42666d18');
INSERT INTO `students` VALUES ('d9c1c663-0678-4018-8952-61c8d10c8c8b', 'ce886dc1-1396-48c7-9ea2-08adf25387e4', '253201324', '姬罡', 'abfb5cae-84d4-4aff-b893-40cd42666d18');
INSERT INTO `students` VALUES ('dc65aa73-09d5-44a6-8e6a-28a8c7ccf3cc', 'a5bab97b-1ff0-4267-9308-c4dc61805d5c', '253201317', '张迦恩', 'abfb5cae-84d4-4aff-b893-40cd42666d18');
INSERT INTO `students` VALUES ('ea5b11f1-54eb-43c5-bb2b-1522b11b39b7', 'e12a7eae-da99-4f44-a0c7-70a6a2c535f2', '253201318', '刘家烨', 'abfb5cae-84d4-4aff-b893-40cd42666d18');
INSERT INTO `students` VALUES ('ea8c876a-6da1-491c-9b0f-4e3fdbcaae85', 'be5eb500-e58d-4465-8eb0-d869bfe3ad17', '253201327', '邓天成', 'abfb5cae-84d4-4aff-b893-40cd42666d18');
INSERT INTO `students` VALUES ('f1745c3f-3ceb-49bd-9caa-47f7314178cb', 'da73a81f-1b9f-4eda-8d37-e0edbbcd1c95', '253201319', '刘镕赫', 'abfb5cae-84d4-4aff-b893-40cd42666d18');
INSERT INTO `students` VALUES ('f3553273-5866-4936-b3d5-e21c8f950c21', '8a1fc1c1-4f35-45df-931b-d62dbd376f19', '253201331', '张天烁', 'abfb5cae-84d4-4aff-b893-40cd42666d18');
INSERT INTO `students` VALUES ('f4200def-d5d1-4acf-96d3-13a9e2e8e1cf', '04fd5084-7d3e-4f5a-8f02-b80c356e9ea7', '253201330', '李武斌', 'abfb5cae-84d4-4aff-b893-40cd42666d18');
INSERT INTO `students` VALUES ('fc9cf5b8-6c70-40ce-af3f-95dc5e747d77', 'ecd3b094-d6e7-49cb-bd7a-4700091a5276', '253201307', '张浩然', 'abfb5cae-84d4-4aff-b893-40cd42666d18');

-- ----------------------------
-- Table structure for teachers
-- ----------------------------
DROP TABLE IF EXISTS `teachers`;
CREATE TABLE `teachers`  (
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '教师UUID',
  `user_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '关联用户ID',
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '教师姓名',
  `department` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '所属院系',
  `class_id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '所属班级ID',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_teachers_user_id`(`user_id`) USING BTREE,
  INDEX `idx_teachers_name`(`name`) USING BTREE,
  INDEX `idx_teachers_class_id`(`class_id`) USING BTREE,
  CONSTRAINT `fk_teacher_class` FOREIGN KEY (`class_id`) REFERENCES `classes` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_teacher_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '教师表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of teachers
-- ----------------------------
INSERT INTO `teachers` VALUES ('f9cc3f0b-4dee-4ba3-81da-982c8dd41642', '0b9c3572-a450-45c8-b858-df9c9b67d299', '刘老师', '人工智能学院', 'abfb5cae-84d4-4aff-b893-40cd42666d18');

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户UUID',
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户名',
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Werkzeug密码哈希',
  `role` tinyint(0) NOT NULL COMMENT '角色 1学生 2教师 3管理员',
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '手机号',
  `status` tinyint(0) NOT NULL DEFAULT 1 COMMENT '账号状态 1正常 0禁用',
  `create_time` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0) COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_users_username`(`username`) USING BTREE,
  INDEX `idx_users_role`(`role`) USING BTREE,
  INDEX `idx_users_status`(`status`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '用户表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO `users` VALUES ('0478ea5f-bba8-4f8a-994f-99dda551ddbe', '253201325', 'scrypt:32768:8:1$WDiDw3dUcjlGQrjV$9df13768891b284110ac26a8dd848ee22ba721e1abe9acbf3b74995ddd6e9db6e8f94479bfb909e95949fc90543a86cff6b292b364bc8429dbbdfce11d1c1751', 1, NULL, 1, '2026-09-15 08:51:00');
INSERT INTO `users` VALUES ('04fd5084-7d3e-4f5a-8f02-b80c356e9ea7', '253201330', 'scrypt:32768:8:1$QTGh34Zz06Gfm0GV$6a9c6ffa170012218b8bb8d6767c2fa9cf291faa74c29cc736c7b8c534dc0ab69325c810ce3a881e4e2a116aa340c4e07402bc31014c7d6f71377fd243d1297c', 1, NULL, 1, '2026-09-15 08:51:02');
INSERT INTO `users` VALUES ('0b9c3572-a450-45c8-b858-df9c9b67d299', 'tea', 'scrypt:32768:8:1$5NoPcZNy5OV32UNf$3c02828555926dc8a025fd4f06f9c350fe14e3415e6b9e8d117eec51735704af829622dfb576e2b4a651f02044a4bdaa4efb831904f878c27f0d6c45deac48f2', 2, NULL, 1, '2026-09-15 08:55:46');
INSERT INTO `users` VALUES ('10000000-0000-0000-0000-000000000001', 'admin', 'scrypt:32768:8:1$yzvEzbvzexg3DG1L$c67ea9a91087e38a4d205dcdc154e190539e7cdac9dfb9b605525bbc7ccc48e5dbe927da7a8126aa656ca2b02536676789e14d165ddf75e577baa02a1a4b635f', 3, '13800000001', 1, '2026-09-15 08:37:02');
INSERT INTO `users` VALUES ('1082a22c-0041-42ad-865f-013a37e0e32c', '253201304', 'scrypt:32768:8:1$ca1MByW8NLDoGlGa$8ea09a7fb5829f5e1ca3b9640c0845452454414ac6bd44df5eb137a961cf159adb4f0186eb197e1f2a87dfeacda0a325b60a4dd1878f58083e98a0d6523833bc', 1, NULL, 1, '2026-09-15 08:50:49');
INSERT INTO `users` VALUES ('20c4a91a-3a17-47c5-a735-9bc6b159a499', '253201312', 'scrypt:32768:8:1$wy7zSpQVqCyVDcTl$ad7b17c0c881b5a59b1d7e6125a6edfd45ea40f022c2499bbb7a08b9ddae40c28f90cf0d11fb3f7675677918c5d5de4b1176cf244ba16ce2e808594c90682ad4', 1, NULL, 1, '2026-09-15 08:50:52');
INSERT INTO `users` VALUES ('24f5bbe6-30cd-45d9-bf9e-e26aa46ad099', '253201323', 'scrypt:32768:8:1$Qdown4YR88JjxCfb$9e895b61175700defb6b576891d72aefc541030d2d623d1cd2ca3dd5c82584e25e92baa9e2e18c33d919d58bcd377313cf3cc56a1da8027235fca6f081aa5648', 1, NULL, 1, '2026-09-15 08:50:58');
INSERT INTO `users` VALUES ('2ae006a3-2b07-4a2a-8abc-e97bd8b2214e', '253201305', 'scrypt:32768:8:1$hbTLGZSepkR7VVM3$2148b52c10108ed56cbba62112fb702a38d97c0f6094210b82b0130b804fe156a35a9455dc3b729e5034a6433dad736999b78929a0dbae8a1c6ed1baff0427d1', 1, NULL, 1, '2026-09-15 08:50:49');
INSERT INTO `users` VALUES ('31b2109d-c855-4c9d-873d-f15a816a2494', '253201302', 'scrypt:32768:8:1$f0bVNubRtHql9qC8$0503a435694effa01252322ea3ff0640a29b8b3919129930e8bc93a5b3e7e39cdf8855049e2d74b924c6b5e0cd4da7fd6bc7f2a97c29809e8a71bd6c23735596', 1, NULL, 1, '2026-09-15 08:50:47');
INSERT INTO `users` VALUES ('45414aea-79f0-4528-a986-5d461f0016ca', '253201308', 'scrypt:32768:8:1$nCBBXr8zhIhcoUnK$3df85d469b698a4d68db54fe850c11090bd601727438fc812041852c73a138c16900335173a6cd4fea2bb8411b7e70ec913fb1efd173f40609621554a4dbc60f', 1, NULL, 1, '2026-09-15 08:50:51');
INSERT INTO `users` VALUES ('4692df2c-3fe9-4e36-be1d-c4f85c4b5beb', '253201337', 'scrypt:32768:8:1$qRbUkUEJjScNjLdV$549485d4a06173eea2aeb12f2b15cd590543de3929852d4101dbea8782ae033418bb4ae3a99d113ff5631a2f859dfbca2dd86c8634fa68a1bc04cf8df93e024d', 1, NULL, 1, '2026-09-15 08:51:06');
INSERT INTO `users` VALUES ('51871058-4655-410e-8d90-fd3e4191e5ef', '253201336', 'scrypt:32768:8:1$BYwhIcn7oGodINRb$7ea28224faf13997b3acb8de61e4b0ea4591d3e2b212915313bc64be20e2788be9b87c023cfefa246d0f84e0bfeaf16ed9ea8cebe7d953e512f3c970361750b3', 1, NULL, 1, '2026-09-15 08:51:06');
INSERT INTO `users` VALUES ('5a50a366-ac19-4605-8b49-f8b426ae213b', '253201311', 'scrypt:32768:8:1$yyWv1GZM7PAnGT6B$6e1b90bcd8c3cdf538578c7917c99751110e19a92ff0a3e0466366922ff3dff5def9b6e67a082097c2446fca6d7109c1a1d6ac69be422aad70a691c29713be01', 1, NULL, 1, '2026-09-15 08:50:52');
INSERT INTO `users` VALUES ('5cd0cc45-8067-4958-9317-362125413388', '253201301', 'scrypt:32768:8:1$DfoNtPQcLyBMcL6B$22be0c5ef793e0535f191f4611002896de1a3862ef641fa43c070681e454e1f9ac47fe16dff8a86928a6e8c8f3fa4b5d6f260bb6b92d48c22c81fde91713bb80', 1, NULL, 1, '2026-09-15 08:50:46');
INSERT INTO `users` VALUES ('5ef0b5a2-549f-4e46-a0bf-0d582a725df5', '253201313', 'scrypt:32768:8:1$WomgvJP46bdcpj65$3e0e92ed3218e9fdb3d1395d8d5711e2388c119804255009db10a6437e73e4f77fffd924e947ad18bc425550ca40d8e9a941c7ce76dbc0eebedb95251cc029d8', 1, NULL, 1, '2026-09-15 08:50:53');
INSERT INTO `users` VALUES ('5fcc1444-d090-4660-8eef-e892f7455011', '253201322', 'scrypt:32768:8:1$URgkuiScUiqvRnmH$31083952a3aea628b8ec157a4e63f861bcf4bbf78f779914362c9c72cccaddd54b259bea1b494db4729a0a83df2b9ce232a7ccab6abf9fdccc5a3cdab900028c', 1, NULL, 1, '2026-09-15 08:50:58');
INSERT INTO `users` VALUES ('6c1c817f-cbd9-40a8-a26a-0a2c8adc453a', '253201342', 'scrypt:32768:8:1$cAO9QzfjOG1Ile7v$6cc21f15dffaf282dd7431dcb47bdbedbe7d45b192b88c1d089c98ea32c556c91cf420fd6fa5dfc233da61332a607770dd256341b5ee662b12ac696a114e68c7', 1, NULL, 1, '2026-09-15 08:51:10');
INSERT INTO `users` VALUES ('6f3a524d-efac-492b-b80c-1fbcd1b66b94', '253201315', 'scrypt:32768:8:1$mXtYPtESZLv3yRt8$8dee8da7bb9cf750b9d695d847311622f7dea47fcbe884c352038f30e7b460914da3ee141b9184824a0db3aa680ecace4b0078e144a24e9e7832413b6439a448', 1, NULL, 1, '2026-09-15 08:50:53');
INSERT INTO `users` VALUES ('7bfb5f43-8087-4902-b942-1d6fbb715be8', '253201340', 'scrypt:32768:8:1$mLFHFMFWpmTLhP2S$33b7e9b88337c57b31abb198ef67cb2bec653f490152851fbdbc1e7ef81cdb5f91037ec6792c0e62fb386252842380aef176b79b9319340496dbc1422054dc00', 1, NULL, 1, '2026-09-15 08:51:08');
INSERT INTO `users` VALUES ('815e10bc-356f-4763-945f-1070a2103200', '253201326', 'scrypt:32768:8:1$fgIneJaXEvSSgwPW$0bff03cf32878990340c36cfb4b7462a12dbcc5719847ea2629e0ee8c9a7ecf17e1c97330bf7c5fde80307fd705de8f5f3312f5d0af435178c8d652f0ef0adc1', 1, NULL, 1, '2026-09-15 08:51:00');
INSERT INTO `users` VALUES ('8294e534-234f-4b17-b7ff-14b6eaece39d', '253201335', 'scrypt:32768:8:1$iHRMW8KKO7xrROPq$bbeb63cb9ffb3a7cfbfda2b58c3e0cb9ada582fb29fe651fbf297e425a15dda46e82a0334e346075de15e2f4630b60e1872b8054a6db1f611f09350ddf22d478', 1, NULL, 1, '2026-09-15 08:51:05');
INSERT INTO `users` VALUES ('83a94444-0242-490c-9ea8-b3d6d3ddc3ab', '253201314', 'scrypt:32768:8:1$yVOoibdWKltGcL28$06dd12fdb53c088ec4bc5f6f7b0aab75363c7d939e68accf89671977684eede96ff9ef9fb789de612ebaad2f70d5047f21b604249c79019cbc94d9efeb7a170b', 1, NULL, 1, '2026-09-15 08:50:53');
INSERT INTO `users` VALUES ('8a1fc1c1-4f35-45df-931b-d62dbd376f19', '253201331', 'scrypt:32768:8:1$4ycoKpHsb4LDVTed$f759949b9f59ded2e6712cc8bbb2463af24d847d2f76b43679a983096a12bb13c70d449034a2d7ed41094f54f9ed282a66235e8418ac5a348723382fbc8c0466', 1, NULL, 1, '2026-09-15 08:51:03');
INSERT INTO `users` VALUES ('9be85242-989a-432a-9c4e-38596e96bb7e', '253201309', 'scrypt:32768:8:1$IZ0BaO5ame5MKA33$26c674fbadec5e3da881263df7a497dbee78c290c90553815a2c5104a52caac8e29b122399361b184a067c6249c67448bb12c305406781b79432f2dc89de1acf', 1, NULL, 1, '2026-09-15 08:50:51');
INSERT INTO `users` VALUES ('9bf8006a-085f-431f-9620-a10c41156e94', '253201339', 'scrypt:32768:8:1$o2rkfDSZSbLzeLCS$919c46eb2cdb9c1d6a92893d700ff0416954fd0343a4dcd5e15d361481e7a1aac0cfaf9a7ad1e0a076b0bcb77dee87df5bcfa3503a8cd9a1539a03696860bb72', 1, NULL, 1, '2026-09-15 08:51:08');
INSERT INTO `users` VALUES ('a077f60a-9945-414b-a1d9-544e4b1c11a8', '253201306', 'scrypt:32768:8:1$jBYdwjmM33TzW3iC$2a73bd9da7fbde0b5678c74eb64bd56e4d1b3823b4f4282c9137aef3876f42bce99bb716fc32d455db0f8676315409f87485430c9cd0994b15aacb14abcef0a9', 1, NULL, 1, '2026-09-15 08:50:50');
INSERT INTO `users` VALUES ('a5bab97b-1ff0-4267-9308-c4dc61805d5c', '253201317', 'scrypt:32768:8:1$dYyFCDf2hiajjgHG$1192a042263f122e5b7bc8f52693ef9e5bf8a72fbfae3b159ae9ff35ee610ae41c7096a123f91ab5ee2ff4c3650a67d10ba752a728c90253c6cac1d584dcee19', 1, NULL, 1, '2026-09-15 08:50:54');
INSERT INTO `users` VALUES ('ad1e1079-926d-4f6f-a795-35a66292f809', '253201338', 'scrypt:32768:8:1$4ASDaXF3Vtfyzqo5$33665b8c3a9f9ae7130bc1ddf0fcff82ad4fbeb072f4844a9b38520bb6da1fd19c4a2431cbd5982f26b0c74d194a3ca3a3c23be010d613a8a2d07eb15bc510b9', 1, NULL, 1, '2026-09-15 08:51:07');
INSERT INTO `users` VALUES ('ae6bd056-119e-4bdb-8f48-f0edc3ee9946', '253201329', 'scrypt:32768:8:1$Xn42xTT3B3oVCr92$b9d79415ce79240a9a85cdd7fed4d4c70b7f44d374cee87f55a8a91c9a5c9898a4a1ad6a83eba493ae0a75ed31de0c6ff2acd6edd103661f7088a69985f1f5a4', 1, NULL, 1, '2026-09-15 08:51:02');
INSERT INTO `users` VALUES ('b94bfa9c-fd43-42a6-a82a-ddd39f483d78', '253201334', 'scrypt:32768:8:1$tO8br0vza93KoJyR$8c833907c4a3d458a72bc47b3e123f2c319dd31d609665ebbcade8fe6b0421f62dfb287408bbcb95e94ad3a58e612c4f2b4ed2b42e447a297054da74003472d3', 1, NULL, 1, '2026-09-15 08:51:04');
INSERT INTO `users` VALUES ('b97d1d7f-9129-4422-9a7b-3564ab48afae', '253201320', 'scrypt:32768:8:1$bo0jyZfkuTiRJjx0$89e60dddf666da1318cab712f684bb3ab4338275590ae7bd20706da60534dcc1bce3a2aad937917b3510c30cb761b82aaba55364244da21a69bf37af1cd4d4db', 1, NULL, 1, '2026-09-15 08:50:56');
INSERT INTO `users` VALUES ('ba069f7b-72df-41dd-ba4e-c4ef74977602', '253201332', 'scrypt:32768:8:1$MEPkOzs8CgGQGSRz$461cd6a9a48c018c972ebd80a9bb9274c872ab1a40ed0aae3b3cd696d9cc2b0255e5c59af1802445bbfb88b01ae633b2160c592736d6010823ed372c15f7d3e8', 1, NULL, 1, '2026-09-15 08:51:03');
INSERT INTO `users` VALUES ('be5eb500-e58d-4465-8eb0-d869bfe3ad17', '253201327', 'scrypt:32768:8:1$u0J83OVH1dkuXsh0$2ae121c0193c170448741406c4fc329a7b36df65c0e50cb4b79fb732111538df0bdd9fc472a58eed385051ef88094882178484c8ebda30c7f016eaa2612818cb', 1, NULL, 1, '2026-09-15 08:51:01');
INSERT INTO `users` VALUES ('ccfc2a08-b412-4c2a-a52a-42f460bf6e9e', '253201341', 'scrypt:32768:8:1$yzvEzbvzexg3DG1L$c67ea9a91087e38a4d205dcdc154e190539e7cdac9dfb9b605525bbc7ccc48e5dbe927da7a8126aa656ca2b02536676789e14d165ddf75e577baa02a1a4b635f', 1, NULL, 1, '2026-09-15 08:51:09');
INSERT INTO `users` VALUES ('ce886dc1-1396-48c7-9ea2-08adf25387e4', '253201324', 'scrypt:32768:8:1$E9h1FN6q9vSvOtna$ccc4f3a04671e7c803a3d96b320b7dd5b900c54be16558b6d11d75b71b5d0a811815c8a138cc488e98069724e2bb501c51075cee38d67f23145380d27941f6f2', 1, NULL, 1, '2026-09-15 08:50:59');
INSERT INTO `users` VALUES ('d164ecc2-5d9b-44a1-bb98-84080d926a93', '253201333', 'scrypt:32768:8:1$IvusLAyugCC3bx3q$a4d5be78aa0c1a7c4735370057248ce2b63544959da970565611105e365817cb462e7024cc1c06990c3e9501e6b2766a4485e02d615366e987cf7b6eac93b998', 1, NULL, 1, '2026-09-15 08:51:04');
INSERT INTO `users` VALUES ('da73a81f-1b9f-4eda-8d37-e0edbbcd1c95', '253201319', 'scrypt:32768:8:1$71TGd3T0o7QP0d46$69fe86ce4554db33b5e11f0b3c90b209ae1c86d5ca77b346ccef6d08768a5da3f8e05a40c0526b2401e54dc9fd66d6672c57ab2eb63b5783fd86295522cfd819', 1, NULL, 1, '2026-09-15 08:50:56');
INSERT INTO `users` VALUES ('e12a7eae-da99-4f44-a0c7-70a6a2c535f2', '253201318', 'scrypt:32768:8:1$CPQKvbJe9Ii6gI5h$8d6e856d3becac56ecf8a14679471e52f37ddc015755f23e743f53e766263197db128fb8fb96a5923434b70ba010533f1c9ec5e495ab34549821dceaf1411d67', 1, NULL, 1, '2026-09-15 08:50:55');
INSERT INTO `users` VALUES ('e1fc93fc-ed05-4b9c-96b4-547d36bc2e04', '253201310', 'scrypt:32768:8:1$MFhVZuTVDmlbcnCm$e9e45c4def0aebe01e80868bc8ee6ce91a4ff61268be7ca2969eeb1fe47f910e90321ea2a28ef7b10843a67601840bce55d317d31f56beab198ef240b2ccbc6a', 1, NULL, 1, '2026-09-15 08:50:51');
INSERT INTO `users` VALUES ('e44a9d76-1dfd-495d-8db5-4108a40386ad', '253201316', 'scrypt:32768:8:1$j8nWZ9QmzpcuXXNZ$560428348292c6d1b20fa2098714ee662a19622d8408c9033e557791893cf4016f3d0cf6204d241c164436e884830ea16819a6a29382110818fb1b2bf5a28c7e', 1, NULL, 1, '2026-09-15 08:50:54');
INSERT INTO `users` VALUES ('e6604e57-d41d-4530-9ee5-eb8bc6944142', '253201328', 'scrypt:32768:8:1$MR9nZKT51h73AVfp$4004ecda3f165bf28733d7a313e188686d9585cd0e8f17e1370b07c5bf67114606ff90812ef574c11e5891ed5691280b7c621162a6dcb2c236d3d010b13bba9b', 1, NULL, 1, '2026-09-15 08:51:01');
INSERT INTO `users` VALUES ('e762dcf3-a434-448f-b3f4-d35a87bd5b66', '253201321', 'scrypt:32768:8:1$MKJT1Tt4QKuWC5Cj$472aaaa0ffe0f63ad8bd661be1b0daa8b4a7a599f04d1e6eaf7beda77f27a232f52b56554d20a4e3ce3516be44a896ff4f926125681ffd227065a5e3a2afae6b', 1, NULL, 1, '2026-09-15 08:50:57');
INSERT INTO `users` VALUES ('ecd3b094-d6e7-49cb-bd7a-4700091a5276', '253201307', 'scrypt:32768:8:1$7VjjgcfmhG6vOVa9$398378e6f3281b6d1c4fff52b5740cb95dde460585b91987b059d7ee2865de85cd4ee160444e3533f0f8ec8a4dc8f80b0d9e9538d5f32b2870a9db7d59a167ca', 1, NULL, 1, '2026-09-15 08:50:50');
INSERT INTO `users` VALUES ('f40de929-ca2a-4381-a62a-c34b43ba2ae9', '253201303', 'scrypt:32768:8:1$WyFszSmHaroPkgVK$64b813b30b34a5e4c6fcbe91a05a5f07c6e7b0b163dd8e8229a76f4b10b4ab44b652f067340f6b90e21190fdfa9d973bbd037e5540a930308c8036532b64bcce', 1, NULL, 1, '2026-09-15 08:50:48');

SET FOREIGN_KEY_CHECKS = 1;
