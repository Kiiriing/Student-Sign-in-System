<template>
  <div class="login-page">
    <canvas ref="canvasRef" class="particle-canvas"></canvas>

    <div class="overlay"></div>

    <nav class="topnav">
      <div class="nav-brand">🎓 学生签到系统</div>
      <div class="nav-links">
        <a href="#" class="nav-link" @click.prevent="openModal('home')">首页</a>
        <a href="#" class="nav-link" @click.prevent="openModal('features')">功能</a>
        <a href="#" class="nav-link" @click.prevent="openModal('updates')">更新</a>
        <a href="#" class="nav-link" @click.prevent="openModal('help')">帮助</a>
      </div>
    </nav>

    <div class="hero">
      <div class="hero-inner">
        <span class="badge-tag fade-up" style="--delay: 0">Welcome Back</span>
        <h1 class="hero-title fade-up" style="--delay: 1"><span class="shimmer-txt">学生签到系统</span></h1>
        <p class="hero-subtitle fade-up" style="--delay: 2">Student Attendance System · 课堂签到 · 班级管理 · 数据统计</p>

        <!-- 玻璃态登录卡片 -->
        <div class="login-card fade-up" style="--delay: 3">
          <div class="input-box" :class="{ error: usernameError, success: usernameSuccess }">
            <span class="input-icon">👤</span>
            <input
              v-model="username"
              placeholder="请输入学号/用户名/姓名"
              autocomplete="off"
              @input="usernameError = false"
              @keyup.enter="focusPassword"
            />
          </div>
          <div class="input-box" :class="{ error: passwordError, success: passwordSuccess }">
            <span class="input-icon">🔒</span>
            <input
              ref="passwordInputRef"
              v-model="password"
              type="password"
              placeholder="请输入登录密码"
              @input="passwordError = false"
              @keyup.enter="login"
            />
          </div>
          <div class="btn-beam-wrap fade-up" style="--delay: 4">
            <button
              class="login-btn ripple-btn"
              :disabled="loading"
              @click="handleLoginClick"
            >
              {{ loading ? "登录中..." : "立即登录" }}
            </button>
          </div>
          <div class="message" :class="{ success: loginSuccess }">
            {{ message }}
          </div>
        </div>
      </div>
    </div>

    <!-- ===== 弹窗：首页 / 功能 / 更新 / 帮助（毛玻璃，点击 X 或任意处关闭） ===== -->
    <Transition name="modal-pop">
      <div v-if="activeModal" class="modal-mask" @click="closeModal">
        <div class="modal-panel">
          <button class="modal-close" type="button" aria-label="关闭" @click="closeModal">✕</button>
          <h3 class="modal-title">{{ modalMeta?.title }}</h3>
          <p class="modal-sub">{{ modalMeta?.subtitle }}</p>

          <div v-if="activeModal === 'home'" class="modal-body">
            <p class="modal-p">欢迎使用「学生签到系统」。登录后按角色自动跳转对应工作台：</p>
            <ul class="modal-list">
              <li v-for="item in HOME_ROLES" :key="item.name"><b>{{ item.name }}</b>：{{ item.desc }}</li>
            </ul>
          </div>

          <div v-else-if="activeModal === 'features'" class="modal-body feat-grid">
            <div v-for="f in FEATURE_LIST" :key="f.name" class="feat-item">
              <span class="feat-icon">{{ f.icon }}</span>
              <div>
                <div class="feat-name">{{ f.name }}</div>
                <div class="feat-desc">{{ f.desc }}</div>
              </div>
            </div>
          </div>

          <div v-else-if="activeModal === 'help'" class="modal-body">
            <p class="modal-p">有问题请发送邮件到 <a class="mail-link" href="mailto:liukiiriing@gmail.com">liukiiriing@gmail.com</a></p>
          </div>

          <div v-else class="modal-body updates-body">
            <div v-if="updatesLoading" class="updates-state">加载中…</div>
            <div v-else-if="updatesError" class="updates-state updates-error">{{ updatesError }}</div>
            <template v-else>
              <div v-for="group in groupedUpdates" :key="group.date" class="upd-group">
                <div class="upd-date"><span class="upd-dot"></span>{{ group.date }}</div>
                <div class="upd-cols">
                  <ul class="update-list">
                    <li v-for="u in group.left" :key="u.update_id">
                      <span class="u-tag" :class="TAG_CLASS[u.tag] || 'u-opt'">{{ u.tag }}</span>
                      <span class="u-text">{{ u.content }}</span>
                    </li>
                  </ul>
                  <ul class="update-list">
                    <li v-for="u in group.right" :key="u.update_id">
                      <span class="u-tag" :class="TAG_CLASS[u.tag] || 'u-opt'">{{ u.tag }}</span>
                      <span class="u-text">{{ u.content }}</span>
                    </li>
                  </ul>
                </div>
              </div>

              <div class="upd-pager">
                <button class="pager-btn" type="button" :disabled="updatesPage <= 1"
                  @click.stop="changeUpdatesPage(updatesPage - 1)">上一页</button>
                <span class="pager-info">共 {{ updatesTotalPages }} 次更新</span>
                <button class="pager-btn" type="button" :disabled="updatesPage >= updatesTotalPages"
                  @click.stop="changeUpdatesPage(updatesPage + 1)">下一页</button>
              </div>
            </template>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from "vue"
