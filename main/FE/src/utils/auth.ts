/**
 * 本地登录态校验小工具
 *
 * 学生端 / 教师端 / 管理端在挂载时都会先读 localStorage 里的 user 和
 * access_token，再决定要不要请求后端。原先三处各写一份，而且都只看
 * 「有没有」，不看「能不能用」：
 *
 *   - 本地没有登录态
 *   - 令牌已过期 / 格式不对
 *
 * 这两种情况下页面照样会发出一批受保护接口请求，全部 401（后端日志噪音，
 * 也会抬高同 IP 的爬虫计数）。这里统一提供「先校验、不通过就不请求接口」
 * 的判断：调用方拿到 null 就直接跳登录页并结束，不要再发请求。
 */

/** 清掉本地登录态 */
export function clearSession() {
  localStorage.removeItem("user")
  localStorage.removeItem("access_token")
}

/**
 * 解析 JWT 的 payload
 *
 * 只做 base64 解码，不验签：验签是后端的事，这里的目的只是本地快速判断
 * 令牌能不能用（是否已过期），避免明知会被拒还照样去请求接口。
 */
function decodePayload(token: string): Record<string, any> | null {
  try {
    const parts = token.split(".")
    if (parts.length !== 3) return null

    // base64url → base64，并补回 padding
    let b64 = parts[1].replace(/-/g, "+").replace(/_/g, "/")
    const pad = b64.length % 4
    if (pad) b64 += "=".repeat(4 - pad)

    const bytes = Uint8Array.from(atob(b64), (c) => c.charCodeAt(0))
    const payload = JSON.parse(new TextDecoder().decode(bytes))

    return payload && typeof payload === "object" ? payload : null
  } catch {
    return null
  }
}

/**
 * 读取并校验本地登录态
 *
 * 返回缓存的 user 对象（含 role）表示登录态可用；
 * 返回 null 表示不可用，此时本地缓存已经被清掉，调用方应跳登录页，
 * 并且不要再请求任何受保护接口。
 */
export function readSession(): Record<string, any> | null {
  const userCache = localStorage.getItem("user")
  const tokenCache = localStorage.getItem("access_token")

  if (!userCache || !tokenCache) {
    clearSession()
    return null
  }

  const payload = decodePayload(tokenCache)
  if (!payload) {
    clearSession()
    return null
  }

  const exp = payload.exp
  if (typeof exp === "number" && exp * 1000 <= Date.now()) {
    clearSession()
    return null
  }

  try {
    const user = JSON.parse(userCache)
    if (!user || typeof user !== "object") {
      clearSession()
      return null
    }
    return user
  } catch {
    clearSession()
    return null
  }
}
