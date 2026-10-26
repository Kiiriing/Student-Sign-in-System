<template>
  <div class="student-page">
    <!-- 顶部导航 -->
    <header class="topbar">
      <div class="topbar-inner">
        <div class="brand">
          <span class="brand-icon">学</span>
          <div class="brand-text">
            <h1>学生签到</h1>
            <span>Student Attendance</span>
          </div>
        </div>
        <div class="user-chip">
          <span class="user-avatar">{{ firstName }}</span>
          <div class="user-info">
            <span class="user-name">{{ student.student_name }}</span>
            <span class="user-no">{{ student.student_no }}</span>
          </div>
          <button class="btn btn-ghost btn-sm" @click="logout">退出</button>
        </div>
      </div>
    </header>

    <main class="main">
      <!-- 个人信息卡 -->
      <section class="card profile-card">
        <div class="profile-avatar">{{ firstName }}</div>
        <div class="profile-detail">
          <h2>{{ student.student_name }}</h2>
          <div class="profile-meta">
            <span class="meta-item"><span class="meta-label">学号</span>{{ student.student_no }}</span>
            <span class="meta-dot">·</span>
            <span class="meta-item"><span class="meta-label">班级</span>{{ student.class_name }}</span>
          </div>
        </div>
      </section>

      <!-- 今日课程 -->
      <section class="card">
        <div class="card-head">
          <div class="card-title">
            <span class="card-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"
                stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="4.5" width="18" height="16" rx="3" />
                <path d="M8 2.5v4M16 2.5v4M3 10h18" />
              </svg>
            </span>
            <div>
              <h2>今日课程</h2>
              <p class="card-sub">{{ today }}</p>
            </div>
          </div>
          <button class="btn btn-soft btn-sm" :disabled="coursesRefreshing" @click="refreshCourses">刷新</button>
        </div>

        <div v-if="courses.length" class="course-grid">
          <div
            v-for="item in courseCards"
            :key="item.course.id"
            class="course-card"
            :class="`status-${item.status}`"
          >
            <div class="course-main">
              <h3>{{ item.course.course_name }}</h3>
              <div class="course-meta">
                <span>教师：{{ item.course.teacher_name }}</span>
                <span>时间：{{ item.course.time || '未安排' }}</span>
              </div>
              <div class="course-status">
                <span class="badge" :class="item.badgeClass">{{ item.badgeText }}</span>
              </div>
            </div>
            <div class="course-action">
              <button
                class="btn"
                :class="item.btnClass"
                :disabled="item.status !== 'active'"
                @click="signIn(item.course)"
              >
                {{ item.btnText }}
              </button>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <p>今日暂无课程安排</p>
        </div>
      </section>

      <!-- 签到记录 -->
      <section class="card">
        <div class="card-head">
          <div class="card-title">
            <span class="card-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"
                stroke-linecap="round" stroke-linejoin="round">
                <path d="M9 6h12M9 12h12M9 18h12" />
                <path d="M4 6h.01M4 12h.01M4 18h.01" />
              </svg>
            </span>
            <div>
              <h2>签到记录</h2>
              <p class="card-sub">查看历史签到情况</p>
            </div>
          </div>
          <div class="filter-bar">
            <input
              type="date"
              class="form-input"
              v-model="filterDate"
              @change="getRecords"
              @click="openDatePicker"
            />
            <button class="btn btn-soft btn-sm" @click="clearDateFilter">全部</button>
          </div>
        </div>

        <div v-if="records.length" class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>课程</th>
                <th>授课教师</th>
                <th>签到时间</th>
                <th>IP 地址</th>
                <th>来源</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in records" :key="item.id">
                <td class="cell-strong">{{ item.course_name }}</td>
                <td>{{ item.teacher_name || '-' }}</td>
                <td><span class="mono">{{ item.time }}</span></td>
                <td><span class="mono">{{ item.ip || '-' }}</span></td>
                <td>
                  <span v-if="Number(item.is_cross) === 1" class="badge badge-cyan">
                    {{ item.source_site_name || '其他网站' }}
                  </span>
                  <span v-else class="text-muted">{{ item.source_site_name || '-' }}</span>
                </td>
                <td>
                  <span
                    class="badge"
                    :class="Number(item.is_script) === 1 ? 'badge-danger' : (Number(item.is_cross) === 1 ? 'badge-cyan' : statusBadgeClass(item.status))"
                  >{{ item.status_text }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="empty-state">
          <p>{{ filterDate ? `${filterDate} 暂无签到记录` : '暂无签到记录' }}</p>
        </div>
      </section>

      <!-- 班级签到情况 -->
      <section class="card">
        <div class="card-head">
          <div class="card-title">
            <span class="card-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"
                stroke-linecap="round" stroke-linejoin="round">
                <path d="M16 20v-1.5a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4V20" />
                <circle cx="9.5" cy="7.5" r="3.5" />
                <path d="M17 11.2a3.5 3.5 0 0 0 0-6.4M21 20v-1.4a4 4 0 0 0-3-3.8" />
              </svg>
            </span>
            <div>
              <h2>班级签到情况</h2>
              <p class="card-sub">查看本班所有同学今日的签到情况</p>
            </div>
          </div>
          <div class="filter-bar">
            <input
              type="date"
              class="form-input"
              v-model="classDate"
              @change="getClassAttendance"
              @click="openDatePicker"
            />
            <button class="btn btn-soft btn-sm" @click="resetClassDate">今天</button>
            <button class="btn btn-soft btn-sm" :disabled="classRefreshing" @click="refreshClassAttendance">刷新</button>
          </div>
        </div>

        <!-- 后端即使当天没有课程也会返回全班名单，这里必须同时判断课程，否则会出现空表格 -->
        <div v-if="classAttendance.courses.length && classAttendance.roster.length">
          <p class="class-meta">
            <span>班级：{{ classAttendance.class_name || '-' }}</span>
            <span class="meta-dot">·</span>
            <span>日期：{{ classAttendance.date }}</span>
            <span class="meta-dot">·</span>
            <span>共 {{ classAttendance.roster.length }} 人</span>
          </p>

          <div class="table-wrap">
            <table class="data-table class-table">
              <thead>
                <tr>
                  <th class="col-student">学号</th>
                  <th class="col-name">姓名</th>
                  <th v-for="c in classAttendance.courses" :key="c.course_id" class="col-course">
                    <div class="course-th">
                      <span class="course-th-name">{{ c.course_name }}</span>
                      <span class="course-th-time">{{ c.time || '-' }}</span>
                    </div>
                  </th>
                  <th class="col-summary">汇总</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="r in classAttendance.roster"
                  :key="r.student_id"
                  :class="{ 'row-me': r.is_me }"
                >
                  <td><span class="mono">{{ r.student_no }}</span></td>
                  <td class="cell-strong">
                    {{ r.student_name }}
                    <span v-if="r.is_me" class="me-tag">我</span>
                  </td>
                  <td v-for="c in classAttendance.courses" :key="c.course_id">
                    <span
                      v-if="c.task_id"
                      class="badge"
                      :class="cellBadgeClass(r.row_status[c.course_id])"
                    >{{ r.row_status[c.course_id]?.status_text }}</span>
                    <span v-else class="no-task">无任务</span>
                  </td>
                  <td>
                    <div class="summary-cell">
                      <template v-for="(c, idx) in classAttendance.courses" :key="c.course_id">
                        <span
                          v-if="c.task_id"
                          class="summary-pill"
                          :class="cellBadgeClass(r.row_status[c.course_id])"
                        >
                          <span class="summary-dot"></span>
                          <span class="summary-text">
                            <span class="summary-course">第{{ toChineseNum(idx + 1) }}节</span>
                            <span class="summary-status">{{ r.row_status[c.course_id]?.status_text }}</span>
                          </span>
                        </span>
                      </template>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div v-else class="empty-state">
          <p>{{ classDate ? '当天暂无课程安排' : '今日暂无课程安排' }}</p>
        </div>
      </section>
    </main>

    <!-- Toast -->
    <transition name="toast">
      <div v-if="toast.show" class="toast" :class="toast.type">{{ toast.msg }}</div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, type Ref } from "vue"
