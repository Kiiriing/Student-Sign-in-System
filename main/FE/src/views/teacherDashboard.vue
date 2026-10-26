<template>
  <div class="teacher-page">
    <!-- ================= 侧边导航 ================= -->
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M22 10L12 5 2 10l10 5 10-5z" />
            <path d="M6 12v5c0 1.7 2.7 3 6 3s6-1.3 6-3v-5" />
          </svg>
        </div>
        <div class="brand-text">
          <div class="brand-name">学生签到系统</div>
          <div class="brand-sub">教师工作台</div>
        </div>
      </div>

      <nav class="nav" aria-label="教师导航">
        <button type="button" class="nav-item" :class="{ active: activeTab === 'courses' }" @click="activeTab = 'courses'">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
          </svg>
          <span>我的课程</span>
        </button>

        <button type="button" class="nav-item" :class="{ active: activeTab === 'tasks' }" @click="switchTab('tasks')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <rect x="3" y="4" width="18" height="18" rx="2" />
            <line x1="16" y1="2" x2="16" y2="6" />
            <line x1="8" y1="2" x2="8" y2="6" />
            <line x1="3" y1="10" x2="21" y2="10" />
          </svg>
          <span>签到任务</span>
        </button>

        <button type="button" class="nav-item" :class="{ active: activeTab === 'roster' }" @click="activeTab = 'roster'">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
            <circle cx="9" cy="7" r="4" />
            <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
            <path d="M16 3.13a4 4 0 0 1 0 7.75" />
          </svg>
          <span>签到名册</span>
        </button>

        <button type="button" class="nav-item" :class="{ active: activeTab === 'rollcall' }" @click="switchTab('rollcall')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M3 11l18-5v12L3 14v-3z" />
            <path d="M11.6 16.8a3 3 0 1 1-5.8-1.6" />
          </svg>
          <span>课堂点名</span>
        </button>

        <button type="button" class="nav-item" :class="{ active: activeTab === 'stats' }" @click="switchTab('stats')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <line x1="18" y1="20" x2="18" y2="10" />
            <line x1="12" y1="20" x2="12" y2="4" />
            <line x1="6" y1="20" x2="6" y2="14" />
          </svg>
          <span>统计分析</span>
        </button>
      </nav>

      <div class="sidebar-footer">
        <button type="button" class="nav-item logout-item" @click="logout">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
            <polyline points="16 17 21 12 16 7" />
            <line x1="21" y1="12" x2="9" y2="12" />
          </svg>
          <span>退出登录</span>
        </button>
      </div>
    </aside>

    <!-- ================= 主区域 ================= -->
    <div class="main">
      <header class="topbar">
        <div class="topbar-titles">
          <h1>{{ tabMeta[activeTab].title }}</h1>
          <p>{{ tabMeta[activeTab].desc }}</p>
        </div>
        <div class="topbar-right">
          <div class="teacher-chip">
            <div class="teacher-avatar">{{ teacherInitial }}</div>
            <div class="teacher-meta">
              <div class="teacher-name">{{ teacherName }}</div>
              <div class="teacher-role">任课教师</div>
            </div>
          </div>
        </div>
      </header>

      <main class="content">
        <div v-if="pageLoading" class="state-card">
          <div class="spinner" aria-hidden="true"></div>
          <p>数据加载中，请稍候…</p>
        </div>

        <div v-else-if="pageError" class="state-card state-error">
          <p>{{ pageError }}</p>
          <button type="button" class="btn btn-primary" @click="loadAll">重新加载</button>
        </div>

        <template v-else>
          <!-- ================= 我的课程 ================= -->
          <section v-show="activeTab === 'courses'">
            <div class="card panel-card">
              <div class="panel-header">
                <h2>授课课程</h2>
                <button type="button" class="btn btn-secondary btn-sm" @click="fetchCourses">刷新</button>
              </div>
              <div v-if="groupedCourses.length === 0" class="empty-block">最近三天暂无授课课程</div>
              <div v-else class="course-day-list">
                <div v-for="g in groupedCourses" :key="g.key" class="course-day-group">
                  <div class="course-day-header">
                    <span class="course-day-date">{{ g.label }}</span>
                    <span class="course-day-count">共 {{ g.items.length }} 节</span>
                  </div>
                  <div class="course-grid">
                    <div v-for="c in g.items" :key="c.id" class="course-card">
                      <div class="course-card-head">
                        <div class="course-name">{{ c.name }}</div>
                        <span class="course-class">{{ c.class_name }}</span>
                      </div>
                      <div class="course-meta">
                        <span v-if="c.time">时段：<span class="mono">{{ c.time }}</span></span>
                      </div>
                      <div class="course-actions">
                        <button
                          v-if="isTaskStartedToday(c.id)"
                          type="button"
                          class="btn btn-disabled btn-sm"
                          @click="showToast('该课程今天已发起过签到，请勿重复发起', 'error')"
                        >已发起签到</button>
                        <button
                          v-else
                          type="button"
                          class="btn btn-primary btn-sm"
                          @click="openCreateTask(c)"
                        >发起签到</button>
                        <button type="button" class="btn btn-secondary btn-sm" @click="viewCourseTasks(c)">查看签到记录</button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <!-- ================= 签到任务 ================= -->
          <section v-show="activeTab === 'tasks'">
            <div class="card panel-card">
              <div class="panel-header">
                <h2>签到任务</h2>
                <div class="filter-row">
                  <CustomSelect v-model="taskFilter.course_name" :options="taskCourseOptions" placeholder="全部课程" class="filter-control" size="sm" @change="fetchTasks" />
                  <input v-model="taskFilter.date" class="form-input form-input-sm filter-control" type="date" @click="openPicker" @change="fetchTasks">
                  <button type="button" class="btn btn-secondary btn-sm" @click="resetTaskFilter">重置</button>
                </div>
              </div>
              <div class="table-wrap">
                <table class="data-table">
                  <thead>
                    <tr>
                      <th>课程</th>
                      <th>班级</th>
                      <th>签到时间段</th>
                      <th>签到进度</th>
                      <th>状态</th>
                      <th class="col-actions">操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="t in tasks" :key="t.task_id">
                      <td class="cell-strong">{{ t.course_name }}</td>
                      <td>{{ t.class_name }}</td>
                      <td><span class="mono">{{ formatDateTime(t.start_time) }} ~ {{ formatDateTime(t.end_time) }}</span></td>
                      <td>{{ t.signed_count }} / {{ t.total_count }} 人</td>
                      <td>
                        <span class="badge" :class="taskStatusClass(t)">
                          {{ taskStatusText(t) }}
                        </span>
                      </td>
                      <td>
                        <div class="row-actions">
                          <button type="button" class="btn btn-sm btn-soft-primary" @click="viewRoster(t.task_id)">查看名册</button>
                          <button
                            v-if="canClose(t)"
                            type="button"
                            class="btn btn-sm btn-soft-warn"
                            @click="closeTask(t)"
                          >结束签到</button>
                          <button
                            v-if="t.status === 0"
                            type="button"
                            class="btn btn-sm btn-soft-danger"
                            @click="deleteTask(t)"
                          >删除</button>
                        </div>
                      </td>
                    </tr>
                    <tr v-if="tasks.length === 0">
                      <td colspan="6" class="empty-cell">暂无签到任务</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </section>

          <!-- ================= 签到名册 ================= -->
          <section v-show="activeTab === 'roster'">
            <div v-if="!roster.task" class="state-card">
              <p>请从「签到任务」中选择一个任务查看签到名册</p>
              <button type="button" class="btn btn-primary" @click="activeTab = 'tasks'">前往签到任务</button>
            </div>
            <template v-else>
              <div class="card panel-card">
                <div class="panel-header">
                  <div>
                    <h2>{{ roster.task.course_name }} - {{ roster.task.class_name }}</h2>
                    <p class="panel-sub">
                      签到时间：<span class="mono">{{ formatDateTime(roster.task.start_time) }} ~ {{ formatDateTime(roster.task.end_time) }}</span>
                    </p>
                  </div>
                  <button type="button" class="btn btn-secondary btn-sm" @click="fetchRoster">刷新</button>
                </div>

                <div class="stats-row">
                  <div v-for="s in statusOptions" :key="s.value" class="stat-mini" :class="'stat-' + s.key">
                    <span class="stat-mini-label">{{ s.label }}</span>
                    <span class="stat-mini-num">{{ displayStats[s.value] || 0 }}</span>
                  </div>
                  <div v-if="(roster.stats.cross || 0) > 0" class="stat-mini stat-cross">
                    <span class="stat-mini-label">已在其他网站</span>
                    <span class="stat-mini-num">{{ roster.stats.cross || 0 }}</span>
                  </div>
                  <div class="stat-mini stat-total">
                    <span class="stat-mini-label">合计</span>
                    <span class="stat-mini-num">{{ displayTotal }}</span>
                  </div>
                </div>
              </div>

              <div class="card panel-card">
                <div class="panel-header">
                  <h2>学生签到名单（按学号排序）</h2>
                  <span v-if="duplicateIpCount > 0" class="ip-duplicate-hint">
                    ⚠ 检测到 {{ duplicateIpCount }} 条记录存在相同 IP（疑似代签）
                  </span>
                </div>
                <div class="table-wrap">
                  <table class="data-table">
                    <thead>
                      <tr>
                        <th>学号</th>
                        <th>姓名</th>
                        <th>签到时间</th>
                        <th>IP 地址</th>
                        <th>来源</th>
                        <th>签到状态</th>
                        <th class="col-actions">操作</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="r in roster.roster" :key="r.student_id">
                        <td><span class="mono">{{ r.student_no }}</span></td>
                        <td class="cell-strong">{{ r.student_name }}</td>
                        <td>{{ r.sign_time ? formatDateTime(r.sign_time) : '-' }}</td>
                        <td>
                          <span v-if="r.ip" class="mono"
                            :class="{ 'ip-duplicate': duplicateIpSet.has(r.ip) }"
                            :title="duplicateIpSet.has(r.ip) ? '该 IP 与其他学生重复，疑似代签' : ''">
                            {{ r.ip }}
                          </span>
                          <span v-else>-</span>
                        </td>
                        <td>
                          <span v-if="Number(r.is_cross) === 1" class="badge badge-cyan">
                            {{ r.source_site_name || '其他网站' }}
                          </span>
                          <span v-else>-</span>
                        </td>
                        <td>
                          <span
                            class="badge"
                            :class="Number(r.is_script) === 1 ? 'badge-danger' : (Number(r.is_cross) === 1 ? 'badge-cyan' : statusBadgeClass(r.status))"
                          >{{ r.status_text }}</span>
                        </td>
                        <td>
                          <CustomSelect :model-value="r.status" :options="rosterStatusOptions" size="sm" @change="(value) => changeStatus(r, String(value))" />
                        </td>
                      </tr>
                      <tr v-if="roster.roster.length === 0">
                        <td colspan="7" class="empty-cell">该班级暂无学生</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </template>
          </section>

          <!-- ================= 课堂点名 ================= -->
          <section v-show="activeTab === 'rollcall'">
            <div class="card panel-card">
              <div class="panel-header">
                <h2>课堂点名</h2>
                <div class="filter-row">
                  <CustomSelect v-model="rollcallTaskId" :options="rollcallTaskOptions" placeholder="请选择签到任务" class="filter-control" size="sm" @change="loadRollcallRoster" />
                </div>
              </div>

              <div class="rollcall-controls">
                <button type="button" class="btn btn-primary btn-sm"
                  :disabled="rollcallRunning && !rollcallPaused"
                  @click="startRollcall">开始点名</button>
                <button type="button" class="btn btn-soft-warn btn-sm"
                  v-if="rollcallRunning && !rollcallPaused"
                  @click="pauseRollcall">暂停</button>
                <button type="button" class="btn btn-success btn-sm"
                  v-if="rollcallPaused"
                  @click="resumeRollcall">继续</button>
                <button type="button" class="btn btn-danger btn-sm"
                  v-if="rollcallRunning"
                  @click="stopRollcall">停止</button>

                <span class="rollcall-divider"></span>

                <label class="rollcall-hint rollcall-voice-label">
                  音色：
                  <CustomSelect v-model="selectedVoiceName" :options="voiceOptions" class="rollcall-voice-select" size="sm" @change="onVoiceChange" />
                </label>
                <button type="button" class="btn btn-secondary btn-sm" @click="previewVoice">试听</button>

                <span v-if="!speechSupported" class="rollcall-hint">浏览器不支持语音识别，仅支持朗读 + 手动点击</span>
                <span v-if="rollcallListening" class="rollcall-hint rollcall-listening-hint">正在聆听...</span>
                <span v-if="rollcallPaused" class="rollcall-hint">已暂停，可点击学生名单进行单个点名</span>
              </div>

              <div v-if="rollcallRoster.length === 0" class="empty-block">
                {{ rollcallTaskId ? '该任务无学生名单' : '请先选择签到任务' }}
              </div>
              <div v-else class="rollcall-list">
                <div v-for="(s, i) in rollcallRoster" :key="s.student_id"
                  class="rollcall-item"
                  :class="{
                    'rollcall-current': (i === rollcallIndex && rollcallRunning) || i === manualIndex,
                    'rollcall-answered': s.status === 1,
                    'rollcall-item-locked': rollcallRunning && !rollcallPaused
                  }"
                  @click="manualRollcall(i)">
                  <span class="rollcall-name">{{ s.student_name }}</span>
                  <span class="rollcall-no">{{ s.student_no }}</span>
                  <span class="rollcall-status">
                    <span v-if="s.status === 1" class="badge badge-ok">已签到</span>
                    <template v-else>
                      <span v-if="(i === rollcallIndex || i === manualIndex) && rollcallListening" class="badge badge-blue">聆听中…</span>
                      <span v-else-if="i === rollcallIndex && rollcallRunning && !rollcallPaused" class="badge badge-blue">点名中</span>
                      <span v-else-if="i === rollcallIndex && rollcallRunning" class="badge badge-warn">未应答</span>
                      <span v-else class="badge badge-off">待点名</span>
                      <button type="button" class="btn btn-soft-primary btn-xs rollcall-confirm-btn"
                        title="确认该学生到场"
                        @click="confirmPresent(i, $event)">✓</button>
                    </template>
                  </span>
                </div>
              </div>
            </div>
          </section>

          <!-- ================= 统计分析 ================= -->
          <section v-show="activeTab === 'stats'">
            <div class="card panel-card">
              <div class="panel-header">
                <h2>统计筛选</h2>
                <div class="filter-row">
                  <CustomSelect v-model="statsFilter.course_id" :options="statsCourseSelectOptions" placeholder="全部课程" class="filter-control" size="sm" @change="fetchStats" />
                  <input v-model="statsFilter.date" class="form-input form-input-sm filter-control" type="date" @click="openPicker" @change="fetchStats">
                  <button type="button" class="btn btn-secondary btn-sm" @click="resetStatsFilter">重置</button>
                </div>
              </div>

              <div class="stats-row">
                <div v-for="s in statusOptions.filter(o => o.value !== 7)" :key="s.value" class="stat-mini" :class="'stat-' + s.key">
                  <span class="stat-mini-label">{{ s.label }}</span>
                  <span class="stat-mini-num">{{ stats.summary[s.key as keyof StatsSummary] || 0 }}</span>
                </div>
                <div class="stat-mini stat-total">
                  <span class="stat-mini-label">应到人次</span>
                  <span class="stat-mini-num">{{ stats.summary.total || 0 }}</span>
                </div>
              </div>
            </div>

            <div class="chart-row">
              <div class="card panel-card chart-half">
                <div class="panel-header">
                  <h2>每日签到人数趋势</h2>
                </div>
                <div ref="lineChartRef" class="chart-box"></div>
              </div>
              <div class="card panel-card chart-half">
                <div class="panel-header">
                  <h2>签到状态分布</h2>
                </div>
                <div ref="pieChartRef" class="chart-box"></div>
              </div>
            </div>

            <div class="card panel-card">
              <div class="panel-header">
                <h2>各次签到明细</h2>
              </div>
              <div ref="barChartRef" class="chart-box chart-tall"></div>
            </div>
          </section>
        </template>
      </main>
    </div>

    <!-- ================= 发起签到弹窗 ================= -->
    <div v-if="createTaskModal.show" class="modal-mask" @click.self="closeCreateTask">
      <div class="modal-card" role="dialog" aria-modal="true" aria-labelledby="ct-title">
        <h3 id="ct-title">发起签到</h3>
        <p class="modal-desc">
          为课程 <span class="mono">{{ createTaskModal.course_name }}</span> 设置签到时间段，学生可在该时段内签到，超时未签到记为旷课。
        </p>
        <div class="form-field">
          <label>签到开始时间 <span class="required">*</span></label>
          <div
            class="time-display-box"
            :class="{ 'is-empty': !createTaskModal.start }"
            @click="openTimePicker('start')"
          >
            <span class="time-display-text">{{ fmtTimeDisplay(createTaskModal.start) }}</span>
            <span class="time-display-icon">📅</span>
          </div>
        </div>
        <div class="form-field">
          <label>签到结束时间 <span class="required">*</span></label>
          <div
            class="time-display-box"
            :class="{ 'is-empty': !createTaskModal.end }"
            @click="openTimePicker('end')"
          >
            <span class="time-display-text">{{ fmtTimeDisplay(createTaskModal.end) }}</span>
            <span class="time-display-icon">📅</span>
          </div>
          <p v-if="createTaskModal.error" class="field-error">{{ createTaskModal.error }}</p>
        </div>
        <div class="modal-actions">
          <button type="button" class="btn btn-secondary" @click="closeCreateTask">取消</button>
          <button type="button" class="btn btn-primary" :disabled="createTaskModal.submitting" @click="confirmCreateTask">
            {{ createTaskModal.submitting ? '创建中…' : '发起签到' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ================= 时间选择器弹框 ================= -->
    <div v-if="timePicker.show" class="modal-mask" @click.self="closeTimePicker">
      <div class="modal-card tp-card" role="dialog" aria-modal="true">
        <h3>{{ timePicker.target === 'start' ? '选择签到开始时间' : '选择签到结束时间' }}</h3>

        <!-- 日期选择 -->
        <div class="tp-section">
          <p class="tp-section-title">选择日期</p>
          <div class="tp-date-list">
            <button
              v-for="d in getDateOptions()"
              :key="d.date"
              type="button"
              class="tp-date-item"
              :class="{ 'is-selected': timePicker.tempDate === d.date, 'is-today': d.isToday }"
              @click="selectDate(d.date)"
            >
              <span class="tp-date-label">{{ d.label }}</span>
              <span class="tp-date-weekday">{{ d.weekday }}</span>
              <span v-if="d.isToday" class="tp-date-today-tag">今天</span>
            </button>
          </div>
        </div>

        <!-- 小时选择 -->
        <div class="tp-section">
          <p class="tp-section-title">选择小时</p>
          <div class="tp-hour-grid">
            <button
              v-for="h in 24"
              :key="h - 1"
              type="button"
              class="tp-time-cell"
              :class="{ 'is-selected': timePicker.tempHour === h - 1 }"
              @click="setHour(h - 1)"
            >{{ String(h - 1).padStart(2, '0') }}</button>
          </div>
        </div>

        <!-- 分钟选择 -->
        <div class="tp-section">
          <p class="tp-section-title">选择分钟</p>
          <div class="tp-minute-grid">
            <button
              v-for="m in [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]"
              :key="m"
              type="button"
              class="tp-time-cell"
              :class="{ 'is-selected': timePicker.tempMinute === m }"
              @click="setMinute(m)"
            >{{ String(m).padStart(2, '0') }}</button>
          </div>
        </div>

        <!-- 预览 -->
        <div class="tp-preview">
          当前选择：<span class="tp-preview-value">{{ timePicker.tempDate }} {{ String(timePicker.tempHour).padStart(2, '0') }}:{{ String(timePicker.tempMinute).padStart(2, '0') }}</span>
        </div>

        <div class="modal-actions">
          <button type="button" class="btn btn-secondary" @click="closeTimePicker">取消</button>
          <button type="button" class="btn btn-primary" @click="confirmTimePicker">确定</button>
        </div>
      </div>
    </div>

    <!-- ================= 全局提示 ================= -->
    <div v-if="toast.show" class="toast-wrap" aria-live="polite">
      <div class="toast" :class="toast.type">
        <span class="toast-icon" aria-hidden="true">
          <svg v-if="toast.type === 'success'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
            <polyline points="22 4 12 14.01 9 11.01" />
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
        </span>
        <span>{{ toast.message }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted, onBeforeUnmount, nextTick, computed, watch } from "vue"
import { useRouter } from "vue-router"
// ECharts 按需引入：只打包用到的图表类型与组件，
// 避免把完整 echarts（含地图、3D 等未使用模块）打进产物
import * as echarts from "echarts/core"
import { BarChart, LineChart, PieChart } from "echarts/charts"
import { GridComponent, LegendComponent, TooltipComponent } from "echarts/components"
import { CanvasRenderer } from "echarts/renderers"
import request from "../api/request"
import CustomSelect from "../components/CustomSelect.vue"
// 考勤状态 → 徽标样式：与学生端共用同一份映射（原先两边各复制了一份）
import { attendanceStatusBadgeClass as statusBadgeClass } from "../utils/status"
import { errorMessage, isAuthError } from "../utils/error"
import { readSession, clearSession } from "../utils/auth"
import { formatDateTime } from "../utils/format"

echarts.use([
  LineChart,
  PieChart,
  BarChart,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  CanvasRenderer
])

// =====================================================
// 类型定义
// =====================================================

interface CourseRow {
  id: string
  name: string
  date: string | null
  time: string | null
  class_id: string
  class_name: string
}

interface TaskRow {
  task_id: string
  course_id: string
  course_name: string
  class_id: string
  class_name: string
  start_time: string
  end_time: string
  status: number
  signed_count: number
  total_count: number
}

interface RosterItem {
  student_id: string
  student_no: string
  student_name: string
  record_id: string | null
  status: number
  status_text: string
  sign_time: string | null
  ip: string | null
  location: string | null
  is_script?: number
  is_cross?: number
  source_site?: string | null
  source_site_name?: string | null
}

interface RosterData {
  task: {
    task_id: string
    course_id: string
    course_name: string
    class_id: string
    class_name: string
    start_time: string
    end_time: string
    status: number
  } | null
  stats: Record<string, number>
  roster: RosterItem[]
}

interface StatsSummary {
  normal: number
  late: number
  absent: number
  early: number
  sick: number
  leave: number
  unsigned?: number
  total: number
}

interface StatsTask {
  task_id: string
  course_name: string
  class_name: string
  start_time: string
  end_time: string
  total_count: number
  normal_count: number
  late_count: number
  absent_count: number
  early_count: number
  sick_count: number
  leave_count: number
}

interface ApiResult<T> {
  code: number
  message?: string
  data?: T
}

type TabKey = "courses" | "tasks" | "roster" | "rollcall" | "stats"
type AlertType = "success" | "error"

const statusOptions = [
  { value: 1, label: "正常", key: "normal", color: "#10b981" },
  { value: 2, label: "迟到", key: "late", color: "#f59e0b" },
  { value: 3, label: "旷课", key: "absent", color: "#dc2626" },
  { value: 4, label: "早退", key: "early", color: "#c559f0" },
  { value: 5, label: "病假", key: "sick", color: "#0891b2" },
  { value: 6, label: "事假", key: "leave", color: "#64748b" },
  { value: 7, label: "未签到", key: "unsigned", color: "#94a3b8" }
] as const

// =====================================================
// 数字滚动动画（Count Up Animation）
// =====================================================

/**
 * 数字从 from 平滑滚动到 to
 * 使用 easeOutCubic 缓动曲线，时长 800ms
 */
function animateCount(from: number, to: number, duration: number, onUpdate: (v: number) => void): () => void {
  const start = performance.now()
  let rafId = 0
  const easeOutCubic = (t: number) => 1 - Math.pow(1 - t, 3)
  const tick = (now: number) => {
    const elapsed = now - start
    const progress = Math.min(elapsed / duration, 1)
    const eased = easeOutCubic(progress)
    const current = Math.round(from + (to - from) * eased)
    onUpdate(current)
    if (progress < 1) {
      rafId = requestAnimationFrame(tick)
    }
  }
  rafId = requestAnimationFrame(tick)
  return () => cancelAnimationFrame(rafId)
}

// 签到名册统计的动画显示值
const displayStats = reactive<Record<number, number>>({})
const displayTotal = ref(0)

// =====================================================
// 页面状态
// =====================================================

const router = useRouter()

const activeTab = ref<TabKey>("courses")

const pageLoading = ref(true)
const pageError = ref("")

const teacherName = ref("教师")
const teacherInitial = ref("师")

const courses = ref<CourseRow[]>([])
const tasks = ref<TaskRow[]>([])

// 今天已发起过签到的课程 ID 集合（用于禁用"发起签到"按钮）
const todayTaskCourseIds = ref<Set<string>>(new Set())

/**
 * 加载今天的签到任务，标记哪些课程今天已经发起过签到
 */
async function loadTodayTaskCourseIds(): Promise<void> {
  const pad = (n: number) => String(n).padStart(2, "0")
  const now = new Date()
  const todayStr = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`
  try {
    const res = await request.get<ApiResult<TaskRow[]>>("/api/teacher/tasks", {
      params: { date: todayStr }
    })
    const list = res.data.data || []
    todayTaskCourseIds.value = new Set(list.map(t => t.course_id))
  } catch {
    // 静默失败，不影响主流程
  }
}

/**
 * 判断某课程今天是否已发起过签到
 */
function isTaskStartedToday(courseId: string): boolean {
  return todayTaskCourseIds.value.has(courseId)
}

// 按日期分组课程：只显示今天、明天、后天三天
const groupedCourses = computed(() => {
  const pad = (n: number) => String(n).padStart(2, "0")
  const now = new Date()
  const todayStr = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`
  const t = new Date(todayStr)

  // 只保留今天、明天、后天三天的课程
  const visibleCourses = courses.value.filter((c) => {
    const d = c.date
    if (!d) return false
    const dateObj = new Date(d)
    if (isNaN(dateObj.getTime())) return false
    const diff = Math.round((dateObj.getTime() - t.getTime()) / 86400000)
    return diff >= 0 && diff <= 2
  })

  const groups = new Map<string, CourseRow[]>()
  for (const c of visibleCourses) {
    const key = c.date || "未安排"
    if (!groups.has(key)) groups.set(key, [])
    groups.get(key)!.push(c)
  }
  const labelFor = (date: string) => {
    if (date === todayStr) return `今天 · ${date}`
    const d = new Date(date)
    const diff = Math.round((d.getTime() - t.getTime()) / 86400000)
    if (diff === 1) return `明天 · ${date}`
    if (diff === 2) return `后天 · ${date}`
    const wd = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"][d.getDay()]
    return `${date} · ${wd}`
  }
  const sortedKeys = Array.from(groups.keys()).sort((a, b) => {
    return a.localeCompare(b)
  })
  return sortedKeys.map(k => ({ key: k, label: labelFor(k), items: groups.get(k)! }))
})

const roster = reactive<RosterData>({
  task: null,
  stats: {},
  roster: []
})

// 触发签到名册统计数字滚动动画
function triggerCountUp() {
  for (const s of statusOptions) {
    const target = roster.stats[s.value] || 0
    const current = displayStats[s.value] || 0
    if (current === target) continue
    animateCount(current, target, 800, (v) => {
      displayStats[s.value] = v
    })
  }
  const totalTarget = roster.roster.length
  if (displayTotal.value !== totalTarget) {
    animateCount(displayTotal.value, totalTarget, 800, (v) => {
      displayTotal.value = v
    })
  }
}

// 监听 roster 数据变化，自动触发数字滚动
watch(
  () => [roster.stats, roster.roster.length] as const,
  () => { nextTick(() => triggerCountUp()) },
  { deep: true }
)

// 重复 IP 检测：同一 IP 被两个及以上不同学生使用时标红（疑似代签）
const duplicateIpSet = computed(() => {
  const count = new Map<string, number>()
  for (const r of roster.roster) {
    if (r.ip) count.set(r.ip, (count.get(r.ip) || 0) + 1)
  }
  const set = new Set<string>()
  for (const [ip, n] of count) {
    if (n > 1) set.add(ip)
  }
  return set
})
const duplicateIpCount = computed(() => {
  let n = 0
  for (const r of roster.roster) {
    if (r.ip && duplicateIpSet.value.has(r.ip)) n++
  }
  return n
})

const stats = reactive<{ summary: StatsSummary; tasks: StatsTask[] }>({
  summary: { normal: 0, late: 0, absent: 0, early: 0, sick: 0, leave: 0, total: 0 },
  tasks: []
})

const taskFilter = reactive({ course_name: "", date: "" })
const statsFilter = reactive({ course_id: "", date: "" })

// 按课程名称去重，用于签到任务筛选下拉框（合并同名课程）
const uniqueCourseNames = computed(() => {
  const seen = new Set<string>()
  const result: { name: string; count: number }[] = []
  for (const c of courses.value) {
    if (seen.has(c.name)) continue
    seen.add(c.name)
    const count = courses.value.filter(x => x.name === c.name).length
    result.push({ name: c.name, count })
  }
  return result
})

/**
 * 统计分析模块的课程选项：
 * 只显示昨天和今天两天的课程（diff 在 -1 到 0 之间）。
 * 当课程名重复时，在名称后追加 日期(MMDD)+开始时间(HHMM)，
 * 例如 "生产性实训09150830"
 */
const statsCourseOptions = computed(() => {
  const pad = (n: number) => String(n).padStart(2, "0")
  const now = new Date()
  const todayStr = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`
  const t = new Date(todayStr)

  // 只保留昨天和今天的课程
  const visible = courses.value.filter((c) => {
    if (!c.date) return false
    const d = new Date(c.date)
    if (isNaN(d.getTime())) return false
    const diff = Math.round((d.getTime() - t.getTime()) / 86400000)
    return diff >= -1 && diff <= 0
  })

  // 统计每个课程名出现的次数（仅基于可见课程）
  const nameCount = new Map<string, number>()
  for (const c of visible) {
    nameCount.set(c.name, (nameCount.get(c.name) || 0) + 1)
  }
  return visible.map((c) => {
    const isDup = (nameCount.get(c.name) || 0) > 1
    let displayName = c.name
    if (isDup) {
      // 提取日期 MMDD
      const dateMatch = (c.date || "").match(/(\d{4})-(\d{2})-(\d{2})/)
      const mmdd = dateMatch ? `${dateMatch[2]}${dateMatch[3]}` : ""
      // 提取开始时间 HHMM（time 形如 "08:30-11:50"）
      const startTimeRaw = (c.time || "").split("-")[0].trim().replace(":", "")
      displayName = `${c.name}${mmdd}${startTimeRaw}`
    }
    return { id: c.id, name: c.name, displayName }
  })
})

const taskCourseOptions = computed(() => [
  { label: "全部课程", value: "" },
  ...uniqueCourseNames.value.map((c) => ({
    label: c.count > 1 ? `${c.name}（共${c.count}节课）` : c.name,
    value: c.name
  }))
])
const statsCourseSelectOptions = computed(() => [
  { label: "全部课程", value: "" },
  ...statsCourseOptions.value.map((c) => ({ label: c.displayName, value: c.id }))
])
const rollcallTaskOptions = computed(() => [
  { label: "请选择签到任务", value: "" },
  ...tasks.value.map((t) => ({
    label: `${t.course_name} - ${t.class_name}（${formatDateTime(t.start_time)}）`,
    value: t.task_id
  }))
])
const rosterStatusOptions = statusOptions.map((s) => ({ label: s.label, value: s.value }))

const tabMeta: Record<TabKey, { title: string; desc: string }> = {
  courses: { title: "我的课程", desc: "查看授课课程并发起课堂签到" },
  tasks: { title: "签到任务", desc: "管理签到任务，查看签到进度并可提前结束" },
  roster: { title: "签到名册", desc: "查看全班学生签到情况，可手动修改签到状态" },
  rollcall: { title: "课堂点名", desc: "自动朗读学生姓名，语音识别喊到并标记签到" },
  stats: { title: "统计分析", desc: "按课程或日期查看签到情况的图表化统计" }
}

// =====================================================
// 弹窗 / 提示
// =====================================================

const createTaskModal = reactive({
  show: false,
  course_id: "",
  course_name: "",
  start: "",
  end: "",
  error: "",
  submitting: false
})

// =====================================================
// 自定义时间选择器弹框
// =====================================================

const timePicker = reactive({
  show: false,
  target: "" as "start" | "end" | "",
  // 临时编辑值，格式 YYYY-MM-DDTHH:mm（与 datetime-local 一致）
  tempDate: "",   // YYYY-MM-DD
  tempHour: 8,
  tempMinute: 0
})

/**
 * 打开时间选择器
 * target: "start" 或 "end"
 */
function openTimePicker(target: "start" | "end") {
  timePicker.target = target
  // 读取当前值
  const current = target === "start" ? createTaskModal.start : createTaskModal.end
  if (current) {
    // 解析 YYYY-MM-DDTHH:mm
    const [d, t] = current.split("T")
    timePicker.tempDate = d
    const [h, m] = t.split(":").map(Number)
    timePicker.tempHour = h || 8
    timePicker.tempMinute = m || 0
  } else {
    // 默认值：今天，开始 08:30 / 结束 11:50
    const pad = (n: number) => String(n).padStart(2, "0")
    const now = new Date()
    timePicker.tempDate = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`
    if (target === "start") {
      timePicker.tempHour = 8
      timePicker.tempMinute = 30
    } else {
      timePicker.tempHour = 11
      timePicker.tempMinute = 50
    }
  }
  timePicker.show = true
}

/**
 * 确认时间选择
 */
function confirmTimePicker() {
  const pad = (n: number) => String(n).padStart(2, "0")
  const value = `${timePicker.tempDate}T${pad(timePicker.tempHour)}:${pad(timePicker.tempMinute)}`
  if (timePicker.target === "start") {
    createTaskModal.start = value
  } else if (timePicker.target === "end") {
    createTaskModal.end = value
  }
  timePicker.show = false
}

/**
 * 取消时间选择
 */
function closeTimePicker() {
  timePicker.show = false
}

/**
 * 格式化时间显示
 * YYYY-MM-DDTHH:mm → 2026-09-15 08:30
 */
function fmtTimeDisplay(value: string): string {
  if (!value) return "点击选择时间"
  return value.replace("T", " ")
}

/**
 * 选择日期（简易日历：前后 7 天 + 今天）
 */
function selectDate(date: string) {
  timePicker.tempDate = date
}

/**
 * 获取可选日期列表（今天 ± 7 天）
 */
function getDateOptions(): { date: string; label: string; weekday: string; isToday: boolean }[] {
  const pad = (n: number) => String(n).padStart(2, "0")
  const weekdays = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"]
  const now = new Date()
  const todayStr = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`
  const result = []
  for (let i = -1; i <= 7; i++) {
    const d = new Date(now)
    d.setDate(d.getDate() + i)
    const dateStr = `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
    result.push({
      date: dateStr,
      label: `${pad(d.getMonth() + 1)}-${pad(d.getDate())}`,
      weekday: weekdays[d.getDay()],
      isToday: dateStr === todayStr
    })
  }
  return result
}

