/**
 * 考勤状态 → 徽标样式映射
 *
 * 学生端 StudentDashboard.vue 与教师端 teacherDashboard.vue 原先各自复制了
 * 一份完全相同的 1~7 状态映射（两处代码逐字一致），这里统一维护一份，
 * 避免以后改样式时漏改其中一处。
 *
 * 状态码含义：
 *   1 正常 / 2 迟到 / 3 旷课 / 4 早退 / 5 病假 / 6 事假 / 7 未签到
 */

const ATTENDANCE_BADGE_CLASS: Record<number, string> = {
  1: "badge-ok",
  2: "badge-warn",
  3: "badge-danger",
  4: "badge-purple",
  5: "badge-cyan",
  6: "badge-gray",
  7: "badge-unsigned"
}

/** 考勤状态码 → 徽标 class；未知状态统一回落到 badge-off */
export function attendanceStatusBadgeClass(status: number): string {
  return ATTENDANCE_BADGE_CLASS[status] || "badge-off"
}