import request from "../api/request"
import { getDeviceId } from "../utils/device"
import { collectBrowserFingerprint } from "../utils/fingerprint"
// 考勤状态 → 徽标样式：与教师端共用同一份映射（原先两边各复制了一份）
import { attendanceStatusBadgeClass as statusBadgeClass } from "../utils/status"
import { errorMessage, isAuthError } from "../utils/error"
import { readSession, clearSession } from "../utils/auth"
import { useRouter } from "vue-router"

const router = useRouter()

interface Student {
  student_id: string
  student_name: string
  student_no: string
  class_name: string
}

interface Course {
  id: number | string
  course_name: string
  teacher_name: string
  date: string
  time: string
  signed: boolean
  has_active_task: boolean
  task_id: string | null
  cross_signed?: boolean
  cross_source_site?: string | null
  cross_source_site_name?: string | null
  cross_sign_time?: string | null
}

interface AttendanceRecord {
  id: number
  course_name: string
  teacher_name: string
  time: string
  ip: string
  status: number
  status_text: string
  is_script?: number
  is_cross?: number
  source_site?: string | null
  source_site_name?: string | null
}

interface ClassCourse {
  course_id: string
  course_name: string
  time: string | null
  teacher_name: string | null
  task_id: string | null
  start_time: string | null
  end_time: string | null
  task_status: number | null
}

interface ClassRosterItem {
  student_id: string
  student_no: string
  student_name: string
  is_me: boolean
  row_status: Record<string, {
    task_id: string | null
    status: number | null
    status_text: string
    sign_time: string | null
    is_script?: number
    is_cross?: number
    source_site?: string | null
    source_site_name?: string | null
    cross_sign_time?: string | null
  }>
  summary: {
    normal: number
    late: number
    absent: number
    early: number
    sick: number
    leave: number
    unsigned: number
    script?: number
    cross?: number
  }
}

interface ClassAttendance {
  date: string
  class_name: string
  courses: ClassCourse[]
  roster: ClassRosterItem[]
}

const student = ref<Student>({
  student_id: "",
  student_name: "",
  student_no: "",
  class_name: ""
})

const courses = ref<Course[]>([])
const records = ref<AttendanceRecord[]>([])
const loading = ref(false)

// 「刷新」按钮防连点状态：true 时按钮禁用，忽略后续点击
const coursesRefreshing = ref(false)
const classRefreshing = ref(false)

const filterDate = ref(todayDateStr())
const classDate = ref("")
const classAttendance = ref<ClassAttendance>({
  date: "",
  class_name: "",
  courses: [],
  roster: []
})

const toast = ref({ show: false, msg: "", type: "info" })

const WEEKDAYS = ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"]

function todayDateStr(): string {
  const d = new Date()
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, "0")
  const day = String(d.getDate()).padStart(2, "0")
  return `${y}-${m}-${day}`
}

const today = computed<string>(() => {
  const base = todayDateStr()
  const w = WEEKDAYS[new Date().getDay()]
  return `${base} ${w}`
})

const firstName = computed(() =>
  student.value.student_name ? student.value.student_name.substring(0, 1) : "学"
)

function showToast(msg: string, type: "info" | "success" | "error" = "info") {
  toast.value = { show: true, msg, type }
  setTimeout(() => (toast.value.show = false), 2500)
}

/**
 * 判断课程状态
 * 返回值：signed(已签到) | active(签到进行中) | ended(已结束) | not_started(未开始)
 *
 * 判定优先级：
 * 1. 已签到 > 签到进行中 > 已结束 > 未开始
 */
type CourseStatus = "signed" | "cross" | "active" | "ended" | "not_started"

