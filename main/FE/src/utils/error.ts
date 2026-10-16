/**
 * 请求错误处理小工具
 *
 * 学生端 / 教师端 / 管理端三个 view 原先各自复制了一份完全相同的
 * errorMessage / isAuthError（逐字一致），这里统一维护一份，
 * 避免以后改错误提示或鉴权判断时漏改其中一处。
 */

/** 后端统一返回 { code, message }，优先取 message，取不到时回落到 fallback */
export function errorMessage(error: unknown, fallback: string): string {
  const err = error as { response?: { data?: { message?: string } } }
  return err?.response?.data?.message || fallback
}

/** 401 / 403 视为登录态失效，需要跳回登录页 */
export function isAuthError(error: unknown): boolean {
  const status = (error as { response?: { status?: number } })?.response?.status
  return status === 401 || status === 403
}
