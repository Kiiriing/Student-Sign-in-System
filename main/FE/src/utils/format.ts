/**
 * 时间显示格式化
 *
 * 管理端 formatTime 与教师端 fmtDateTime 原先各自复制了一份完全相同的实现
 * （逐字一致），这里统一维护一份。
 *
 * 约定：空值显示 "-"；无法解析的字符串原样返回，避免把脏数据显示成 Invalid Date。
 */

export function formatDateTime(value?: string | null): string {
  if (!value) return "-"
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  const pad = (n: number) => String(n).padStart(2, "0")
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`
}
