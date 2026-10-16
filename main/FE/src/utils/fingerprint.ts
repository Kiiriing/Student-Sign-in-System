// 浏览器自动化指纹检测工具
//
// 用于识别 selenium / puppeteer / playwright / phantomjs 等
// 自动化工具操控的浏览器。命中任意一条即视为可疑。
//
// 检测维度（仅保留 HTTP 层无法伪造、且不会对真人浏览器误报的特征）：
//   1. navigator.webdriver === true           selenium/puppeteer 默认不隐藏
//   4. navigator.languages 为空                真浏览器至少有 1 个
//   5. document 上 cdc_ 开头的变量              chromedriver 注入痕迹
//   6. WebGL renderer 为 SwiftShader/Mesa       headless chrome 特征
//   7. Notification 与 permissions API 状态矛盾 headless chrome 特征
//
// 已移除的不可靠检测项（会在真人浏览器上误报）：
//   ✗ window.chrome.runtime 缺失：普通网页本来就没有 chrome.runtime
//     （只有 chrome-extension:// 上下文才有）
//   ✗ navigator.plugins.length === 0：Chrome 91+ 隐私保护可能返回空
//   ✗ window.outerWidth/outerHeight === 0：浏览器最小化时可能为 0
//
// 用法：
//   import { collectBrowserFingerprint } from "@/utils/fingerprint"
//   const fp = await collectBrowserFingerprint()
//   if (fp) {
//     // fp 非空 = 命中了自动化特征，发给后端做记录
//     await request.post("/api/student/signin", { ..., client_fp: fp })
//   }

interface FpHit {
  key: string
  detail: string
}

/**
 * 收集浏览器自动化指纹
 *
 * 返回值：
 *   "" 空字符串：未命中任何特征（正常浏览器）
 *   "key1,key2,..."：命中的特征 key 列表（不含隐私详情）
 *
 * 不返回详细数据（如具体 webgl vendor、具体 cdc 变量名），
 * 一方面避免泄露浏览器隐私，另一方面后端只需要"命中了哪类特征"。
 */
export async function collectBrowserFingerprint(): Promise<string> {
  const hits: FpHit[] = []

  // 1. navigator.webdriver
  // selenium 默认 true；puppeteer / playwright 在未显式 hide 时也常为 true
  // 这是 HTTP 层无法伪造的检测维度，最可靠
  try {
    if (navigator.webdriver === true) {
      hits.push({ key: "webdriver", detail: "navigator.webdriver=true" })
    }
  } catch {
    /* ignore */
  }

  // 2. navigator.languages 为空
  // 真浏览器至少有 1 个语言；headless chrome 可能返回空数组
  try {
    if (!navigator.languages || navigator.languages.length === 0) {
      hits.push({ key: "no-languages", detail: "navigator.languages empty" })
    }
  } catch {
    /* ignore */
  }

  // 3. document 上 cdc_ 开头的变量（chromedriver 注入痕迹）
  // 真浏览器不会有；chromedriver 启动 Chrome 时会注入 cdc_ 前缀的辅助变量
  try {
    const cdcKeys = Object.keys(document).filter(k => k.startsWith("cdc_"))
    if (cdcKeys.length > 0) {
      hits.push({ key: "cdc-keys", detail: `cdc_ vars: ${cdcKeys.join(",")}` })
    }
  } catch {
    /* ignore */
  }

  // 4. WebGL vendor/renderer 异常
  // headless chrome 的 renderer 常为 "SwiftShader" / "Mesa" / "Google SwiftShader"
  // 真浏览器 renderer 一般是 Intel/AMD/NVIDIA 显卡型号
  try {
    const canvas = document.createElement("canvas")
    const gl = (canvas.getContext("webgl") ||
      canvas.getContext("experimental-webgl")) as WebGLRenderingContext | null
    if (gl) {
      const debugInfo = gl.getExtension("WEBGL_debug_renderer_info")
      if (debugInfo) {
        const renderer = String(gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) || "")
        // 严格匹配 headless 特征，避免误报真 GPU
        if (/SwiftShader|Headless|Mesa/i.test(renderer)) {
          hits.push({ key: "headless-gl", detail: `webgl renderer: ${renderer}` })
        }
      }
    }
  } catch {
    /* ignore */
  }

  // 5. Notification 与 permissions API 状态矛盾
  // 真浏览器两者一致；headless chrome 会出现 Notification=denied 但 permissions=prompt
  try {
    if ("Notification" in window && "permissions" in navigator) {
      const perm = await (navigator as any).permissions.query({
        name: "notifications"
      })
      if (Notification.permission === "denied" && perm && perm.state === "prompt") {
        hits.push({ key: "perm-mismatch", detail: "notification permission mismatch" })
      }
    }
  } catch {
    /* ignore */
  }

  if (hits.length === 0) return ""
  return hits.map(h => h.key).join(",")
}