function getCourseStatus(course: Course): CourseStatus {
  if (course.signed) return "signed"
  // 本站没签到，但已从其他站同步回来 → 已在其他网站签到
  if (course.cross_signed) return "cross"
  if (course.has_active_task) return "active"

  // 解析课程时间，判断是否已结束
  const timeStr = course.time || ""
  const match = timeStr.match(/(\d{1,2}):(\d{2})\s*[-~至]\s*(\d{1,2}):(\d{2})/)
  if (match) {
    const endHour = parseInt(match[3], 10)
    const endMinute = parseInt(match[4], 10)
    // 用课程日期构造结束时间
    const dateStr = course.date || todayDateStr()
    const endTime = new Date(`${dateStr}T${String(endHour).padStart(2, "0")}:${String(endMinute).padStart(2, "0")}:00`)
    if (!isNaN(endTime.getTime()) && Date.now() > endTime.getTime()) {
      return "ended"
    }
  }

  return "not_started"
}

/**
 * 课程卡片展示信息
 *
 * 状态与文案只在这里算一次，模板里直接取值，
 * 避免原先每张卡片反复调用 getCourseStatus() 多次
 */
const COURSE_STATUS_META: Record<CourseStatus, {
  badgeClass: string
  badgeText: string
  btnClass: string
  btnText: string
}> = {
  signed: { badgeClass: "badge-ok", badgeText: "已签到", btnClass: "btn-success", btnText: "已签到" },
  cross: { badgeClass: "badge-cyan", badgeText: "已在其他网站签到", btnClass: "btn-disabled", btnText: "已在其他网站签到" },
  active: { badgeClass: "badge-blue", badgeText: "签到进行中", btnClass: "btn-primary", btnText: "立即签到" },
  ended: { badgeClass: "badge-off", badgeText: "已结束", btnClass: "btn-disabled", btnText: "已结束" },
  not_started: { badgeClass: "badge-off", badgeText: "未开始", btnClass: "btn-disabled", btnText: "未开始" }
}

const courseCards = computed(() =>
  courses.value.map(course => {
    const status = getCourseStatus(course)
    const card = { course, status, ...COURSE_STATUS_META[status] }

    // 已在其他网站签到时，把来源站点补进徽标文案
    if (status === "cross" && course.cross_source_site_name) {
      card.badgeText = `已在${course.cross_source_site_name}签到`
      card.btnText = `已在${course.cross_source_site_name}签到`
    }

    return card
  })
)

/**
 * 脚本签到统一用红色 badge-danger 样式展示
 * 后端已将 status_text 改为"脚本签到"，这里只负责样式
 */
function cellBadgeClass(cell?: { is_script?: number; is_cross?: number; status?: number | null } | null): string {
  if (cell && Number(cell.is_script) === 1) {
    return "badge-danger"
  }
  // 已在其他网站签到：与「我的记录」里一致，用青色标识来源
  if (cell && Number(cell.is_cross) === 1) {
    return "badge-cyan"
  }
  return statusBadgeClass(cell?.status || 0)
}

const CN_NUMS = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十",
  "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十"]
function toChineseNum(n: number): string {
  return n >= 0 && n < CN_NUMS.length ? CN_NUMS[n] : String(n)
}

function logout() {
  if (!window.confirm("确认退出登录？")) return
  localStorage.removeItem("user")
  localStorage.removeItem("access_token")
  router.replace("/login")
}

/**
 * 初始化学生信息
 *
 * 返回 true 表示本地登录态可用，可以继续拉取数据；
 * 返回 false 表示登录态不通过（已跳转登录页），调用方不要再去请求接口。
 *
 * 之所以要有返回值：原先 onMounted 里调用本函数后并不检查结果，
 * 本函数内部的 return 也拦不住 onMounted 后面的代码，于是登录态缺失或
 * 令牌过期时仍会照常发出 courses / records / class-attendance 三个请求，
 * 每次都在后端白打三个 401（日志噪音，也会抬高同 IP 的爬虫计数）。
 */
function initStudent(): boolean {
  const session = readSession()
  if (!session) {
    router.replace("/login")
    return false
  }
  if (Number(session.role) !== 1) {
    clearSession()
    router.replace("/login")
    return false
  }
  student.value = {
    student_id: session.student_id || "",
    student_name: session.student_name || "",
    student_no: session.student_no || "",
    class_name: session.class_name || ""
  }
  return true
}

async function getCourses() {
  try {
    const res = await request.get("/api/student/courses")
    if (res.data.code === 200) {
      const payload = res.data.data
      if (payload) {
        student.value = {
          student_id: payload.student_id || "",
          student_name: payload.student_name || "",
          student_no: payload.student_no || "",
          class_name: payload.class_name || ""
        }
        const userCache = localStorage.getItem("user")
        if (userCache) {
          try {
            const user = JSON.parse(userCache)
            Object.assign(user, student.value)
            localStorage.setItem("user", JSON.stringify(user))
          } catch {
            /* ignore */
          }
        }
        courses.value = (payload.courses || []).map((c: any) => ({
          id: c.id,
          course_name: c.name,
          teacher_name: c.teacher_name,
          date: c.date || todayDateStr(),
          time: c.time || "",
          signed: !!c.signed,
          has_active_task: !!c.has_active_task,
          task_id: c.task_id || null,
          cross_signed: !!c.cross_signed,
          cross_source_site: c.cross_source_site || null,
          cross_source_site_name: c.cross_source_site_name || null,
          cross_sign_time: c.cross_sign_time || null
        }))
      }
    }
  } catch (error: unknown) {
    if (isAuthError(error)) {
      localStorage.removeItem("user")
      localStorage.removeItem("access_token")
      router.replace("/login")
      return
    }
    showToast(errorMessage(error, "课程加载失败"), "error")
  }
}

async function getRecords() {
  try {
    const params: Record<string, string> = {}
    if (filterDate.value) params.date = filterDate.value
    const res = await request.get("/api/student/records", { params })
    if (res.data.code === 200) {
      records.value = (res.data.data || []).map((r: any) => ({
        id: r.id,
        course_name: r.course_name,
        teacher_name: r.teacher_name,
        time: r.sign_time,
        ip: r.ip,
        status: r.status,
        status_text: r.status_text,
        is_script: r.is_script,
        is_cross: Number(r.is_cross) || 0,
        source_site: r.source_site || null,
        source_site_name: r.source_site_name || null
      }))
    }
  } catch (error: unknown) {
    if (isAuthError(error)) {
      localStorage.removeItem("user")
      localStorage.removeItem("access_token")
      router.replace("/login")
      return
    }
    showToast(errorMessage(error, "记录加载失败"), "error")
  }
}

