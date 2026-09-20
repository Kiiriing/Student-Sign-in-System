// 生成 UUID 的兼容实现
// crypto.randomUUID 仅在安全上下文（HTTPS 或 localhost）中可用
// 通过局域网 IP 访问 HTTP 时不可用，需要回退方案
function generateUUID(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID()
  }
  // 回退：使用 Math.random 生成 RFC4122 v4 UUID
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0
    const v = c === "x" ? r : (r & 0x3) | 0x8
    return v.toString(16)
  })
}

export function getDeviceId(): string {
  let deviceId = localStorage.getItem("device_id")

  if (!deviceId) {
    deviceId = generateUUID()
    localStorage.setItem("device_id", deviceId)
  }

  return deviceId
}