/**
 * 快速设置小时
 */
function setHour(h: number) {
  timePicker.tempHour = h
}

/**
 * 快速设置分钟
 */
function setMinute(m: number) {
  timePicker.tempMinute = m
}

const toast = reactive({ show: false, type: "success" as AlertType, message: "" })
let toastTimer: ReturnType<typeof setTimeout> | undefined

function showToast(message: string, type: AlertType = "success") {
  toast.message = message
  toast.type = type
  toast.show = true
  if (toastTimer) clearTimeout(toastTimer)
  toastTimer = setTimeout(() => { toast.show = false }, 2800)
}

// =====================================================
// 工具函数
// =====================================================

function toBackendDT(localValue: string): string {
  // datetime-local 输出 YYYY-MM-DDTHH:mm → YYYY-MM-DD HH:mm:ss
  return localValue.replace("T", " ") + ":00"
}

function taskStatusText(t: TaskRow): string {
  if (t.status === 0) return "已关闭"
  // 签到窗口 = end_time + 10 分钟（迟到宽限期）
  const endPlus10 = new Date(t.end_time).getTime() + 10 * 60 * 1000
  if (endPlus10 < Date.now()) return "已结束"
  return "进行中"
}

function taskStatusClass(t: TaskRow): string {
  const text = taskStatusText(t)
  if (text === "进行中") return "badge-ok"
  return "badge-off"
}