import { useRouter } from "vue-router"
import request from "../api/request"
import { getDeviceId } from "../utils/device"

interface LoginResponse {
  code: number
  message: string
  access_token: string
  user_id: string
  username: string
  role: number
  student_id?: string
  student_no?: string
  student_name?: string
  class_name?: string
  teacher_id?: string
  teacher_name?: string
  department?: string
  admin_name?: string
  error?: string
}

const router = useRouter()

const username = ref("")
const password = ref("")
const message = ref("")
const loginSuccess = ref(false)
const usernameError = ref(false)
const passwordError = ref(false)
const usernameSuccess = ref(false)
const passwordSuccess = ref(false)
const loading = ref(false)
const canvasRef = ref<HTMLCanvasElement>()
const passwordInputRef = ref<HTMLInputElement>()
const deviceId = ref(getDeviceId())
let animation: number

// ===== 登录页弹窗：首页 / 功能 / 更新 / 帮助 =====
type ModalKey = "home" | "features" | "updates" | "help"

const activeModal = ref<ModalKey | null>(null)

const MODAL_META: Record<ModalKey, { title: string; subtitle: string }> = {
  home: { title: "首页", subtitle: "三端协同 · 快速了解" },
  features: { title: "功能", subtitle: "系统主要能力" },
  updates: { title: "更新", subtitle: "今日更新内容" },
  help: { title: "帮助", subtitle: "获取支持" }
}

const modalMeta = computed(() => (activeModal.value ? MODAL_META[activeModal.value] : null))

// 今天第一次打开登录页时弹一次更新提醒，按自然日记录，同一天只弹一次
const NOTICE_KEY = "login_notice_date"

