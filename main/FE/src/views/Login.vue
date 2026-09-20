<template>
  <div class="login-page">
    <canvas ref="canvasRef" class="particle-canvas"></canvas>

    <div class="overlay"></div>

    <nav class="topnav">
      <div class="nav-brand">🎓 学生签到系统</div>
      <div class="nav-links">
        <a href="#" class="nav-link">首页</a>
        <a href="#" class="nav-link">功能</a>
        <a href="#" class="nav-link">帮助</a>
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from "vue"
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
  function resize() {
    canvasEl.width = window.innerWidth
    canvasEl.height = window.innerHeight
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

  const particles = Array.from({ length: 120 }, () => ({
    x: Math.random() * canvasEl.width,
    y: Math.random() * canvasEl.height,
    vx: (Math.random() - 0.5) * 0.5,
    vy: (Math.random() - 0.5) * 0.5,
    size: Math.random() * 1.5 + 1.5,
    baseSize: 0,
    // 鼠标接近时的发光强度
    glow: 0
  }))
  particles.forEach(p => { p.baseSize = p.size })

  function draw() {
    ctxEl.clearRect(0, 0, canvasEl.width, canvasEl.height)

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
          p.vx += (dx / dist) * force
          p.vy += (dy / dist) * force
          // 发光强度
          p.glow = 1 - dist / maxDist
        } else {
          p.glow *= 0.95
        }
      } else {
        p.glow *= 0.95
      }

      // 速度阻尼，防止无限加速
      p.vx *= 0.96
      p.vy *= 0.96
      // 最小基础速度，避免完全静止
      const speed = Math.sqrt(p.vx * p.vx + p.vy * p.vy)
      if (speed < 0.15) {
        p.vx += (Math.random() - 0.5) * 0.1
        p.vy += (Math.random() - 0.5) * 0.1
      }

      p.x += p.vx
      p.y += p.vy
      if (p.x <= 0 || p.x >= canvasEl.width) {
        p.vx = -p.vx
      }
      if (p.y <= 0 || p.y >= canvasEl.height) {
        p.vy = -p.vy
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
  draw()

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
  margin: 0 0 14px;
  font-size: 48px;
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: 2px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  padding: 10px 24px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2);
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