function canClose(t: TaskRow): boolean {
  return t.status === 1
}

// =====================================================
// 数据加载
// =====================================================

async function fetchCourses(): Promise<void> {
  const res = await request.get<ApiResult<CourseRow[]>>("/api/teacher/courses")
  courses.value = res.data.data || []
}

async function fetchTasks(): Promise<void> {
  const params: Record<string, string> = {}
  // 后端只支持 course_id，同名课程合并后按 course_name 在前端过滤
  if (taskFilter.date) params.date = taskFilter.date
  const res = await request.get<ApiResult<TaskRow[]>>("/api/teacher/tasks", { params })
  let list = res.data.data || []
  if (taskFilter.course_name) {
    list = list.filter(t => t.course_name === taskFilter.course_name)
  }
  tasks.value = list
}

async function fetchRoster(): Promise<void> {
  if (!roster.task) return
  const res = await request.get<ApiResult<RosterData>>("/api/teacher/attendance/roster", {
    params: { task_id: roster.task.task_id }
  })
  const data = res.data.data
  if (data) {
    roster.task = data.task
    roster.stats = data.stats || {}
    roster.roster = data.roster || []
  }
}

async function fetchStats(): Promise<void> {
  const params: Record<string, string> = {}
  if (statsFilter.course_id) params.course_id = statsFilter.course_id
  if (statsFilter.date) params.date = statsFilter.date
  const res = await request.get<ApiResult<{ summary: StatsSummary; tasks: StatsTask[] }>>("/api/teacher/statistics", { params })
  const data = res.data.data
  if (data) {
    // 过滤掉未来签到的课程（start_time 在当前时间之后的任务不计入统计）
    const now = Date.now()
    const filteredTasks = (data.tasks || []).filter((t) => {
      const startMs = new Date(t.start_time).getTime()
      return !isNaN(startMs) && startMs <= now
    })
    // 重新汇总，避免包含未来任务（强制 Number 转换，防止字符串拼接）
    const summary: StatsSummary = {
      normal: 0, late: 0, absent: 0, early: 0, sick: 0, leave: 0, total: 0
    }
    for (const t of filteredTasks) {
      summary.normal += Number(t.normal_count) || 0
      summary.late += Number(t.late_count) || 0
      summary.absent += Number(t.absent_count) || 0
      summary.early += Number(t.early_count) || 0
      summary.sick += Number(t.sick_count) || 0
      summary.leave += Number(t.leave_count) || 0
      summary.total += Number(t.total_count) || 0
    }
    stats.summary = summary
    stats.tasks = filteredTasks
  }
  await nextTick()
  renderCharts()
}