function clearDateFilter() {
  filterDate.value = ""
  getRecords()
}

async function getClassAttendance() {
  try {
    const params: Record<string, string> = {}
    if (classDate.value) params.date = classDate.value
    const res = await request.get("/api/student/class-attendance", { params })
    if (res.data.code === 200 && res.data.data) {
      classAttendance.value = {
        date: res.data.data.date || "",
        class_name: res.data.data.class_name || "",
        courses: res.data.data.courses || [],
        roster: res.data.data.roster || []
      }
    } else {
      classAttendance.value = { date: "", class_name: "", courses: [], roster: [] }
    }
  } catch (error: unknown) {
    if (isAuthError(error)) {
      localStorage.removeItem("user")
      localStorage.removeItem("access_token")
      router.replace("/login")
      return
    }
    showToast(errorMessage(error, "班级签到情况加载失败"), "error")
  }
}

function resetClassDate() {
  classDate.value = ""
  getClassAttendance()
}

/**
 * 「刷新」按钮防连点
 *
 * 「刷新」按钮很容易被连续点击，短时间内会给后端重复发起大量相同请求，
 * 既造成无谓压力，也会把正常用户推到后端 BURST 爬虫阈值以上。
 *
 * 处理方式：
 *   1. 请求进行中：禁用按钮并忽略后续点击，避免并发重复请求
 *   2. 请求结束后的冷却时间内：连点同样被忽略，避免接口很快返回后
 *      被继续连点造成请求风暴
 *
 * 注意：仅用于用户点击刷新按钮；签到完成后的内部刷新仍直接调用
 * getCourses / getClassAttendance，不受冷却影响。
 */
const REFRESH_COOLDOWN = 3000

async function withRefreshGuard(flag: Ref<boolean>, task: () => Promise<void>) {
  if (flag.value) return
  flag.value = true
  try {
    await task()
  } finally {
    setTimeout(() => (flag.value = false), REFRESH_COOLDOWN)
  }
}

function refreshCourses() {
  return withRefreshGuard(coursesRefreshing, getCourses)
}

function refreshClassAttendance() {
  return withRefreshGuard(classRefreshing, getClassAttendance)
}

/**
 * 日期控件：点击任意位置直接弹出系统日期选择面板
 *
 * 原生行为是「点文本区域只聚焦单个年/月/日字段」，
 * 这里统一改为弹出面板，避免还要再点一次右侧图标。
 */
function openDatePicker(event: MouseEvent) {
  const el = event.currentTarget as HTMLInputElement
  if (typeof el.showPicker !== "function") return
  // 阻止原生的字段聚焦行为，避免与 showPicker 冲突
  event.preventDefault()
  try {
    el.showPicker()
  } catch {
    /* 浏览器拒绝调用时自动回退到原生行为 */
  }
}

async function signIn(course: Course) {
  const status = getCourseStatus(course)
  if (loading.value || status === "signed" || status === "cross" || status === "ended" || status === "not_started") return
  loading.value = true
  try {
    let location = ""
    if (navigator.geolocation) {
      try {
        const geoPos: any = await new Promise((resolve, reject) => {
          navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 3000 })
        })
        location = `${geoPos.coords.latitude},${geoPos.coords.longitude}`
      } catch {
        /* ignore geo error */
      }
    }

    // 浏览器自动化指纹检测（selenium / puppeteer / playwright / headless）
    // 命中特征则 client_fp 非空，后端识别后标记为"脚本签到"红色 badge
    let client_fp = ""
    try {
      client_fp = await collectBrowserFingerprint()
    } catch {
      /* ignore fp error - 不影响签到主流程 */
    }

    const res = await request.post("/api/student/signin", {
      course_id: course.id,
      device_id: getDeviceId(),
      location,
      client_fp
    })
    if (res.data.code === 200) {
      course.signed = true
      showToast(res.data.message || "签到成功", "success")
      await getRecords()
      await getClassAttendance()
    } else {
      showToast(res.data.message || "签到失败", "error")
    }
  } catch (error: unknown) {
    showToast(errorMessage(error, "签到失败"), "error")
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  // 没有登录态时直接结束，不再发出下面三个必然 401 的请求
  if (!initStudent()) return
  await getCourses()
  await getRecords()
  await getClassAttendance()
})
</script>

<style scoped>
/* ==========================================================================
   学生端视觉重设计
   - 设计语言：靛蓝渐变主色 + 玻璃拟态导航 + 柔和多层阴影 + 大圆角
   - 所有 class 与模板一一对应，交互逻辑零改动
   ========================================================================== */