function todayKey() {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`
}

function openModal(key: ModalKey) {
  activeModal.value = key
  if (key === "updates") loadUpdates(1)
}

function closeModal() {
  activeModal.value = null
}

// ===== 更新日志：从后端接口分页拉取 =====
interface UpdateItem {
  update_id: number
  tag: string
  content: string
  date: string
  created_at: string
}

const updatesList = ref<UpdateItem[]>([])
const updatesLoading = ref(false)
const updatesError = ref("")
const updatesPage = ref(1)
// 总天数：一天算一次更新
const updatesTotalPages = ref(1)

// 类型 → 徽标样式类
const TAG_CLASS: Record<string, string> = { 新增: "u-new", 优化: "u-opt", 修复: "u-fix" }

// 按创建日期分组，并把每组的记录按「列优先」拆成左右两列
// 即：先从上到下填满左列，剩余的再从上到下填右列
const groupedUpdates = computed(() => {
  const map = new Map<string, UpdateItem[]>()
  for (const item of updatesList.value) {
    const arr = map.get(item.date)
    if (arr) arr.push(item)
    else map.set(item.date, [item])
  }
  return [...map.entries()].map(([date, items]) => {
    const half = Math.ceil(items.length / 2)
    return { date, left: items.slice(0, half), right: items.slice(half) }
  })
})

async function loadUpdates(page = 1) {
  updatesLoading.value = true
  updatesError.value = ""
  try {
    // 后端按日期分页：一天一页，翻页即查看更早的更新
    const res = await request.get("/api/system/updates", { params: { page } })
    if (res.data.code === 200) {
      const data = res.data.data
      updatesList.value = data.list
      updatesPage.value = data.page
      updatesTotalPages.value = data.total_pages
    } else {
      updatesError.value = res.data.message || "加载更新日志失败"
    }
  } catch {
    updatesError.value = "网络异常，无法获取更新日志"
  } finally {
    updatesLoading.value = false
  }
}

function changeUpdatesPage(page: number) {
  if (page < 1 || page > updatesTotalPages.value || page === updatesPage.value) return
  loadUpdates(page)
}

const HOME_ROLES = [
  { name: "学生端", desc: "查看课表，一键完成课堂签到" },
  { name: "教师端", desc: "发起课堂点名、语音朗读与数据统计" },
  { name: "管理员端", desc: "管理教师 / 学生账户、班级与课程安排" }
]

const FEATURE_LIST = [
  { icon: "🔐", name: "统一登录", desc: "学号 / 用户名 / 姓名 + 密码，按角色自动跳转" },
  { icon: "📖", name: "课表与签到", desc: "学生端查看课表并完成签到" },
  { icon: "🎙️", name: "课堂点名", desc: "语音朗读点名，逐个确认到场" },
  { icon: "👥", name: "账户与班级", desc: "创建账户、分配班级、批量管理" },
  { icon: "📚", name: "课程管理", desc: "支持多天重复排课与上课时间段设置" },
  { icon: "📊", name: "数据统计", desc: "签到进度与状态分布可视化图表" }
]

// 用户名框 Enter → 聚焦到密码框
function focusPassword() {
  if (!username.value) {
    usernameError.value = true
    message.value = "请输入学号/用户名/姓名"
    return
  }
  passwordInputRef.value?.focus()
}

// 按钮波纹效果 + 登录
function handleLoginClick(e: MouseEvent) {
  createRipple(e)
  login()
}

// 创建水波纹
function createRipple(e: MouseEvent) {
  const button = e.currentTarget as HTMLButtonElement
  const rect = button.getBoundingClientRect()
  const size = Math.max(rect.width, rect.height)
  const x = e.clientX - rect.left - size / 2
  const y = e.clientY - rect.top - size / 2

  // 清理旧波纹
  const oldRipples = button.querySelectorAll(".ripple-wave")
  oldRipples.forEach((r) => r.remove())

  const ripple = document.createElement("span")
  ripple.className = "ripple-wave"
  ripple.style.width = ripple.style.height = `${size}px`
  ripple.style.left = `${x}px`
  ripple.style.top = `${y}px`
  button.appendChild(ripple)

  // 动画结束后移除
  setTimeout(() => {
    ripple.remove()
  }, 700)
}

async function login() {
  usernameError.value = false
  passwordError.value = false
  loginSuccess.value = false
  if (!username.value) {
    usernameError.value = true
    message.value = "请输入学号/用户名/姓名"
    return
  }
  if (!password.value) {
    passwordError.value = true
    message.value = "请输入密码"
    return
  }
  loading.value = true
  try {
    const res = await request.post<LoginResponse>("/api/auth/login", {
      username: username.value,
      password: password.value,
      device_id: deviceId.value
    })
    if (res.data.code === 200) {
      loginSuccess.value = true
      usernameSuccess.value = true
      passwordSuccess.value = true
      message.value = "登录成功，正在跳转..."
      const userData = {
        user_id: res.data.user_id,
        username: res.data.username,
        role: res.data.role,
        student_id: res.data.student_id,
        student_no: res.data.student_no,
        student_name: res.data.student_name,
        class_name: res.data.class_name,
        teacher_id: res.data.teacher_id,
        teacher_name: res.data.teacher_name,
        department: res.data.department,
        admin_name: res.data.admin_name
      }
      localStorage.setItem("user", JSON.stringify(userData))
      localStorage.setItem("access_token", res.data.access_token)

      setTimeout(() => {
        const userRole = res.data.role
        if (userRole === 1) {
          router.push("/student/dashboard")
        } else if (userRole === 2) {
          router.push("/teacher/dashboard")
        } else if (userRole === 3) {
          router.push("/admin/dashboard")
        } else {
          message.value = "未知角色，无法跳转"
        }
      }, 800)
    } else {
      usernameError.value = true
      passwordError.value = true
      message.value = res.data.message
    }
  } catch (error: any) {
    usernameError.value = true
    passwordError.value = true
    if (error?.response?.data?.message) {
      message.value = error.response.data.message
    } else {
      message.value = "服务器连接失败"
    }
  } finally {
    loading.value = false
  }
}

function initCanvas(): (() => void) | undefined {
  if (window.innerWidth < 700) {
    return
  }
  const canvas = canvasRef.value
  if (!canvas) {
    return
  }
  const ctx = canvas.getContext("2d")
  if (!ctx) {
    return
  }
  const canvasEl: HTMLCanvasElement = canvas
  const ctxEl: CanvasRenderingContext2D = ctx

  // 逻辑尺寸（CSS 像素），物理计算与绘制统一用它，避免高 DPI 屏被拉伸发虚
  let viewW = 0
  let viewH = 0
  function resize() {
    const dpr = window.devicePixelRatio || 1
    viewW = window.innerWidth
    viewH = window.innerHeight
    canvasEl.width = Math.round(viewW * dpr)
    canvasEl.height = Math.round(viewH * dpr)
    ctxEl.setTransform(dpr, 0, 0, dpr, 0, 0)
  }
  resize()
  window.addEventListener("resize", resize)

  // 鼠标位置
  const mouse = { x: -9999, y: -9999, active: false }
  function onMouseMove(e: MouseEvent) {
    mouse.x = e.clientX
    mouse.y = e.clientY
    mouse.active = true
  }
  function onMouseLeave() {
    mouse.active = false
    mouse.x = -9999
    mouse.y = -9999
  }
  function onTouchMove(e: TouchEvent) {
    if (e.touches.length > 0) {
      mouse.x = e.touches[0].clientX
      mouse.y = e.touches[0].clientY
      mouse.active = true
    }
  }
  window.addEventListener("mousemove", onMouseMove)
  window.addEventListener("mouseleave", onMouseLeave)
  window.addEventListener("touchmove", onTouchMove)

  // 以 60fps 为基准的速度（px/帧），实际位移按 dt 缩放
  const FRAME_MS = 1000 / 60
  const MIN_SPEED = 0.15
  const MAX_SPEED = 0.4
  const SPEED_LIMIT = 3

  const particles = Array.from({ length: 120 }, () => {
    const angle = Math.random() * Math.PI * 2
    const speed = MIN_SPEED + Math.random() * (MAX_SPEED - MIN_SPEED)
    return {
      x: Math.random() * viewW,
      y: Math.random() * viewH,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed,
      // 漂移方向：angle 缓慢自转，轨迹是缓慢弧线而不是机械直线
      angle,
      speed,
      turn: (Math.random() - 0.5) * 0.012,
      size: Math.random() * 1.5 + 1.5,
      baseSize: 0,
      // 鼠标接近时的发光强度
      glow: 0
    }
  })
  particles.forEach(p => { p.baseSize = p.size })

  let lastFrame = performance.now()
  function draw(now: number) {
    // 帧率归一化：高刷屏（144/165Hz）与 60Hz 下运动速度保持一致
    const dt = Math.min((now - lastFrame) / FRAME_MS, 3)
    lastFrame = now

    ctxEl.clearRect(0, 0, viewW, viewH)

    // 鼠标光晕（径向渐变背景）
    if (mouse.active) {
      const grad = ctxEl.createRadialGradient(
        mouse.x, mouse.y, 0,
        mouse.x, mouse.y, 200
      )
      grad.addColorStop(0, "rgba(255, 255, 255, 0.12)")
      grad.addColorStop(0.5, "rgba(192, 132, 252, 0.06)")
      grad.addColorStop(1, "rgba(0, 0, 0, 0)")
      ctxEl.fillStyle = grad
      ctxEl.beginPath()
      ctxEl.arc(mouse.x, mouse.y, 200, 0, Math.PI * 2)
      ctxEl.fill()
    }

    const glowDecay = Math.pow(0.95, dt)
    const ease = 1 - Math.pow(0.96, dt)

    particles.forEach((p) => {
      // 鼠标互动：排斥效果 + 发光
      if (mouse.active) {
        const dx = p.x - mouse.x
        const dy = p.y - mouse.y
        const dist = Math.sqrt(dx * dx + dy * dy)
        const maxDist = 120
        if (dist < maxDist && dist > 0) {
          // 排斥力（越近力越大）
          const force = (1 - dist / maxDist) * 1.5
          p.vx += (dx / dist) * force * dt
          p.vy += (dy / dist) * force * dt
          // 发光强度
          p.glow = 1 - dist / maxDist
        } else {
          p.glow *= glowDecay
        }
      } else {
        p.glow *= glowDecay
      }

      // 漂移方向缓慢自转
      p.angle += p.turn * dt
      // 平滑回归基础漂移速度：鼠标推力的余速会自然衰减，不会把粒子定在原地抖
      p.vx += (Math.cos(p.angle) * p.speed - p.vx) * ease
      p.vy += (Math.sin(p.angle) * p.speed - p.vy) * ease

      // 限制极限速度，避免多帧叠加后飞出去
      const speed = Math.sqrt(p.vx * p.vx + p.vy * p.vy)
      if (speed > SPEED_LIMIT) {
        p.vx = (p.vx / speed) * SPEED_LIMIT
        p.vy = (p.vy / speed) * SPEED_LIMIT
      }

      p.x += p.vx * dt
      p.y += p.vy * dt
      // 撞边反弹：同时翻转漂移方向，否则目标速度会把粒子重新压回墙上
      if (p.x <= 0) {
        p.x = 0
        p.vx = Math.abs(p.vx)
        p.angle = Math.PI - p.angle
      } else if (p.x >= viewW) {
        p.x = viewW
        p.vx = -Math.abs(p.vx)
        p.angle = Math.PI - p.angle
      }
      if (p.y <= 0) {
        p.y = 0
        p.vy = Math.abs(p.vy)
        p.angle = -p.angle
      } else if (p.y >= viewH) {
        p.y = viewH
        p.vy = -Math.abs(p.vy)
        p.angle = -p.angle
      }

      // 粒子大小随发光强度变化
      const currentSize = p.baseSize + p.glow * 2.5

      // 发光粒子（带光晕）
      if (p.glow > 0.1) {
        const glowGrad = ctxEl.createRadialGradient(
          p.x, p.y, 0,
          p.x, p.y, currentSize * 4
        )
        glowGrad.addColorStop(0, `rgba(255, 255, 255, ${p.glow * 0.6})`)
        glowGrad.addColorStop(0.5, `rgba(192, 132, 252, ${p.glow * 0.3})`)
        glowGrad.addColorStop(1, "rgba(0, 0, 0, 0)")
        ctxEl.fillStyle = glowGrad
        ctxEl.beginPath()
        ctxEl.arc(p.x, p.y, currentSize * 4, 0, Math.PI * 2)
        ctxEl.fill()
      }

      // 粒子本体
      ctxEl.beginPath()
      ctxEl.arc(p.x, p.y, currentSize, 0, Math.PI * 2)
      const alpha = 0.6 + p.glow * 0.4
      ctxEl.fillStyle = `rgba(255, 255, 255, ${alpha})`
      ctxEl.fill()
    })

    // 粒子之间的连线
    for (let i = 0; i < particles.length; i++) {
      const p = particles[i]
      // 粒子与鼠标的连线
      if (mouse.active) {
        const dx = p.x - mouse.x
        const dy = p.y - mouse.y
        const dist = Math.sqrt(dx * dx + dy * dy)
        if (dist < 150) {
          ctxEl.beginPath()
          ctxEl.moveTo(p.x, p.y)
          ctxEl.lineTo(mouse.x, mouse.y)
          const alpha = (1 - dist / 150) * 0.5
          ctxEl.strokeStyle = `rgba(192, 132, 252, ${alpha})`
          ctxEl.lineWidth = 1
          ctxEl.stroke()
        }
      }
      // 粒子之间的连线
      for (let j = i + 1; j < particles.length; j++) {
        const q = particles[j]
        const dx = p.x - q.x
        const dy = p.y - q.y
        const distance = Math.sqrt(dx * dx + dy * dy)
        if (distance < 130) {
          ctxEl.beginPath()
          ctxEl.moveTo(p.x, p.y)
          ctxEl.lineTo(q.x, q.y)
          // 鼠标附近的粒子连线更亮
          const glowBoost = Math.max(p.glow, q.glow) * 0.5
          const alpha = (1 - distance / 130) + glowBoost
          ctxEl.strokeStyle = `rgba(255, 255, 255, ${Math.min(alpha, 1)})`
          ctxEl.lineWidth = 0.8
          ctxEl.stroke()
        }
      }
    }

    animation = requestAnimationFrame(draw)
  }
  requestAnimationFrame(draw)

  // 清理函数
  const cleanup = () => {
    window.removeEventListener("mousemove", onMouseMove)
    window.removeEventListener("mouseleave", onMouseLeave)
    window.removeEventListener("touchmove", onTouchMove)
    window.removeEventListener("resize", resize)
  }
  return cleanup
}

// 保存清理函数
let cleanupCanvas: (() => void) | null = null

onMounted(() => {
  const fn = initCanvas()
  if (fn) {
    cleanupCanvas = fn
  }
  // 今天第一次打开登录页：弹出更新提醒（同一天只弹一次）
  const today = todayKey()
  if (localStorage.getItem(NOTICE_KEY) !== today) {
    localStorage.setItem(NOTICE_KEY, today)
    openModal("updates")
  }
})

onBeforeUnmount(() => {
  cancelAnimationFrame(animation)
  if (cleanupCanvas) {
    cleanupCanvas()
    cleanupCanvas = null
  }
})
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.login-page {
  position: fixed;
  inset: 0;
  overflow: hidden;
  background: linear-gradient(135deg, #1a1c3a 0%, #2d1b4e 50%, #1a1c3a 100%);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
}

/* ===== 1. 粒子背景 ===== */
.particle-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
}

/* ===== 2. 遮罩层 ===== */
.overlay {
  position: absolute;
  inset: 0;
  z-index: 1;
  background:
    radial-gradient(800px 500px at 30% 20%, rgba(99, 102, 241, 0.25), transparent 60%),
    radial-gradient(700px 500px at 70% 80%, rgba(236, 72, 153, 0.2), transparent 55%),
    linear-gradient(180deg, rgba(15, 23, 42, 0.7) 0%, rgba(15, 23, 42, 0.45) 50%, rgba(15, 23, 42, 0.85) 100%);
  pointer-events: none;
}

/* ===== 3. 顶部导航 ===== */
.topnav {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 32px;
}
.nav-brand {
  color: #fff;
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 0.5px;
}

/* 导航链接 + 下划线展开 */
.nav-links {
  display: flex;
  align-items: center;
  gap: 28px;
}
.nav-link {
  position: relative;
  color: rgba(255, 255, 255, 0.75);
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  padding-bottom: 4px;
  transition: color 0.25s ease-out;
}
.nav-link::after {
  content: "";
  position: absolute;
  left: 0;
  bottom: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, #fff, rgba(255, 255, 255, 0.5));
  border-radius: 1px;
  transform: scaleX(0);
  transform-origin: left center;
  transition: transform 0.35s ease-out;
}
.nav-link:hover {
  color: #fff;
}
.nav-link:hover::after {
  transform: scaleX(1);
}

/* ===== 4. Hero 区 ===== */
.hero {
  position: relative;
  z-index: 10;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 80px 20px 100px;
}
.hero-inner {
  width: 100%;
  max-width: 460px;
  text-align: center;
}

.badge-tag {
  display: inline-block;
  padding: 5px 16px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.25);
  color: rgba(255, 255, 255, 0.85);
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  margin-bottom: 24px;
  backdrop-filter: blur(6px);
}

/* ===== 金属光泽扫光文字（Metallic Shimmer Text） ===== */
.hero-title {
  /* 必须是块级：inline-flex 会让标题和上面的 .badge-tag 挤在同一行并按基线对齐 */
  display: flex;
  width: fit-content;
  margin: 0 auto 14px;
  font-size: 48px;
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: 2px;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  padding: 10px 24px;
  /* box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2); */
  transition: all 250ms cubic-bezier(0.16, 1, 0.3, 1);
}
.hero-title:hover {
  transform: translateY(-3px);
  box-shadow: 0 20px 35px -5px rgba(0, 0, 0, 0.3);
}

.shimmer-txt {
  background: linear-gradient(
    100deg,
    #475569 0%,
    #94a3b8 30%,
    #e2e8f0 40%,
    #ffffff 50%,
    #e2e8f0 68%,
    #94a3b8 88%,
    #475569 100%
  );
  background-size: 250% 100%;
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
  animation: shimmerFlow 4s linear infinite;
  filter: drop-shadow(0 2px 10px rgba(245, 158, 11, 0.3));
}

@keyframes shimmerFlow {
  0% { background-position: 200% 50%; }
  100% { background-position: -50% 50%; }
}

.hero-subtitle {
  margin: 0 0 40px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 15px;
  line-height: 1.6;
  letter-spacing: 0.5px;
  max-width: 420px;
  margin-left: auto;
  margin-right: auto;
}

/* ===== 玻璃态登录卡片 ===== */
.login-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(16px) saturate(160%);
  -webkit-backdrop-filter: blur(16px) saturate(160%);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 24px;
  padding: 32px 28px;
  box-shadow:
    0 20px 50px rgba(0, 0, 0, 0.35),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.input-box {
  width: 100%;
  height: 52px;
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(6px);
  border: 1.5px solid rgba(255, 255, 255, 0.3);
  border-radius: 999px;
  padding: 0 18px;
  margin-bottom: 16px;
  transition: all 0.25s ease-out;
}
.input-box:focus-within {
  border-color: rgba(255, 255, 255, 0.7);
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.2);
}
.input-icon {
  margin-right: 12px;
  font-size: 18px;
  opacity: 0.8;
}
.input-box input {
  flex: 1;
  width: 100%;
  border: none;
  outline: none;
  background: transparent;
  color: #fff;
  font-size: 15px;
  font-family: inherit;
}
.input-box input::placeholder {
  color: rgba(255, 255, 255, 0.6);
}
.input-box.success {
  border-color: #10b981;
  background: rgba(16, 185, 129, 0.12);
}
.input-box.error {
  border-color: #ef4444;
  background: rgba(239, 68, 68, 0.12);
  animation: shake 0.3s;
}

.login-btn {
  position: relative;
  overflow: hidden;
  width: 100%;
  height: 52px;
  border: none;
  border-radius: 999px;
  color: #1a1c3a;
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 0.5px;
  cursor: pointer;
  background: #fff;
  transition: all 0.2s ease-out;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.3);
}

/* ===== 流光环形边框（覆盖整个按钮） ===== */
.btn-beam-wrap {
  position: relative;
  width: 100%;
  height: 52px;
  margin-top: 8px;
  border-radius: 999px;
  overflow: hidden;
  isolation: isolate;
}
.btn-beam-wrap::before {
  content: "";
  position: absolute;
  inset: -50%;
  border-radius: 999px;
  background: conic-gradient(
    from 0deg,
    transparent 0deg,
    transparent 240deg,
    #6366f1 290deg,
    #ec4899 320deg,
    #fde68a 345deg,
    #ffffff 360deg
  );
  animation: beamSpin 4s linear infinite;
  filter: blur(8px);
  z-index: 0;
}
.btn-beam-wrap .login-btn {
  position: relative;
  z-index: 2;
  height: 100%;
  margin-top: 0;
  background: rgba(255, 255, 255, 0.78);
  backdrop-filter: blur(2px);
  box-shadow: none;
}
.btn-beam-wrap .login-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.68);
}

@keyframes beamSpin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 水波纹特效 */
.ripple-wave {
  position: absolute;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.5) 0%, rgba(99, 102, 241, 0.2) 50%, transparent 80%);
  transform: scale(0);
  opacity: 1;
  pointer-events: none;
  animation: rippleExpand 0.65s ease-out forwards;
}
@keyframes rippleExpand {
  0% {
    transform: scale(0);
    opacity: 1;
  }
  100% {
    transform: scale(2.5);
    opacity: 0;
  }
}
.login-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.5);
}
.login-btn:active:not(:disabled) {
  transform: scale(0.98) translateY(0);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}
.login-btn:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.8), 0 0 0 5px rgba(0, 0, 0, 0.3);
}
.login-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
  transform: none;
}

.message {
  margin-top: 18px;
  font-size: 14px;
  font-weight: 500;
  color: #fca5a5;
  min-height: 20px;
  transition: color 0.2s ease-out;
}
.message.success {
  color: #6ee7b7;
}

/* ===== 淡入上移入场动画 ===== */
.fade-up {
  opacity: 0;
  transform: translateY(20px);
  animation: fadeInUp 0.7s ease-out forwards;
  animation-delay: calc(var(--delay, 0) * 0.12s + 0.15s);
}

@keyframes fadeInUp {
  0% {
    opacity: 0;
    transform: translateY(20px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes shake {
  0% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  50% { transform: translateX(5px); }
  75% { transform: translateX(-5px); }
  100% { transform: translateX(0); }
}

/* ===== 弹窗（毛玻璃，与登录卡片同一设计语言） ===== */
.modal-mask {
  position: fixed;
  inset: 0;
  z-index: 100;
  display: flex;
  padding: 24px 20px;
  overflow-y: auto;
  background: rgba(10, 14, 30, 0.55);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}
.modal-panel {
  position: relative;
  /* margin:auto 让面板在遮罩中自动居中，同时内容过高时整体可滚动而不被裁切 */
  margin: auto;
  width: 100%;
  max-width: 680px;
  padding: 28px 30px 22px;
  border-radius: 24px;
  color: #fff;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(24px) saturate(160%);
  -webkit-backdrop-filter: blur(24px) saturate(160%);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow:
    0 20px 50px rgba(0, 0, 0, 0.35),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}
/* 顶部一道细渐变光：点到为止的科技感 */
.modal-panel::before {
  content: "";
  position: absolute;
  top: 0;
  left: 26px;
  right: 26px;
  height: 2px;
  border-radius: 0 0 2px 2px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.85), #a78bfa, transparent);
  opacity: 0.75;
  pointer-events: none;
}
.modal-close {
  position: absolute;
  top: 14px;
  right: 14px;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
  font-size: 13px;
  line-height: 1;
  cursor: pointer;
  transition: all 0.2s ease-out;
}
.modal-close:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: rotate(90deg);
}
.modal-title {
  margin: 0 0 6px;
  font-size: 19px;
  font-weight: 700;
  letter-spacing: 0.5px;
  background: linear-gradient(90deg, #ffffff, #c7d2fe);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
}
.modal-sub {
  margin: 0 0 20px;
  font-size: 12px;
  letter-spacing: 1.5px;
  color: rgba(255, 255, 255, 0.55);
}
.modal-body {
  font-size: 14px;
  line-height: 1.7;
  color: rgba(255, 255, 255, 0.88);
}
.modal-p {
  margin: 0 0 10px;
}
.modal-list {
  margin: 0;
  padding-left: 18px;
}
.modal-list li {
  margin-bottom: 8px;
}
.modal-list b {
  color: #fff;
}

/* 功能网格 */
.feat-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.feat-item {
  display: flex;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
}
.feat-icon {
  font-size: 18px;
  line-height: 1.3;
}
.feat-name {
  font-weight: 600;
  font-size: 14px;
}
.feat-desc {
  font-size: 12px;
  line-height: 1.5;
  color: rgba(255, 255, 255, 0.65);
}

/* 帮助：邮箱链接 */
.mail-link {
  color: #a5b4fc;
  text-decoration: underline;
}
.mail-link:hover {
  color: #fff;
}

/* 更新列表：先填满左列，再填右列（列优先） */
.upd-cols {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}
.update-list {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin: 0;
  padding: 0;
  list-style: none;
}
.update-list li {
  display: flex;
  gap: 10px;
  padding: 9px 10px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.08);
  transition: background 0.2s ease-out, border-color 0.2s ease-out;
}
.update-list li:hover {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(255, 255, 255, 0.2);
}
.u-tag {
  flex: none;
  height: 20px;
  padding: 0 9px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
  line-height: 20px;
  border: 1px solid transparent;
}
.u-new {
  background: rgba(16, 185, 129, 0.2);
  border-color: rgba(16, 185, 129, 0.4);
  color: #6ee7b7;
}
.u-opt {
  background: rgba(129, 140, 248, 0.2);
  border-color: rgba(129, 140, 248, 0.4);
  color: #c7d2fe;
}
.u-fix {
  background: rgba(245, 158, 11, 0.2);
  border-color: rgba(245, 158, 11, 0.4);
  color: #fcd34d;
}
.u-text {
  font-size: 13px;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.86);
}

/* 更新分组：按日期 */
.upd-group {
  margin-bottom: 18px;
}
.upd-group:last-child {
  margin-bottom: 0;
}
.upd-date {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  padding-bottom: 8px;
  font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 1px;
  color: rgba(255, 255, 255, 0.92);
}
/* 日期下划线：淡出渐隐 */
.upd-date::after {
  content: "";
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 1px;
  background: linear-gradient(90deg, rgba(255, 255, 255, 0.35), transparent);
}
.upd-dot {
  flex: none;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #a78bfa;
  box-shadow: 0 0 8px rgba(167, 139, 250, 0.9);
}

/* 加载 / 错误状态 */
.updates-state {
  padding: 26px 0;
  text-align: center;
  font-size: 13px;
  letter-spacing: 1px;
  color: rgba(255, 255, 255, 0.6);
}
.updates-error {
  color: #fca5a5;
}

/* 翻页器 */
.upd-pager {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-top: 18px;
  padding-top: 14px;
  border-top: 1px solid rgba(255, 255, 255, 0.14);
}
.pager-btn {
  padding: 7px 16px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.28);
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  font-size: 12px;
  letter-spacing: 0.5px;
  cursor: pointer;
  transition: all 0.2s ease-out;
}
.pager-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.22);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-1px);
}
.pager-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}
.pager-info {
  font-size: 12px;
  letter-spacing: 0.5px;
  color: rgba(255, 255, 255, 0.6);
}

/* 弹窗过渡：遮罩淡入 + 面板缩放上浮 */
.modal-pop-enter-active,
.modal-pop-leave-active {
  transition: opacity 0.25s ease-out;
}
.modal-pop-enter-from,
.modal-pop-leave-to {
  opacity: 0;
}
.modal-pop-enter-active .modal-panel,
.modal-pop-leave-active .modal-panel {
  transition: transform 0.25s ease-out, opacity 0.25s ease-out;
}
.modal-pop-enter-from .modal-panel,
.modal-pop-leave-to .modal-panel {
  opacity: 0;
  transform: scale(0.94) translateY(10px);
}

/* ===== 响应式 ===== */
@media (max-width: 700px) {
  .particle-canvas { display: none; }
  .login-page {
    background: linear-gradient(135deg, #1a1c3a 0%, #2d1b4e 50%, #1a1c3a 100%);
  }
  .topnav { padding: 16px 18px; }
  .nav-links { gap: 18px; }
  .nav-link { font-size: 13px; }
  .hero { padding: 60px 16px 80px; }
  .hero-title { font-size: 32px; }
  .hero-subtitle { font-size: 13px; margin-bottom: 28px; }
  .badge-tag { font-size: 11px; margin-bottom: 18px; }
  .login-card { padding: 24px 20px; border-radius: 20px; }
  .feat-grid { grid-template-columns: 1fr; }
  .upd-cols { flex-direction: column; }
  .modal-panel { padding: 24px 20px 18px; }
}

@media (max-width: 380px) {
  .hero-title { font-size: 28px; }
  .input-box { height: 48px; }
  .login-btn { height: 48px; font-size: 15px; }
}

@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.001ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.001ms !important;
  }
  .fade-up {
    opacity: 1 !important;
    transform: none !important;
    animation: none !important;
  }
  .shimmer-txt {
    background: none !important;
    -webkit-text-fill-color: #fff !important;
    color: #fff !important;
    animation: none !important;
  }
  .hero-title {
    animation: none !important;
    transform: none !important;
  }
  .btn-beam-wrap::before {
    animation: none !important;
    display: none !important;
  }
  .login-btn:hover:not(:disabled),
  .login-btn:active:not(:disabled) {
    transform: none !important;
  }
}
</style>