/**
 * 进入统计分析 Tab 时的初始化：
 * 默认选择"正在签到中"的课程进行数据分析；若没有，则保持全部课程。
 */
async function initStatsTab(): Promise<void> {
  // 已经选了课程就直接拉取
  if (statsFilter.course_id) {
    fetchStats()
    return
  }
  try {
    // 拉取所有签到任务，找出当前正在签到中的课程
    const res = await request.get<ApiResult<TaskRow[]>>("/api/teacher/tasks")
    const list = res.data.data || []
    const now = Date.now()
    const active = list.find((t) => {
      if (t.status !== 1) return false
      const start = new Date(t.start_time).getTime()
      const end = new Date(t.end_time).getTime()
      return !isNaN(start) && !isNaN(end) && start <= now && now <= end
    })
    if (active) {
      statsFilter.course_id = active.course_id
    }
  } catch {
    /* 静默失败，不影响后续 fetchStats */
  }
  fetchStats()
}

async function loadAll(): Promise<void> {
  pageLoading.value = true
  pageError.value = ""
  try {
    await fetchCourses()
    await fetchTasks()
    await loadTodayTaskCourseIds()
  } catch (error: unknown) {
    if (isAuthError(error)) {
      showToast("登录已失效，请重新登录", "error")
      router.replace("/login")
      return
    }
    pageError.value = errorMessage(error, "数据加载失败，请检查后端服务是否启动")
  } finally {
    pageLoading.value = false
  }
}

// =====================================================
// 发起签到
// =====================================================

function openCreateTask(course: CourseRow) {
  createTaskModal.course_id = course.id
  createTaskModal.course_name = course.name
  createTaskModal.start = ""
  createTaskModal.end = ""
  createTaskModal.error = ""
  createTaskModal.show = true
}

function closeCreateTask() {
  createTaskModal.show = false
}

async function confirmCreateTask() {
  createTaskModal.error = ""
  if (!createTaskModal.start || !createTaskModal.end) {
    createTaskModal.error = "请填写签到开始和结束时间"
    return
  }
  if (new Date(createTaskModal.end) <= new Date(createTaskModal.start)) {
    createTaskModal.error = "结束时间必须晚于开始时间"
    return
  }

  createTaskModal.submitting = true
  try {
    const res = await request.post<ApiResult<null>>("/api/teacher/attendance/create", {
      course_id: createTaskModal.course_id,
      start_time: toBackendDT(createTaskModal.start),
      end_time: toBackendDT(createTaskModal.end)
    })
    if (res.data.code === 200) {
      createTaskModal.show = false
      showToast("签到任务已创建")
      await fetchTasks()
      // 刷新今天的签到状态，让对应课程按钮变灰
      await loadTodayTaskCourseIds()
    } else {
      createTaskModal.error = res.data.message || "创建失败"
    }
  } catch (error: unknown) {
    if (isAuthError(error)) {
      createTaskModal.show = false
      router.replace("/login")
      return
    }
    createTaskModal.error = errorMessage(error, "创建签到任务失败")
  } finally {
    createTaskModal.submitting = false
  }
}

// =====================================================
// 结束签到
// =====================================================

async function closeTask(t: TaskRow) {
  if (!window.confirm(`确认结束「${t.course_name}」的签到？结束后学生将无法继续签到。`)) return
  try {
    const res = await request.post<ApiResult<null>>("/api/teacher/attendance/close", { task_id: t.task_id })
    if (res.data.code === 200) {
      t.status = 0
      showToast("签到已结束")
    } else {
      showToast(res.data.message || "操作失败", "error")
    }
  } catch (error: unknown) {
    if (isAuthError(error)) { router.replace("/login"); return }
    showToast(errorMessage(error, "结束签到失败"), "error")
  }
}