.student-page {
  /* 主色（靛蓝 → 紫罗兰） */
  --brand-1: #4f46e5;
  --brand-2: #7c3aed;
  --brand-soft: #eef1ff;
  --brand-soft-2: #e0e6ff;

  /* 状态色 */
  --ok: #10b981;
  --ok-deep: #047857;
  --warn-deep: #b45309;
  --danger: #ef4444;
  --danger-deep: #b91c1c;
  --cyan: #0e7490;
  --purple: #a21caf;

  /* 中性色 */
  --ink-900: #0f172a;
  --ink-800: #1e293b;
  --ink-700: #334155;
  --ink-500: #64748b;
  --ink-400: #94a3b8;
  --ink-300: #cbd5e1;
  --line: #e6eaf2;
  --line-soft: #f1f4f9;
  --surface: #ffffff;
  --page-bg: #f5f7fb;

  /* 尺寸与阴影 */
  --r-card: 18px;
  --r-item: 14px;
  --shadow-1: 0 1px 2px rgba(15, 23, 42, 0.04), 0 12px 28px -20px rgba(15, 23, 42, 0.28);
  --shadow-2: 0 18px 34px -22px rgba(79, 70, 229, 0.45);
  --ease: cubic-bezier(0.2, 0.8, 0.3, 1);

  min-height: 100vh;
  padding-bottom: 40px;
  box-sizing: border-box;
  /* 强制浅色配色，保证原生日期下拉面板始终是浅色 */
  color-scheme: light;
  background-color: var(--page-bg);
  background-image:
    radial-gradient(900px 480px at 6% -10%, #e9edff 0%, rgba(233, 237, 255, 0) 62%),
    radial-gradient(720px 420px at 104% -4%, #e6f8f2 0%, rgba(230, 248, 242, 0) 58%);
  background-repeat: no-repeat;
  background-attachment: fixed;
  color: var(--ink-900);
  /* 覆盖全局 #app 的 text-align: center，避免表格内容被居中 */
  text-align: left;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
    "Microsoft YaHei", sans-serif;
  -webkit-font-smoothing: antialiased;
}

/* ===== 顶部导航 ===== */
.topbar {
  position: sticky;
  top: 0;
  z-index: 30;
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(14px) saturate(180%);
  -webkit-backdrop-filter: blur(14px) saturate(180%);
  border-bottom: 1px solid rgba(226, 232, 240, 0.9);
}

.topbar-inner {
  max-width: 1120px;
  margin: 0 auto;
  height: 68px;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.brand-icon {
  width: 40px;
  height: 40px;
  flex-shrink: 0;
  border-radius: 13px;
  background: linear-gradient(135deg, var(--brand-1), var(--brand-2));
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 17px;
  font-weight: 700;
  box-shadow: 0 10px 20px -10px rgba(79, 70, 229, 0.85);
  transition: transform 0.3s var(--ease), box-shadow 0.3s var(--ease);
}

.brand-icon:hover {
  transform: rotate(-6deg) scale(1.06);
  box-shadow: 0 14px 24px -10px rgba(79, 70, 229, 0.95);
}

.brand-text {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.brand-text h1 {
  /* 覆盖全局 h1 的 56px 字号与 32px 外边距，否则会撑破顶栏高度 */
  margin: 0;
  font-size: 17px;
  font-weight: 700;
  color: var(--ink-900);
  line-height: 1.25;
  letter-spacing: 0.3px;
}

.brand-text span {
  font-size: 11px;
  color: var(--ink-400);
  letter-spacing: 1.2px;
  text-transform: uppercase;
}

.user-chip {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 5px 7px 5px 5px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid var(--line);
  border-radius: 999px;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
}

.user-avatar {
  width: 34px;
  height: 34px;
  flex-shrink: 0;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--brand-1), var(--brand-2));
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  box-shadow: 0 6px 14px -8px rgba(79, 70, 229, 0.9);
}

.user-info {
  display: flex;
  flex-direction: column;
  line-height: 1.25;
  min-width: 0;
}

.user-name {
  font-size: 13.5px;
  font-weight: 600;
  color: var(--ink-900);
}

.user-no {
  font-size: 11.5px;
  color: var(--ink-400);
  font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
}

/* ===== 主内容 ===== */
.main {
  max-width: 1120px;
  margin: 26px auto 0;
  padding: 0 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--r-card);
  box-shadow: var(--shadow-1);
  padding: 24px;
  transition: box-shadow 0.3s var(--ease), border-color 0.3s var(--ease);
  animation: card-rise 0.5s var(--ease) both;
}

.card:nth-child(1) { animation-delay: 0.02s; }
.card:nth-child(2) { animation-delay: 0.08s; }
.card:nth-child(3) { animation-delay: 0.14s; }
.card:nth-child(4) { animation-delay: 0.2s; }

.card:hover {
  box-shadow: var(--shadow-2);
}

@keyframes card-rise {
  from {
    opacity: 0;
    transform: translateY(14px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 14px;
  flex-wrap: wrap;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.card-icon {
  width: 38px;
  height: 38px;
  flex-shrink: 0;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--brand-1);
  background: linear-gradient(135deg, var(--brand-soft), var(--brand-soft-2));
  box-shadow: inset 0 0 0 1px rgba(79, 70, 229, 0.12);
}

.card-icon svg {
  width: 19px;
  height: 19px;
}

.card-head h2 {
  font-size: 17px;
  font-weight: 700;
  color: var(--ink-900);
  letter-spacing: 0.2px;
  line-height: 1.3;
  margin: 0;
}

.card-sub {
  font-size: 12.5px;
  color: var(--ink-500);
  margin-top: 3px;
}

/* ===== 个人信息卡（渐变横幅） ===== */
.profile-card {
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  gap: 22px;
  padding: 26px 28px;
  border: none;
  color: #fff;
  background: linear-gradient(118deg, #4338ca 0%, #4f46e5 46%, #6d28d9 100%);
  box-shadow: 0 26px 50px -26px rgba(67, 56, 202, 0.7);
}

/* 右上角柔光 */
.profile-card::before {
  content: "";
  position: absolute;
  top: -240px;
  right: -120px;
  width: 440px;
  height: 440px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.3) 0%, rgba(255, 255, 255, 0) 66%);
  pointer-events: none;
}

/* 左下角网格纹理 */
.profile-card::after {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.07) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.07) 1px, transparent 1px);
  background-size: 24px 24px;
  -webkit-mask-image: linear-gradient(115deg, #000 0%, transparent 68%);
  mask-image: linear-gradient(115deg, #000 0%, transparent 68%);
}

.profile-avatar {
  position: relative;
  z-index: 1;
  width: 76px;
  height: 76px;
  flex-shrink: 0;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30px;
  font-weight: 600;
  color: #fff;
  background: rgba(255, 255, 255, 0.18);
  border: 1px solid rgba(255, 255, 255, 0.35);
  box-shadow:
    0 0 0 7px rgba(255, 255, 255, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.45);
  backdrop-filter: blur(4px);
}

.profile-detail {
  position: relative;
  z-index: 1;
  min-width: 0;
}

.profile-detail h2 {
  font-size: 24px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 0.6px;
  line-height: 1.25;
  margin: 0;
}

.profile-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 12px;
  flex-wrap: wrap;
}