// 删除签到任务
async function deleteTask(t: TaskRow) {
  if (!window.confirm(`确认删除「${t.course_name}」的签到任务？该任务下的所有签到记录将一并删除，且不可恢复。`)) return
  try {
    const res = await request.post<ApiResult<null>>("/api/teacher/attendance/delete", { task_id: t.task_id })
    if (res.data.code === 200) {
      tasks.value = tasks.value.filter(x => x.task_id !== t.task_id)
      showToast("签到任务已删除")
    } else {
      showToast(res.data.message || "删除失败", "error")
    }
  } catch (error: unknown) {
    if (isAuthError(error)) { router.replace("/login"); return }
    showToast(errorMessage(error, "删除签到任务失败"), "error")
  }
}

// =====================================================
// 查看名册
// =====================================================

async function viewRoster(taskId: string) {
  activeTab.value = "roster"
  try {
    const res = await request.get<ApiResult<RosterData>>("/api/teacher/attendance/roster", {
      params: { task_id: taskId }
    })
    const data = res.data.data
    if (data) {
      roster.task = data.task
      roster.stats = data.stats || {}
      roster.roster = data.roster || []
    }
  } catch (error: unknown) {
    if (isAuthError(error)) { router.replace("/login"); return }
    showToast(errorMessage(error, "加载签到名册失败"), "error")
  }
}

function viewCourseTasks(course: CourseRow) {
  taskFilter.course_name = course.name
  taskFilter.date = ""
  activeTab.value = "tasks"
  fetchTasks()
}

function resetTaskFilter() {
  taskFilter.course_name = ""
  taskFilter.date = ""
  fetchTasks()
}

function resetStatsFilter() {
  statsFilter.course_id = ""
  statsFilter.date = ""
  fetchStats()
}

// 点击日期框任意位置都弹出原生选择器（不再只点小图标才触发）
function openPicker(event: MouseEvent) {
  const el = event.currentTarget as HTMLInputElement | null
  try {
    el?.showPicker?.()
  } catch {
    /* 部分浏览器在选择器已打开时会抛错，忽略即可 */
  }
}

// =====================================================
// 修改签到状态
// =====================================================

async function changeStatus(row: RosterItem, value: string) {
  const newStatus = Number(value)
  const oldStatus = row.status
  const oldSignTime = row.sign_time
  const oldIp = row.ip
  const oldIsScript = row.is_script
  const oldIsCross = row.is_cross
  row.status = newStatus
  row.status_text = statusOptions.find((s) => s.value === newStatus)?.label || "未知"
  // 教师手动修改状态后清除脚本签到标记（与后端行为一致）
  row.is_script = 0
  // 手动补录后本站已有记录，不再是"已在其他网站签到"
  row.is_cross = 0
  // 设为"未签到"时清除签到时间和 IP
  if (newStatus === 7) {
    row.sign_time = null
    row.ip = null
  }
  try {
    const res = await request.put<ApiResult<null>>("/api/teacher/attendance/record", {
      task_id: roster.task?.task_id,
      student_id: row.student_id,
      status: newStatus
    })
    if (res.data.code !== 200) {
      row.status = oldStatus
      row.status_text = statusOptions.find((s) => s.value === oldStatus)?.label || "未知"
      row.sign_time = oldSignTime
      row.ip = oldIp
      row.is_script = oldIsScript
      row.is_cross = oldIsCross
      showToast(res.data.message || "修改失败", "error")
      return
    }
    // 更新统计
    if (roster.stats[oldStatus]) roster.stats[oldStatus]--
    roster.stats[newStatus] = (roster.stats[newStatus] || 0) + 1
    if (oldIsCross === 1 && roster.stats.cross) roster.stats.cross--
    showToast(`「${row.student_name}」签到状态已更新`)
  } catch (error: unknown) {
    row.status = oldStatus
    row.status_text = statusOptions.find((s) => s.value === oldStatus)?.label || "未知"
    row.sign_time = oldSignTime
    row.ip = oldIp
    row.is_script = oldIsScript
    row.is_cross = oldIsCross
    if (isAuthError(error)) { router.replace("/login"); return }
    showToast(errorMessage(error, "修改签到状态失败"), "error")
  }
}

// =====================================================
// Tab 切换
// =====================================================

function switchTab(tab: TabKey) {
  activeTab.value = tab
  if (tab === "tasks") fetchTasks()
  if (tab === "rollcall") fetchRollcallTasks()
  if (tab === "stats") initStatsTab()
}

// =====================================================
// ECharts
// =====================================================

const pieChartRef = ref<HTMLElement>()
const barChartRef = ref<HTMLElement>()
const lineChartRef = ref<HTMLElement>()
let pieChart: echarts.ECharts | null = null
let barChart: echarts.ECharts | null = null
let lineChart: echarts.ECharts | null = null

function renderCharts() {
  renderLine()
  renderPie()
  renderBar()
}

/**
 * 每日签到人数折线对比图：
 * 按日期聚合 stats.tasks，输出多条折线对比各状态及签到总数
 */