.meta-item {
  display: inline-flex;
  align-items: center;
  padding: 5px 13px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.94);
  background: rgba(255, 255, 255, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.22);
}

.meta-label {
  font-size: 11.5px;
  margin-right: 7px;
  color: rgba(255, 255, 255, 0.66);
}

/* 横幅内用 chip 分隔，隐藏圆点 */
.profile-card .meta-dot {
  display: none;
}

.meta-dot {
  color: var(--ink-300);
}

/* ===== 今日课程 ===== */
.course-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(310px, 1fr));
  gap: 16px;
}

.course-card {
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 18px 18px 18px 21px;
  border: 1px solid var(--line);
  border-radius: var(--r-item);
  background: linear-gradient(180deg, #fff 0%, #fbfcff 100%);
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
  transition: transform 0.25s var(--ease), box-shadow 0.25s var(--ease),
    border-color 0.25s var(--ease);
  min-width: 0;
}

/* 左侧状态色条 */
.course-card::before {
  content: "";
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: var(--stripe, var(--ink-300));
  transition: width 0.25s var(--ease);
}

.course-card:hover {
  transform: translateY(-3px);
  border-color: #dfe5f2;
  box-shadow: 0 18px 30px -20px rgba(15, 23, 42, 0.45);
}

.course-card:hover::before {
  width: 6px;
}

.course-card.status-signed {
  --stripe: var(--ok);
  background: linear-gradient(180deg, #fff 0%, #f6fdfa 100%);
}

.course-card.status-active {
  --stripe: var(--brand-1);
  background: linear-gradient(180deg, #fff 0%, #f7f8ff 100%);
}

.course-card.status-cross {
  --stripe: var(--cyan);
  background: linear-gradient(180deg, #fff 0%, #f2fbfd 100%);
}

.course-card.status-ended,
.course-card.status-not_started {
  --stripe: var(--ink-300);
}

.course-main {
  min-width: 0;
  flex: 1;
}

.course-main h3 {
  font-size: 15.5px;
  font-weight: 650;
  color: var(--ink-900);
  line-height: 1.4;
  margin-bottom: 8px;
  word-break: break-word;
}

.course-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 12.5px;
  color: var(--ink-500);
}

.course-status {
  margin-top: 12px;
}

.course-action {
  flex-shrink: 0;
}

.course-action .btn {
  min-width: 100px;
}

/* ===== 徽章 ===== */
.badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 11px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  line-height: 1.45;
  white-space: nowrap;
  border: 1px solid transparent;
}

/* 统一用同色小圆点打头，状态识别更快 */
.badge::before {
  content: "";
  width: 6px;
  height: 6px;
  flex-shrink: 0;
  border-radius: 50%;
  background: currentColor;
  opacity: 0.8;
}

.badge-ok { background: #e7f8f1; color: var(--ok-deep); border-color: rgba(16, 185, 129, 0.2); }
.badge-blue { background: #e8edff; color: #1d4ed8; border-color: rgba(79, 70, 229, 0.2); }
.badge-warn { background: #fff5e6; color: var(--warn-deep); border-color: rgba(245, 158, 11, 0.22); }
.badge-danger { background: #fdecec; color: var(--danger-deep); border-color: rgba(239, 68, 68, 0.22); }
.badge-purple { background: #f7edfe; color: var(--purple); border-color: rgba(162, 28, 175, 0.18); }
.badge-cyan { background: #e5f7fb; color: var(--cyan); border-color: rgba(14, 116, 144, 0.18); }
.badge-gray { background: #eef1f6; color: #475569; border-color: rgba(71, 85, 105, 0.14); }
.badge-unsigned { background: #f2f5f9; color: #64748b; border-color: rgba(100, 116, 139, 0.16); }
.badge-off { background: #f4f6fa; color: var(--ink-400); border-color: rgba(148, 163, 184, 0.2); }

.text-muted { color: var(--ink-400); }

/* ===== 按钮 ===== */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 9px 18px;
  border: none;
  border-radius: 11px;
  font-size: 13.5px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  white-space: nowrap;
  transition: transform 0.16s var(--ease), box-shadow 0.24s var(--ease),
    background 0.24s var(--ease), color 0.24s var(--ease), border-color 0.24s var(--ease);
}

.btn:focus-visible {
  outline: none;
  box-shadow: 0 0 0 2px #fff, 0 0 0 4px rgba(99, 102, 241, 0.45);
}

.btn:active {
  transform: scale(0.975);
}

.btn-primary {
  color: #fff;
  background: linear-gradient(135deg, var(--brand-1), var(--brand-2));
  box-shadow: 0 10px 20px -10px rgba(79, 70, 229, 0.9);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 16px 26px -12px rgba(79, 70, 229, 0.95);
}

.btn-success {
  color: #fff;
  background: linear-gradient(135deg, #10b981, #059669);
  box-shadow: 0 10px 20px -10px rgba(5, 150, 105, 0.85);
}

.btn-success:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 16px 26px -12px rgba(5, 150, 105, 0.9);
}

.btn-disabled {
  background: #f1f4f9;
  color: var(--ink-400);
  cursor: not-allowed;
  box-shadow: none;
}

.btn:disabled {
  cursor: not-allowed;
  opacity: 0.85;
}

.btn-soft {
  background: var(--brand-soft);
  color: #4338ca;
  border: 1px solid rgba(79, 70, 229, 0.1);
}

.btn-soft:hover:not(:disabled) {
  background: var(--brand-soft-2);
}

.btn-ghost {
  background: transparent;
  color: var(--ink-500);
}

.btn-ghost:hover {
  background: #fdecec;
  color: var(--danger-deep);
}

.btn-sm {
  padding: 7px 14px;
  font-size: 12.5px;
  border-radius: 10px;
}

/* ===== 筛选栏 & 日期下拉（重点美化） ===== */
.filter-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px;
  background: #f7f8fc;
  border: 1px solid var(--line);
  border-radius: 14px;
}

.form-input {
  padding: 8px 12px;
  border: 1px solid var(--line);
  border-radius: 10px;
  font-size: 13px;
  font-family: inherit;
  background: #fff;
  color: var(--ink-700);
  box-sizing: border-box;
  transition: border-color 0.2s var(--ease), box-shadow 0.2s var(--ease),
    background 0.2s var(--ease);
}

.form-input:focus {
  outline: none;
  border-color: #818cf8;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.18);
}

/* —— 日期选择器：去掉原生外观，换成定制的日历图标与交互 ——
   点击控件任意位置都会弹出日期面板（见 script 中的 openDatePicker） */
input[type="date"].form-input {
  appearance: none;
  -webkit-appearance: none;
  height: 34px;
  padding: 0 6px 0 11px;
  display: inline-flex;
  align-items: center;
  font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  font-size: 12.5px;
  font-weight: 600;
  letter-spacing: 0.3px;
  color: var(--ink-700);
  background: #fff;
  cursor: pointer;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
}

input[type="date"].form-input:hover {
  border-color: #c7d2fe;
  background: #fdfdff;
}

/* 内部年月日字段 */
input[type="date"].form-input::-webkit-datetime-edit {
  padding: 0;
}

input[type="date"].form-input::-webkit-datetime-edit-fields-wrapper {
  padding: 0;
}

input[type="date"].form-input::-webkit-datetime-edit-text {
  color: var(--ink-300);
  padding: 0 1px;
}

input[type="date"].form-input::-webkit-datetime-edit-year-field,
input[type="date"].form-input::-webkit-datetime-edit-month-field,
input[type="date"].form-input::-webkit-datetime-edit-day-field {
  padding: 2px 3px;
  border-radius: 5px;
  color: var(--ink-700);
  font-weight: 600;
  transition: background 0.15s var(--ease), color 0.15s var(--ease);
}

/* 面板展开后正在编辑的字段高亮 */
input[type="date"].form-input::-webkit-datetime-edit-year-field:focus,
input[type="date"].form-input::-webkit-datetime-edit-month-field:focus,
input[type="date"].form-input::-webkit-datetime-edit-day-field:focus {
  outline: none;
  background: var(--brand-soft);
  color: #4338ca;
}

/* 下拉触发按钮：替换为定制日历图标 */
input[type="date"].form-input::-webkit-calendar-picker-indicator {
  width: 20px;
  height: 20px;
  margin-left: 4px;
  padding: 3px;
  flex-shrink: 0;
  border-radius: 7px;
  cursor: pointer;
  background-color: var(--brand-soft);
  background-image: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%20fill='none'%20stroke='%234f46e5'%20stroke-width='2'%20stroke-linecap='round'%20stroke-linejoin='round'%3E%3Crect%20x='3'%20y='4.5'%20width='18'%20height='16'%20rx='3'/%3E%3Cpath%20d='M8%202.5v4M16%202.5v4M3%2010h18'/%3E%3C/svg%3E");
  background-size: 13px 13px;
  background-position: center;
  background-repeat: no-repeat;
  opacity: 1;
  transition: background-color 0.2s var(--ease), transform 0.2s var(--ease);
}

input[type="date"].form-input:hover::-webkit-calendar-picker-indicator {
  background-color: var(--brand-soft-2);
  transform: scale(1.08);
}

input[type="date"].form-input:focus::-webkit-calendar-picker-indicator {
  background-color: var(--brand-1);
  background-image: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%20fill='none'%20stroke='%23ffffff'%20stroke-width='2'%20stroke-linecap='round'%20stroke-linejoin='round'%3E%3Crect%20x='3'%20y='4.5'%20width='18'%20height='16'%20rx='3'/%3E%3Cpath%20d='M8%202.5v4M16%202.5v4M3%2010h18'/%3E%3C/svg%3E");
}

/* 隐藏多余的原生控件，保持界面干净 */
input[type="date"].form-input::-webkit-inner-spin-button,
input[type="date"].form-input::-webkit-clear-button {
  display: none;
}

/* ===== 表格 ===== */
.table-wrap {
  overflow-x: auto;
  border: 1px solid var(--line);
  border-radius: var(--r-item);
  background: #fff;
}

/* 横向滚动条美化（班级签到表列较多时会用到） */
.table-wrap::-webkit-scrollbar {
  height: 8px;
}

.table-wrap::-webkit-scrollbar-track {
  background: #f7f8fc;
}

.table-wrap::-webkit-scrollbar-thumb {
  background: #d7dded;
  border-radius: 4px;
}

.table-wrap::-webkit-scrollbar-thumb:hover {
  background: var(--ink-400);
}

.data-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 13.5px;
  text-align: left;
}

.data-table th {
  text-align: left;
  padding: 12px 16px;
  background: #f8fafd;
  color: var(--ink-500);
  font-weight: 600;
  font-size: 12.5px;
  letter-spacing: 0.4px;
  white-space: nowrap;
  border-bottom: 1px solid var(--line);
}

.data-table td {
  padding: 13px 16px;
  text-align: left;
  border-bottom: 1px solid var(--line-soft);
  color: var(--ink-700);
}

.data-table tbody tr {
  transition: background 0.18s var(--ease);
}

/* 隔行极浅底，长表格更容易横向对齐阅读 */
.data-table tbody tr:nth-child(even) {
  background: #fcfdff;
}

.data-table tbody tr:hover {
  background: #f6f8ff;
}

.data-table tbody tr:last-child td {
  border-bottom: none;
}

.cell-strong {
  font-weight: 600;
  color: var(--ink-900);
}

.mono {
  font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  font-size: 12.5px;
  color: var(--ink-500);
}

.empty-cell {
  text-align: center;
  color: var(--ink-400);
  padding: 34px 16px;
}

/* 空状态：干净的白底描边面板，文字垂直居中（参考签到名册的空态样式） */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  min-height: 180px;
  padding: 32px 24px;
  text-align: center;
  font-size: 14px;
  color: #475569;
  background: #fcfdff;
  border: 1px solid var(--line);
  border-radius: var(--r-item);
}

/* ===== 班级签到情况 ===== */
.class-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 16px;
  padding: 10px 14px;
  font-size: 12.5px;
  color: var(--ink-500);
  background: #f8fafd;
  border: 1px solid var(--line);
  border-radius: 11px;
}

.class-table th,
.class-table td {
  text-align: center;
}

.class-table .col-student { white-space: nowrap; text-align: center; }
.class-table .col-name { white-space: nowrap; min-width: 88px; text-align: center; }
.class-table .col-course { min-width: 112px; text-align: center; }
.class-table .col-summary { min-width: 168px; text-align: center; }

.course-th {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  text-align: center;
}

.course-th-name {
  font-size: 12px;
  font-weight: 600;
  color: var(--ink-700);
}

.course-th-time {
  font-size: 11px;
  color: var(--ink-400);
  font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
}

.class-table td {
  text-align: center;
  font-size: 13px;
}

.row-me {
  background: #f2f5ff !important;
}

.row-me td:first-child {
  box-shadow: inset 3px 0 0 var(--brand-1);
}

.row-me:hover {
  background: #e9eeff !important;
}

.me-tag {
  display: inline-block;
  margin-left: 6px;
  padding: 1.5px 7px;
  border-radius: 999px;
  font-size: 10.5px;
  font-weight: 700;
  color: #fff;
  background: linear-gradient(135deg, var(--brand-1), var(--brand-2));
  vertical-align: middle;
}

.no-task {
  color: var(--ink-300);
  font-size: 12px;
}

.summary-cell {
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: stretch;
  min-width: 150px;
}

.summary-pill {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 5px 10px;
  border-radius: 9px;
  font-size: 12px;
  font-weight: 600;
  text-align: left;
  white-space: nowrap;
  border: 1px solid transparent;
  border-left: 3px solid var(--stripe, var(--ink-300));
  background: #f8fafc;
}

.summary-dot {
  width: 8px;
  height: 8px;
  flex-shrink: 0;
  border-radius: 50%;
  background: currentColor;
}

.summary-text {
  display: flex;
  align-items: center;
  gap: 6px;
  flex: 1;
  min-width: 0;
}

.summary-course {
  font-size: 11px;
  font-weight: 600;
  color: var(--ink-500);
}

.summary-status {
  font-weight: 700;
  color: currentColor;
}

/* 状态色：淡色底 + 左色条 + 同色文字 */
.summary-pill.badge-ok { background: #ecfdf5; color: var(--ok-deep); border-left-color: var(--ok); }
.summary-pill.badge-warn { background: #fffbeb; color: var(--warn-deep); border-left-color: #f59e0b; }
.summary-pill.badge-danger { background: #fef2f2; color: var(--danger-deep); border-left-color: #dc2626; }
.summary-pill.badge-purple { background: #faf5ff; color: var(--purple); border-left-color: #c559f0; }
.summary-pill.badge-cyan { background: #ecfeff; color: var(--cyan); border-left-color: #0891b2; }
.summary-pill.badge-gray { background: #f1f5f9; color: #475569; border-left-color: #64748b; }
.summary-pill.badge-unsigned { background: #f8fafc; color: #64748b; border-left-color: #94a3b8; }
.summary-pill.badge-off { background: #f8fafc; color: #64748b; border-left-color: var(--ink-300); }

/* ===== Toast ===== */
.toast {
  position: fixed;
  top: 86px;
  left: 50%;
  transform: translateX(-50%);
  display: inline-flex;
  align-items: center;
  gap: 9px;
  padding: 12px 22px;
  border-radius: 14px;
  font-size: 13.5px;
  font-weight: 600;
  z-index: 1000;
  border: 1px solid transparent;
  backdrop-filter: blur(12px) saturate(180%);
  -webkit-backdrop-filter: blur(12px) saturate(180%);
  box-shadow: 0 22px 42px -20px rgba(15, 23, 42, 0.5);
}

.toast::before {
  content: "";
  width: 8px;
  height: 8px;
  flex-shrink: 0;
  border-radius: 50%;
  background: currentColor;
}

.toast.info {
  background: rgba(255, 255, 255, 0.96);
  color: var(--ink-900);
  border-color: var(--line);
}

.toast.success {
  background: rgba(236, 253, 245, 0.96);
  color: var(--ok-deep);
  border-color: rgba(16, 185, 129, 0.3);
}

.toast.error {
  background: rgba(254, 242, 242, 0.96);
  color: var(--danger-deep);
  border-color: rgba(239, 68, 68, 0.3);
}

.toast-enter-active,
.toast-leave-active {
  transition: opacity 0.2s var(--ease), transform 0.2s var(--ease);
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-10px);
}

/* ===== 响应式 ===== */
@media (max-width: 900px) {
  .main {
    margin-top: 20px;
    padding: 0 16px;
    gap: 16px;
  }

  .topbar-inner {
    padding: 0 16px;
  }

  .card {
    padding: 18px;
  }

  .course-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 700px) {
  .brand-text span {
    display: none;
  }

  .user-info {
    display: none;
  }

  .user-chip {
    gap: 6px;
  }

  .card-head {
    align-items: stretch;
  }

  .filter-bar {
    width: 100%;
    flex-wrap: wrap;
  }

  .filter-bar .form-input {
    flex: 1;
    min-width: 0;
  }

  .filter-bar .btn {
    flex: 1;
  }

  .profile-card {
    flex-direction: column;
    text-align: center;
    gap: 16px;
    padding: 24px 20px;
  }

  .profile-meta {
    justify-content: center;
  }

  .course-card {
    flex-direction: column;
    align-items: stretch;
    gap: 14px;
  }

  .course-action,
  .course-action .btn {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .card {
    padding: 15px;
    border-radius: 16px;
  }

  .card-icon {
    width: 34px;
    height: 34px;
  }

  .data-table th,
  .data-table td {
    padding: 10px 12px;
  }

  .profile-detail h2 {
    font-size: 21px;
  }

  .toast {
    top: 78px;
    max-width: calc(100vw - 32px);
  }
}

@media (prefers-reduced-motion: reduce) {
  * {
    transition: none !important;
    animation: none !important;
  }

  .btn:active,
  .brand-icon:hover,
  .course-card:hover {
    transform: none !important;
  }
}
</style>