function renderLine() {
  if (!lineChartRef.value) return
  if (!lineChart) lineChart = echarts.init(lineChartRef.value)

  // 按日期聚合
  const byDate = new Map<string, { normal: number; late: number; absent: number; early: number; sick: number; leave: number; signed: number }>()
  const pad = (n: number) => String(n).padStart(2, "0")
  for (const t of stats.tasks) {
    const d = new Date(t.start_time)
    if (isNaN(d.getTime())) continue
    const key = `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
    const entry = byDate.get(key) || { normal: 0, late: 0, absent: 0, early: 0, sick: 0, leave: 0, signed: 0 }
    const n = Number(t.normal_count) || 0
    const l = Number(t.late_count) || 0
    const a = Number(t.absent_count) || 0
    const e = Number(t.early_count) || 0
    const s = Number(t.sick_count) || 0
    const lv = Number(t.leave_count) || 0
    entry.normal += n
    entry.late += l
    entry.absent += a
    entry.early += e
    entry.sick += s
    entry.leave += lv
    // 实际签到 = 正常 + 迟到 + 早退
    entry.signed += n + l + e
    byDate.set(key, entry)
  }

  const dates = Array.from(byDate.keys()).sort()
  const dateLabels = dates.map((d) => {
    const parts = d.split("-")
    return `${parts[1]}/${parts[2]}`
  })

  const pick = (key: "normal" | "late" | "absent" | "early" | "sick" | "leave" | "signed") =>
    dates.map((d) => byDate.get(d)![key])

  const series = [
    { name: "签到总数", type: "line", smooth: true, symbol: "circle", symbolSize: 8, lineStyle: { width: 3 }, itemStyle: { color: "#1e40af" }, areaStyle: { opacity: 0.08 }, data: pick("signed") },
    { name: "正常", type: "line", smooth: true, symbol: "circle", symbolSize: 6, itemStyle: { color: "#10b981" }, data: pick("normal") },
    { name: "迟到", type: "line", smooth: true, symbol: "circle", symbolSize: 6, itemStyle: { color: "#f59e0b" }, data: pick("late") },
    { name: "旷课", type: "line", smooth: true, symbol: "circle", symbolSize: 6, itemStyle: { color: "#dc2626" }, data: pick("absent") },
    { name: "早退", type: "line", smooth: true, symbol: "circle", symbolSize: 6, itemStyle: { color: "#c559f0" }, data: pick("early") }
  ]

  lineChart.setOption({
    tooltip: { trigger: "axis" },
    legend: { top: 0, icon: "circle", textStyle: { fontSize: 11 } },
    grid: { left: 40, right: 16, top: 40, bottom: 32 },
    xAxis: { type: "category", data: dateLabels, axisLabel: { fontSize: 11 }, boundaryGap: false },
    yAxis: { type: "value", minInterval: 1 },
    series
  })
}

function renderPie() {
  if (!pieChartRef.value) return
  if (!pieChart) pieChart = echarts.init(pieChartRef.value)

  const s = stats.summary
  const data = statusOptions
    .filter((opt) => opt.value !== 7)
    .map((opt) => ({
      name: opt.label,
      value: s[opt.key as keyof StatsSummary] || 0,
      itemStyle: { color: opt.color }
    }))

  pieChart.setOption({
    tooltip: { trigger: "item", formatter: "{b}: {c} ({d}%)" },
    legend: { bottom: 0, icon: "circle" },
    series: [{
      type: "pie",
      radius: ["42%", "68%"],
      center: ["50%", "45%"],
      avoidLabelOverlap: true,
      itemStyle: { borderRadius: 6, borderColor: "#fff", borderWidth: 2 },
      label: { show: true, formatter: "{b}\n{c}人" },
      data
    }]
  })
}

function renderBar() {
  if (!barChartRef.value) return
  if (!barChart) barChart = echarts.init(barChartRef.value)

  const taskLabels = stats.tasks.map((t) => {
    const d = new Date(t.start_time)
    const pad = (n: number) => String(n).padStart(2, "0")
    return `${d.getMonth() + 1}/${d.getDate()} ${pad(d.getHours())}:${pad(d.getMinutes())}\n${t.course_name}`
  })

  const series = statusOptions
    .filter((opt) => opt.value !== 7)
    .map((opt) => ({
      name: opt.label,
      type: "bar",
      stack: "total",
      itemStyle: { color: opt.color },
      data: stats.tasks.map((t) => t[`${opt.key}_count` as keyof StatsTask] as number || 0)
    }))

  barChart.setOption({
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    legend: { top: 0, icon: "circle" },
    grid: { left: 48, right: 24, top: 48, bottom: 64 },
    xAxis: { type: "category", data: taskLabels, axisLabel: { fontSize: 11 } },
    yAxis: { type: "value", minInterval: 1 },
    series
  })
}

function handleResize() {
  lineChart?.resize()
  pieChart?.resize()
  barChart?.resize()
}

// =====================================================
// 退出登录
// =====================================================

function logout() {
  localStorage.removeItem("access_token")
  localStorage.removeItem("user")
  router.push("/login")
}

// =====================================================
// 初始化
// =====================================================

/**
 * 校验教师端登录态
 *
 * 返回缓存的 user 对象表示可用；返回 null 表示不通过（令牌缺失/过期、
 * 或角色不是教师），此时已清掉本地缓存并跳登录页，调用方不要再请求接口。
 */
function initTeacher(): Record<string, any> | null {
  const session = readSession()
  if (!session) {
    router.replace("/login")
    return null
  }
  if (Number(session.role) !== 2) {
    clearSession()
    router.replace("/login")
    return null
  }
  return session
}

onMounted(async () => {
  // 登录态不通过时直接结束，不再发出 courses / tasks 等必然 401 的请求
  const session = initTeacher()
  if (!session) return

  const name = session.teacher_name || session.name || session.username
  if (name) {
    teacherName.value = name
    teacherInitial.value = name.slice(0, 1).toUpperCase()
  }

  await loadAll()
  window.addEventListener("resize", handleResize)
})

// =====================================================
// 课堂点名模块
// =====================================================

// --- 点名状态 ---
const rollcallTaskId = ref("")
const rollcallRoster = ref<RosterItem[]>([])
const rollcallIndex = ref(-1)
const rollcallRunning = ref(false)
const rollcallPaused = ref(false)
const rollcallListening = ref(false)       // 语音识别监听中
const speechSupported = ref(false)         // 浏览器是否支持语音识别
const rollcallMaleVoice = ref<SpeechSynthesisVoice | null>(null)

// --- TTS 初始化 ---
const availableVoices = ref<SpeechSynthesisVoice[]>([])
const selectedVoiceName = ref("")
const voiceOptions = computed(() => availableVoices.value.map((v) => ({ label: v.name, value: v.name })))

function initTTS() {
  if (!("speechSynthesis" in window)) return
  const loadVoices = () => {
    const voices = window.speechSynthesis.getVoices()
    if (!voices.length) return
    // 筛选中文语音
    const zh = voices.filter(v => v.lang.startsWith("zh"))
    availableVoices.value = zh

    // 按质量优先级选择默认声音
    // 1. Premium 云端男声（最接近真人）
    // 2. 系统男声 Yunxi / Kangkang
    // 3. 任何中文男声
    // 4. 任何中文语音（退而求其次）
    let best = zh.find(v => /premium.*(male|man)|(male|man).*premium|云希|Yunxi/i.test(v.name))
    if (!best) best = zh.find(v => /male|男|Kangkang|Hui|男|云希/i.test(v.name))
    if (!best) best = zh[0]

    rollcallMaleVoice.value = best || null
    selectedVoiceName.value = best?.name || ""
  }
  loadVoices()
  window.speechSynthesis.onvoiceschanged = loadVoices
}

// --- 音色切换 ---
function onVoiceChange() {
  const v = availableVoices.value.find(v => v.name === selectedVoiceName.value)
  if (v) rollcallMaleVoice.value = v
}

// --- 试听当前音色 ---
async function previewVoice() {
  if (!("speechSynthesis" in window)) { showToast("浏览器不支持语音合成", "error"); return }
  window.speechSynthesis.cancel()
  await speakName("同学们好，现在开始点名")
}

// --- 语音识别初始化 ---
let recognition: any = null

function initSpeechRecognition() {
  const SR = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
  if (!SR) {
    speechSupported.value = false
    return
  }
  speechSupported.value = true
  recognition = new SR()
  recognition.lang = "zh-CN"
  recognition.continuous = false
  recognition.interimResults = false
}

// --- 朗读学生姓名 ---
function speakName(name: string): Promise<void> {
  return new Promise((resolve) => {
    const synth = window.speechSynthesis
    if (!synth) { resolve(); return }

    // Chrome 已知 bug：
    // 1. 引擎空闲后会休眠，需先 resume() 唤醒，否则首次播报延迟 1~2 秒
    // 2. cancel() 会让引擎进入暂停状态，仅在确实在播报时才调用
    try { synth.resume() } catch { /* ignore */ }
    if (synth.speaking || synth.pending) {
      synth.cancel()
    }

    const u = new SpeechSynthesisUtterance(name)
    u.lang = "zh-CN"
    u.rate = 0.9
    u.pitch = rollcallMaleVoice.value ? 0.8 : 0.6
    if (rollcallMaleVoice.value) u.voice = rollcallMaleVoice.value

    let settled = false
    const done = () => {
      if (settled) return
      settled = true
      resolve()
    }
    u.onend = done
    u.onerror = done
    // 兜底：个别情况下 onend 不触发，避免流程卡住
    const guard = setTimeout(done, 8000)
    u.onend = () => { clearTimeout(guard); done() }

    synth.speak(u)
  })
}

// --- 监听学生喊"到" ---
function listenForResponse(timeoutMs = 3000): Promise<boolean> {
  return new Promise((resolve) => {
    const SR = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    if (!SR || !speechSupported.value) { resolve(false); return }
    // 每次创建新实例，避免上次事件残留
    const rec = new SR()
    rec.lang = "zh-CN"
    rec.continuous = false
    rec.interimResults = false

    let resolved = false
    let timer: ReturnType<typeof setTimeout> | undefined
    const done = (val: boolean) => {
      if (resolved) return
      resolved = true
      if (timer) clearTimeout(timer)
      rollcallListening.value = false
      activeListenRec = null
      try { rec.stop() } catch { /* ignore */ }
      resolve(val)
    }

    rollcallListening.value = true
    activeListenRec = rec
    rec.onresult = (e: any) => {
      const text = (e.results[0][0].transcript || "").trim()
      // 只匹配"到"及其常见变体，避免误识别
      if (/^(到|到了|我到|在|我来了?|来了?)$/i.test(text)) done(true)
    }
    rec.onerror = (e: any) => {
      // 麦克风不可用时禁用语音识别，不再反复尝试
      if (e.error === "not-allowed" || e.error === "service-not-allowed" || e.error === "device-not-found" || e.error === "audio-capture") {
        speechSupported.value = false
        showToast("未检测到麦克风设备，已切换为手动点名模式", "error")
      }
      done(false)
    }
    rec.onend = () => done(false)
    timer = setTimeout(() => done(false), timeoutMs)
    try {
      rec.start()
    } catch {
      done(false)
    }
  })
}

// --- 标记学生为正常签到 ---
async function markStudentSigned(student: RosterItem) {
  // 更新本地状态
  student.status = 1
  student.status_text = "正常"
  student.is_script = 0
  student.sign_time = new Date().toLocaleTimeString("zh-CN", { hour12: false })
  // 调用后端 API
  try {
    await request.put("/api/teacher/attendance/record", {
      task_id: rollcallTaskId.value,
      student_id: student.student_id,
      status: 1
    })
  } catch {
    showToast("标记签到状态失败", "error")
  }
}

// --- 加载点名可选任务列表 ---
async function fetchRollcallTasks() {
  try {
    const res = await request.get<ApiResult<TaskRow[]>>("/api/teacher/tasks")
    const list = res.data.data || []
    // 只显示有签到任务（status=1 进行中 或 status=2 已结束）
    rollcallTaskId.value = ""
    rollcallRoster.value = []
    // 自动选第一个任务
    if (list.length > 0) {
      rollcallTaskId.value = list[0].task_id
      await loadRollcallRoster()
    }
  } catch {
    showToast("加载签到任务失败", "error")
  }
}

// --- 加载点名名单 ---
async function loadRollcallRoster() {
  if (!rollcallTaskId.value) {
    rollcallRoster.value = []
    return
  }
  try {
    const res = await request.get<ApiResult<RosterData>>("/api/teacher/attendance/roster", {
      params: { task_id: rollcallTaskId.value }
    })
    const data = res.data.data
    if (data && data.roster) {
      rollcallRoster.value = data.roster.map(r => ({ ...r }))
    } else {
      rollcallRoster.value = []
    }
    rollcallIndex.value = -1
    rollcallRunning.value = false
    rollcallPaused.value = false
  } catch {
    showToast("加载点名名单失败", "error")
  }
}

// --- 点名主循环 ---
async function rollcallStep() {
  if (!rollcallRunning.value || rollcallPaused.value) return
  // 找下一个未签到的学生
  let next = -1
  for (let i = rollcallIndex.value + 1; i < rollcallRoster.value.length; i++) {
    if (rollcallRoster.value[i].status !== 1) {
      next = i
      break
    }
  }
  if (next === -1) {
    // 全部已点名
    rollcallRunning.value = false
    showToast("点名完成", "success")
    return
  }
  rollcallIndex.value = next
  const student = rollcallRoster.value[next]

  // 朗读姓名
  await speakName(student.student_name)

  // 等待 500ms 避免 TTS 声音被麦克风识别
  await new Promise(r => setTimeout(r, 500))

  // 语音识别（如果支持）
  if (speechSupported.value && rollcallRunning.value && !rollcallPaused.value) {
    const answered = await listenForResponse(3000)
    if (answered && rollcallRunning.value && !rollcallPaused.value) {
      await markStudentSigned(student)
    }
  }

  // 继续下一个
  if (rollcallRunning.value && !rollcallPaused.value) {
    setTimeout(() => rollcallStep(), 300)
  }
}

// --- 开始点名 ---
function startRollcall() {
  if (!rollcallRoster.value.length) {
    showToast("请先选择签到任务", "error")
    return
  }
  rollcallRunning.value = true
  rollcallPaused.value = false
  rollcallIndex.value = -1
  rollcallStep()
}

// --- 暂停点名 ---
function pauseRollcall() {
  rollcallPaused.value = true
  rollcallListening.value = false
  if ("speechSynthesis" in window) window.speechSynthesis.cancel()
  if (activeListenRec) try { activeListenRec.stop() } catch { /* ignore */ }
  if (recognition) try { recognition.stop() } catch { /* ignore */ }
}

// --- 继续点名 ---
function resumeRollcall() {
  // 中断正在进行的单个点名，避免与自动流程冲突
  manualAbort = true
  manualIndex.value = -1
  if (activeListenRec) try { activeListenRec.stop() } catch { /* ignore */ }
  if ("speechSynthesis" in window) window.speechSynthesis.cancel()
  rollcallPaused.value = false
  rollcallStep()
}

// --- 停止点名 ---
function stopRollcall() {
  manualAbort = true
  manualIndex.value = -1
  rollcallRunning.value = false
  rollcallPaused.value = false
  rollcallListening.value = false
  rollcallIndex.value = -1
  if ("speechSynthesis" in window) window.speechSynthesis.cancel()
  if (activeListenRec) try { activeListenRec.stop() } catch { /* ignore */ }
  if (recognition) try { recognition.stop() } catch { /* ignore */ }
}

// --- 手动点名某学生：朗读 + 语音识别，听到"到"才标记 ---
const manualBusy = ref(false)
const manualIndex = ref(-1)          // 暂停时手动点名的学生（不影响自动光标）
let activeListenRec: any = null      // 当前语音识别实例（用于暂停/恢复时中断）
let manualAbort = false              // 恢复/停止自动点名时中止手动流程

async function manualRollcall(index: number) {
  const student = rollcallRoster.value[index]
  if (!student) return
  // 自动点名正在进行（非暂停状态）时禁用单个点名，避免与自动流程抢麦克风
  if (rollcallRunning.value && !rollcallPaused.value) return
  // 已经签到或正在处理中则忽略
  if (student.status === 1 || manualBusy.value) return

  manualBusy.value = true
  manualIndex.value = index
  manualAbort = false
  try {
    // 朗读姓名
    await speakName(student.student_name)
    if (manualAbort) return
    // 等待 500ms 避免 TTS 声音被麦克风识别
    await new Promise(r => setTimeout(r, 500))
    if (manualAbort) return
    // 有麦克风时监听学生喊"到"，听到才标记
    if (speechSupported.value) {
      const answered = await listenForResponse(3000)
      if (!manualAbort && answered) await markStudentSigned(student)
    }
    // 没有麦克风/没听到：保持"未应答"，老师可点"✓"按钮手动确认
  } finally {
    manualBusy.value = false
    manualIndex.value = -1
    activeListenRec = null
  }
}

// --- 老师手动确认学生到场 ---
async function confirmPresent(index: number, event: Event) {
  event.stopPropagation()
  const student = rollcallRoster.value[index]
  if (!student || student.status === 1) return
  await markStudentSigned(student)
}

// --- 初始化 ---
initTTS()
initSpeechRecognition()

// 保活：Chrome 语音引擎空闲约 15 秒会休眠，定期 resume 保持唤醒
// （无播报时 resume 是空操作，不会发出声音）
const ttsKeepAlive = window.setInterval(() => {
  if ("speechSynthesis" in window) {
    try { window.speechSynthesis.resume() } catch { /* ignore */ }
  }
}, 5000)

onBeforeUnmount(() => {
  window.removeEventListener("resize", handleResize)
  lineChart?.dispose()
  pieChart?.dispose()
  barChart?.dispose()
  // 清理点名资源
  window.clearInterval(ttsKeepAlive)
  if ("speechSynthesis" in window) window.speechSynthesis.cancel()
  if (recognition) try { recognition.stop() } catch { /* ignore */ }
})
</script>

<style scoped>
.teacher-page {
  --primary: #1e40af;
  --primary-hover: #1e3a8a;
  --primary-soft: #dbeafe;
  --secondary: #f8fafc;
  --accent1: #3b82f6;
  --accent2: #64748b;
  --accent3: #10b981;
  --accent4: #c559f0;
  --gray-50: #f8fafc;
  --gray-100: #f1f5f9;
  --gray-200: #e2e8f0;
  --gray-300: #cbd5e1;
  --gray-500: #64748b;
  --gray-700: #334155;
  --gray-900: #0f172a;
  --green: #10b981;
  --amber: #f59e0b;
  --red: #dc2626;
  --purple: #c559f0;
  --cyan: #0891b2;

  display: flex;
  position: fixed;
  inset: 0;
  background: var(--gray-50);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
  color: var(--gray-900);
}

/* ============ 侧边栏 ============ */
.sidebar {
  width: 232px;
  background: var(--primary);
  border-right: 1px solid rgba(255, 255, 255, .08);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  height: 100%;
  overflow-y: auto;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 22px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, .08);
}

.brand-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: rgba(255, 255, 255, .15);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background .2s ease-out, color .2s ease-out, transform .2s ease-out;
}
.brand-icon:hover {
  background: var(--accent1);
  color: #fff;
  transform: scale(1.1);
}
.brand-icon svg { width: 22px; height: 22px; transition: color .2s ease-out; }

.brand-name { font-size: 15px; font-weight: 700; color: #fff; }
.brand-sub { font-size: 12px; color: rgba(255, 255, 255, .6); margin-top: 2px; }

.nav { flex: 1; padding: 14px 12px; display: flex; flex-direction: column; gap: 4px; }

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 10px 12px;
  border: none;
  background: transparent;
  border-radius: 8px;
  font-size: 14px;
  color: rgba(255, 255, 255, .75);
  cursor: pointer;
  text-align: left;
  white-space: nowrap;
  transition: background .15s ease-out, color .15s ease-out;
}
.nav-item svg { width: 18px; height: 18px; flex-shrink: 0; }
.nav-item:hover { background: rgba(255, 255, 255, .1); color: #fff; }
.nav-item.active { background: var(--accent1); color: #fff; font-weight: 600; }

.sidebar-footer { padding: 12px; border-top: 1px solid rgba(255, 255, 255, .08); }
.logout-item { color: rgba(255, 255, 255, .75); }
.logout-item:hover { background: rgba(220, 38, 38, .25); color: #fecaca; }

/* ============ 主区域 ============ */
.main { flex: 1; display: flex; flex-direction: column; min-width: 0; overflow: hidden; }

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 28px;
  background: #fff;
  border-bottom: 1px solid var(--gray-200);
}
.topbar-titles h1 { font-size: 20px; font-weight: 700; margin: 0; }
.topbar-titles p { margin: 4px 0 0; font-size: 13px; color: var(--gray-500); }

.teacher-chip { display: flex; align-items: center; gap: 10px; }
.teacher-avatar {
  width: 38px; height: 38px; border-radius: 50%;
  background: var(--primary); color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-weight: 600; font-size: 15px;
}
.teacher-name { font-size: 14px; font-weight: 600; }
.teacher-role { font-size: 12px; color: var(--gray-500); }

.content { flex: 1; padding: 24px 28px; overflow-y: auto; }

/* ============ 卡片 ============ */
.card {
  background: #fff;
  border: 1px solid var(--gray-200);
  border-radius: 12px;
  box-shadow: 0 1px 2px rgba(15, 23, 42, .04);
}
.panel-card { padding: 20px; margin-bottom: 20px; }
.panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 18px;
}
.panel-header h2 { font-size: 16px; font-weight: 700; margin: 0;}
.panel-sub { margin: 4px 0 0; font-size: 12px; color: var(--gray-500); }

.filter-row { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
/* 筛选栏内下拉框与日期框统一为定长：提高优先级覆盖 .form-input{width:100%}，
   并禁止 flex 伸缩，保证两者长度始终一致 */
.filter-row .filter-control { flex: 0 0 250px; width: 150px; }

/* ============ 课程卡片 ============ */
.course-day-list { display: flex; flex-direction: column; gap: 24px; }
.course-day-group { display: flex; flex-direction: column; gap: 12px; }
.course-day-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 8px 14px;
  background: var(--primary-soft);
  border-left: 3px solid var(--primary);
  border-radius: 8px;
  color: var(--primary);
  font-weight: 600;
  font-size: 14px;
}
.course-day-count { font-size: 12px; color: var(--gray-500); font-weight: 500; }
.course-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}
.course-card {
  background: #fff;
  border: 1px solid var(--gray-200);
  border-radius: 12px;
  box-shadow: 0 1px 2px rgba(15, 23, 42, .04);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-width: 0;
  transition: box-shadow .2s ease-out, transform .2s ease-out;
}
.course-card:hover {
  box-shadow: 0 4px 6px -1px rgba(15, 23, 42, .1), 0 2px 4px -2px rgba(15, 23, 42, .1);
  transform: translateY(-2px);
}
.course-card-head { display: flex; justify-content: space-between; align-items: baseline; gap: 8px; min-width: 0; }
.course-name { font-size: 16px; font-weight: 700; word-break: break-word; min-width: 0; }
.course-class { font-size: 12px; color: var(--primary); background: var(--primary-soft); padding: 2px 8px; border-radius: 6px; white-space: nowrap; }
.course-meta { font-size: 13px; color: var(--gray-500); display: flex; flex-direction: column; gap: 2px; }
.course-actions { display: flex; gap: 8px; margin-top: 4px; flex-wrap: wrap; }

/* ============ 表格 ============ */
.table-wrap { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.data-table th {
  text-align: left; padding: 10px 12px;
  background: var(--gray-50); color: var(--gray-500);
  font-weight: 600; font-size: 12px;
  border-bottom: 1px solid var(--gray-200);
  white-space: nowrap;
}
.data-table td { padding: 10px 12px; border-bottom: 1px solid var(--gray-100); }
.data-table tbody tr:hover { background: var(--gray-50); }
.cell-strong { font-weight: 600; }
.col-actions { width: 160px; }
.empty-cell { text-align: center; color: var(--gray-500); padding: 28px; }
.empty-block { grid-column: 1/-1; text-align: center; color: var(--gray-500); padding: 32px; }

.row-actions { display: flex; gap: 6px; flex-wrap: wrap; }

.mono { font-family: "SFMono-Regular", Consolas, monospace; font-size: 12px; }

/* 重复 IP（疑似代签）标红 */
.ip-duplicate {
  color: var(--red, #ef4444);
  font-weight: 700;
}
.ip-duplicate-hint {
  font-size: 13px;
  font-weight: 600;
  color: var(--red, #ef4444);
  white-space: nowrap;
}

/* ============ 徽章 ============ */
.badge { display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: 12px; font-weight: 500; }
.badge-ok { background: #ecfdf5; color: #047857; }
.badge-warn { background: #fef3c7; color: #b45309; }
.badge-danger { background: #fee2e2; color: #b91c1c; }
.badge-purple { background: #faf5ff; color: #a21caf; }
.badge-cyan { background: #cffafe; color: #0e7490; }
.badge-gray { background: #e2e8f0; color: #475569; }
.badge-unsigned { background: #f1f5f9; color: #64748b; }
.badge-off { background: var(--gray-100); color: var(--gray-500); }

/* ============ 统计小卡 ============ */
.stats-row { display: flex; gap: 12px; flex-wrap: wrap; }
.stat-mini {
  flex: 1; min-width: 90px;
  padding: 12px 14px;
  border-radius: 10px;
  border: 1px solid var(--gray-200);
  display: flex; flex-direction: column; gap: 4px;
}
.stat-mini-label { font-size: 12px; color: var(--gray-500); }
.stat-mini-num {
  font-size: 22px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  display: inline-block;
  transition: transform 0.3s ease;
}
.stat-normal { background: #ecfdf5; }
.stat-normal .stat-mini-num { color: var(--accent3); }
.stat-late { background: #fffbeb; }
.stat-late .stat-mini-num { color: var(--amber); }
.stat-absent { background: #fef2f2; }
.stat-absent .stat-mini-num { color: var(--red); }
.stat-early { background: #faf5ff; }
.stat-early .stat-mini-num { color: var(--accent4); }
.stat-sick { background: #ecfeff; }
.stat-sick .stat-mini-num { color: var(--cyan); }
.stat-leave { background: var(--gray-50); }
.stat-leave .stat-mini-num { color: var(--accent2); }
.stat-unsigned { background: #f8fafc; }
.stat-unsigned .stat-mini-num { color: #94a3b8; }
.stat-cross .stat-mini-num { color: var(--cyan); }
.stat-total { background: var(--primary-soft); }
.stat-total .stat-mini-num { color: var(--primary); }

/* ============ 图表 ============ */
.chart-box { width: 100%; height: 340px; }
.chart-tall { height: 420px; }
.chart-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}
.chart-row .panel-card { margin-bottom: 0; }
.chart-half .chart-box { height: 320px; }
@media (max-width: 1100px) {
  .chart-row { grid-template-columns: 1fr; }
}

/* ============ 状态/加载 ============ */
.state-card {
  text-align: center; padding: 60px 20px;
  background: #fff; border-radius: 12px;
  border: 1px solid var(--gray-200);
}
.state-error p { color: var(--red); margin-bottom: 16px; }
.spinner {
  width: 36px; height: 36px; margin: 0 auto 14px;
  border: 3px solid var(--gray-200); border-top-color: var(--primary);
  border-radius: 50%; animation: spin .8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ============ 按钮 ============ */
.btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 6px;
  padding: 8px 16px; border-radius: 8px; font-size: 13px; font-weight: 500;
  border: 1px solid transparent; cursor: pointer;
  box-shadow: 0 1px 2px rgba(15, 23, 42, .04);
  transition: background .15s ease-out, border-color .15s ease-out, transform .15s ease-out, box-shadow .15s ease-out;
  white-space: nowrap;
}
.btn:hover { transform: translateY(-1px); box-shadow: 0 1px 3px rgba(15, 23, 42, .1); }
.btn:active { transform: scale(0.98) translateY(0); box-shadow: 0 1px 2px rgba(15, 23, 42, .04); }
.btn:focus-visible { outline: none; box-shadow: 0 0 0 2px #fff, 0 0 0 4px rgba(37, 99, 235, .5); }
.btn-primary { background: var(--primary); color: #fff; }
.btn-primary:hover { background: var(--primary-hover); }
.btn-primary:disabled { opacity: .5; cursor: not-allowed; transform: none; box-shadow: 0 1px 2px rgba(15, 23, 42, .04); }
.btn-success { background: var(--green, #10b981); color: #fff; }
.btn-success:hover { background: #059669; }
.btn-success:disabled { opacity: .5; cursor: not-allowed; transform: none; box-shadow: 0 1px 2px rgba(15, 23, 42, .04); }
.btn-danger { background: var(--red, #ef4444); color: #fff; }
.btn-danger:hover { background: #dc2626; }
.btn-danger:disabled { opacity: .5; cursor: not-allowed; transform: none; box-shadow: 0 1px 2px rgba(15, 23, 42, .04); }
.btn-secondary { background: #fff; color: var(--gray-700); border-color: var(--gray-200); }
.btn-secondary:hover { background: var(--gray-50); }
.btn-disabled {
  background: var(--gray-100, #f1f5f9);
  color: var(--gray-400, #94a3b8);
  border-color: var(--gray-200, #e2e8f0);
  cursor: not-allowed;
}
.btn-disabled:hover { transform: none; box-shadow: 0 1px 2px rgba(15, 23, 42, .04); }
.btn-sm { padding: 5px 10px; font-size: 12px; }
.btn-soft-primary { background: var(--primary-soft); color: var(--primary); box-shadow: none; }
.btn-soft-primary:hover { background: #bfdbfe; }
.btn-soft-warn { background: #fef3c7; color: #b45309; box-shadow: none; }
.btn-soft-warn:hover { background: #fde68a; }
.btn-soft-danger { background: #fee2e2; color: #b91c1c; box-shadow: none; }
.btn-soft-danger:hover { background: #fecaca; }
.btn-soft-ok { background: #d1fae5; color: #047857; box-shadow: none; }
.btn-soft-ok:hover { background: #a7f3d0; }
.btn-xs { padding: 3px 8px; font-size: 12px; border-radius: 6px; }

/* ============ 表单 ============ */
.form-input {
  width: 100%; padding: 8px 12px;
  border: 1px solid var(--gray-300); border-radius: 8px;
  font-size: 13px; outline: none;
  box-sizing: border-box;
  min-width: 0;
  transition: border-color .15s, box-shadow .15s;
}
.form-input[type="datetime-local"],
.form-input[type="date"],
.form-input[type="time"] {
  min-width: 0;
  max-width: 100%;
}
.form-input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 2px #fff, 0 0 0 4px rgba(37, 99, 235, .35);
}
.form-input-sm { padding: 5px 10px; font-size: 12px; }
.cs {
  --cs-accent: var(--primary);
  --cs-border: var(--gray-300);
  --cs-border-hover: var(--gray-500);
  --cs-bg-hover: var(--gray-50);
  --cs-text: var(--gray-900);
}
.form-field { margin-bottom: 16px; display: flex; flex-direction: column; gap: 6px; }
.form-field label { font-size: 13px; font-weight: 600; }
.required { color: var(--red); }
.field-error { margin: 0; font-size: 12px; color: var(--red); }

/* ============ 弹窗 ============ */
.modal-mask {
  position: fixed; inset: 0; background: rgba(15, 23, 42, .45);
  display: flex; align-items: center; justify-content: center;
  z-index: 100; padding: 20px;
}
.modal-card {
  background: #fff; border-radius: 12px; padding: 24px;
  width: 100%; max-width: 440px;
  box-sizing: border-box;
  box-shadow: 0 10px 25px rgba(15, 23, 42, .12);
}
.modal-card h3 { margin: 0 0 8px; font-size: 18px; }
.modal-desc { margin: 0 0 18px; font-size: 13px; color: var(--gray-500); line-height: 1.6; }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 8px; }

/* ============ 时间显示框 ============ */
.time-display-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  background: #fff;
  border: 1.5px solid var(--gray-200, #e2e8f0);
  border-radius: 8px;
  cursor: pointer;
  transition: border-color .15s, box-shadow .15s;
  user-select: none;
}
.time-display-box:hover {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, .1);
}
.time-display-box.is-empty .time-display-text {
  color: var(--gray-400, #94a3b8);
}
.time-display-text {
  font-size: 14px;
  font-weight: 500;
  color: var(--gray-700, #334155);
  font-variant-numeric: tabular-nums;
}
.time-display-icon { font-size: 16px; }

/* ============ 时间选择器弹框 ============ */
.tp-card { max-width: 480px; }
.tp-section { margin-bottom: 16px; }
.tp-section-title {
  margin: 0 0 8px;
  font-size: 12px;
  font-weight: 600;
  color: var(--gray-500, #64748b);
  text-transform: uppercase;
  letter-spacing: .5px;
}

/* 日期列表 */
.tp-date-list {
  display: flex;
  gap: 6px;
  overflow-x: auto;
  padding-bottom: 4px;
}
.tp-date-item {
  flex: 0 0 auto;
  min-width: 58px;
  padding: 8px 6px;
  background: #f8fafc;
  border: 1.5px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  transition: all .15s;
}
.tp-date-item:hover {
  border-color: var(--primary);
  background: #eff6ff;
}
.tp-date-item.is-selected {
  background: var(--primary);
  border-color: var(--primary);
  color: #fff;
}
.tp-date-item.is-selected .tp-date-label,
.tp-date-item.is-selected .tp-date-weekday {
  color: #fff;
}
.tp-date-item.is-today {
  border-color: var(--primary);
}
.tp-date-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--gray-700, #334155);
}
.tp-date-weekday {
  font-size: 11px;
  color: var(--gray-500, #64748b);
}
.tp-date-today-tag {
  font-size: 9px;
  color: var(--primary);
  font-weight: 700;
}
.tp-date-item.is-selected .tp-date-today-tag { color: #fff; }

/* 小时网格 */
.tp-hour-grid {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 4px;
}
.tp-time-cell {
  padding: 8px 4px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  color: var(--gray-700, #334155);
  font-variant-numeric: tabular-nums;
  transition: all .12s;
}
.tp-time-cell:hover {
  background: #eff6ff;
  border-color: var(--primary);
}
.tp-time-cell.is-selected {
  background: var(--primary);
  border-color: var(--primary);
  color: #fff;
}

/* 分钟网格 */
.tp-minute-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 4px;
}

/* 预览 */
.tp-preview {
  padding: 10px 14px;
  background: #f1f5f9;
  border-radius: 8px;
  font-size: 13px;
  color: var(--gray-600, #475569);
  margin-bottom: 12px;
}
.tp-preview-value {
  font-weight: 600;
  color: var(--primary);
  font-variant-numeric: tabular-nums;
}

/* ============ Toast ============ */
.toast-wrap {
  position: fixed; top: 24px; right: 24px; z-index: 200;
  animation: toastIn .2s ease;
}
@keyframes toastIn { from { transform: translateX(20px); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
.toast {
  display: flex; align-items: center; gap: 8px;
  padding: 12px 18px; border-radius: 10px;
  font-size: 13px; font-weight: 500;
  box-shadow: 0 4px 12px rgba(15, 23, 42, .1);
}
.toast.success { background: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0; }
.toast.error { background: #fef2f2; color: #b91c1c; border: 1px solid #fecaca; }
.toast-icon svg { width: 18px; height: 18px; }

@media (max-width: 768px) {
  .sidebar { width: 64px; }
  .brand-text, .nav-item span, .sidebar-footer span { display: none; }
  .nav-item { justify-content: center; }
  .content { padding: 16px; }
  .course-grid { grid-template-columns: 1fr; }
  .modal-card { padding: 18px; }
  .topbar { padding: 16px; }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: .001ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: .001ms !important;
    scroll-behavior: auto !important;
  }
  .course-card:hover, .btn:hover, .brand-icon:hover { transform: none; }
}

/* ============ 课堂点名 ============ */
.badge-blue { background: #dbeafe; color: #1d4ed8; }

.rollcall-controls {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 18px;
  flex-wrap: wrap;
}
.rollcall-divider {
  width: 1px;
  height: 20px;
  background: var(--gray-200);
  margin: 0 4px;
}
.rollcall-voice-select {
  width: auto;
  min-width: 180px;
}
/* 「音色：」文字与下拉框水平排列、垂直居中，避免挤在同一列 */
.rollcall-voice-label {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}
.rollcall-hint {
  font-size: 13px;
  color: var(--gray-500);
}
.rollcall-listening-hint {
  color: #1d4ed8;
  font-weight: 500;
  animation: rollcall-pulse 1.2s infinite;
}
@keyframes rollcall-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.rollcall-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 10px;
}
.rollcall-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border: 1px solid var(--gray-200);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s ease-out;
  background: #fff;
}
.rollcall-item:hover {
  border-color: var(--accent1, #3b82f6);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}
.rollcall-current {
  border-color: #3b82f6;
  background: #eff6ff;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.25);
}
/* 自动点名进行中（非暂停）时禁止单个点名 */
.rollcall-item-locked { cursor: not-allowed; }
.rollcall-item-locked:hover {
  border-color: var(--gray-200);
  box-shadow: none;
}
.rollcall-answered {
  border-left: 3px solid #10b981;
}
.rollcall-name {
  font-weight: 600;
  font-size: 15px;
  color: var(--gray-900, #0f172a);
  flex: 1 1 auto;
  white-space: nowrap;
}
.rollcall-no {
  font-size: 13px;
  color: var(--gray-500, #64748b);
  font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  flex: none;
}
.rollcall-status {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 6px;
}
.rollcall-confirm-btn { margin-left: 2px; }
</style>
