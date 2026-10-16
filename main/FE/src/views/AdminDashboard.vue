<template>
  <div class="admin-page">
    <!-- ================= 侧边导航 ================= -->
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M22 10L12 5 2 10l10 5 10-5z" />
            <path d="M6 12v5c0 1.7 2.7 3 6 3s6-1.3 6-3v-5" />
            <path d="M22 10v6" />
          </svg>
        </div>
        <div class="brand-text">
          <div class="brand-name">学生签到系统</div>
          <div class="brand-sub">管理后台</div>
        </div>
      </div>

      <nav class="nav" aria-label="管理导航">
        <button
          type="button"
          class="nav-item"
          :class="{ active: activeTab === 'accounts' }"
          @click="activeTab = 'accounts'"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
            <circle cx="9" cy="7" r="4" />
            <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
            <path d="M16 3.13a4 4 0 0 1 0 7.75" />
          </svg>
          <span>账户管理</span>
        </button>

        <button
          type="button"
          class="nav-item"
          :class="{ active: activeTab === 'createTeacher' }"
          @click="activeTab = 'createTeacher'"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
            <circle cx="12" cy="7" r="4" />
            <line x1="19" y1="8" x2="19" y2="14" />
            <line x1="22" y1="11" x2="16" y2="11" />
          </svg>
          <span>新建教师</span>
        </button>

        <button
          type="button"
          class="nav-item"
          :class="{ active: activeTab === 'createStudent' }"
          @click="activeTab = 'createStudent'"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M22 10L12 5 2 10l10 5 10-5z" />
            <path d="M6 12v5c0 1.7 2.7 3 6 3s6-1.3 6-3v-5" />
          </svg>
          <span>新建学生</span>
        </button>

        <button
          type="button"
          class="nav-item"
          :class="{ active: activeTab === 'createCourse' }"
          @click="activeTab = 'createCourse'"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
            <line x1="12" y1="6" x2="16" y2="6" />
            <line x1="12" y1="10" x2="16" y2="10" />
          </svg>
          <span>新建课程</span>
        </button>

        <button
          type="button"
          class="nav-item"
          :class="{ active: activeTab === 'classManagement' }"
          @click="activeTab = 'classManagement'"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M3 21h18" />
            <path d="M5 21V7l8-4v18" />
            <path d="M19 21V11l-6-4" />
          </svg>
          <span>班级管理</span>
        </button>

        <button
          type="button"
          class="nav-item"
          :class="{ active: activeTab === 'updates' }"
          @click="activeTab = 'updates'"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
            <line x1="8" y1="13" x2="16" y2="13" />
            <line x1="8" y1="17" x2="13" y2="17" />
          </svg>
          <span>更新日志</span>
        </button>

        <button
          type="button"
          class="nav-item"
          :class="{ active: activeTab === 'sync' }"
          @click="activeTab = 'sync'"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M21 12a9 9 0 0 1-15.6 6.3" />
            <path d="M3 12a9 9 0 0 1 15.6-6.3" />
            <polyline points="17 3 21 6 17 9" />
            <polyline points="7 15 3 18 7 21" />
          </svg>
          <span>跨站同步</span>
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
          <div class="admin-chip">
            <div class="admin-avatar">{{ adminInitial }}</div>
            <div class="admin-meta">
              <div class="admin-name">{{ adminUsername }}</div>
              <div class="admin-role">系统管理员</div>
            </div>
          </div>
          <button type="button" class="btn btn-secondary btn-icon mobile-logout" title="退出登录" @click="logout">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
              <polyline points="16 17 21 12 16 7" />
              <line x1="21" y1="12" x2="9" y2="12" />
            </svg>
          </button>
        </div>
      </header>

      <main class="content">
        <div v-if="pageLoading" class="state-card">
          <div class="spinner" aria-hidden="true"></div>
          <p>数据加载中，请稍候…</p>
        </div>

        <div v-else-if="pageError" class="state-card">
          <p class="state-error">{{ pageError }}</p>
          <button type="button" class="btn btn-primary" @click="loadAll">重新加载</button>
        </div>

        <template v-else>
          <!-- ================= 账户管理 ================= -->
          <section v-show="activeTab === 'accounts'">
            <div class="stats-grid">
              <div class="card stat-card">
                <div class="stat-head">
                  <span class="stat-label">教师账户</span>
                  <span class="stat-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                      <circle cx="12" cy="7" r="4" />
                    </svg>
                  </span>
                </div>
                <div class="stat-number">{{ teachers.length }}</div>
                <div class="stat-caption">可登录教师账号总数</div>
              </div>

              <div class="card stat-card">
                <div class="stat-head">
                  <span class="stat-label">学生账户</span>
                  <span class="stat-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                      <path d="M22 10L12 5 2 10l10 5 10-5z" />
                      <path d="M6 12v5c0 1.7 2.7 3 6 3s6-1.3 6-3v-5" />
                    </svg>
                  </span>
                </div>
                <div class="stat-number">{{ students.length }}</div>
                <div class="stat-caption">在校学生账号总数</div>
              </div>

              <div class="card stat-card">
                <div class="stat-head">
                  <span class="stat-label">行政班级</span>
                  <span class="stat-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                      <path d="M3 21h18" />
                      <path d="M5 21V7l8-4v18" />
                      <path d="M19 21V11l-6-4" />
                    </svg>
                  </span>
                </div>
                <div class="stat-number">{{ classes.length }}</div>
                <div class="stat-caption">已建班级数量</div>
              </div>

              <div class="card stat-card">
                <div class="stat-head">
                  <span class="stat-label">课程安排</span>
                  <span class="stat-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                      <rect x="3" y="4" width="18" height="18" rx="2" />
                      <line x1="16" y1="2" x2="16" y2="6" />
                      <line x1="8" y1="2" x2="8" y2="6" />
                      <line x1="3" y1="10" x2="21" y2="10" />
                    </svg>
                  </span>
                </div>
                <div class="stat-number">{{ courses.length }}</div>
                <div class="stat-caption">已排课程总数</div>
              </div>
            </div>

            <div class="card panel-card">
              <div class="panel-header">
                <h2>账户列表</h2>
                <div class="sub-tabs" role="tablist">
                  <button
                    type="button"
                    role="tab"
                    :class="{ active: accountTab === 'teacher' }"
                    @click="accountTab = 'teacher'"
                  >教师账户</button>
                  <button
                    type="button"
                    role="tab"
                    :class="{ active: accountTab === 'student' }"
                    @click="accountTab = 'student'"
                  >学生账户</button>
                </div>
              </div>

              <div v-if="accountTab === 'student'" class="table-toolbar">
                <label class="search-field">
                  <svg class="search-icon" viewBox="0 0 24 24" aria-hidden="true">
                    <circle cx="11" cy="11" r="7" />
                    <line x1="16.5" y1="16.5" x2="21" y2="21" />
                  </svg>
                  <input
                    v-model="studentNoFilter"
                    class="search-input"
                    type="text"
                    placeholder="搜索姓名 / 学号 / 用户名 / 班级 / 手机号 / 状态"
                    autocomplete="off"
                  >
                </label>
                <span class="toolbar-count">共 {{ padCount(filteredStudents.length) }} 人</span>
              </div>

              <div class="table-wrap">
                <table v-if="accountTab === 'teacher'" class="data-table">
                  <thead>
                    <tr>
                      <th>教师姓名</th>
                      <th>登录用户名</th>
                      <th>所属院系</th>
                      <th>所属班级</th>
                      <th>手机号</th>
                      <th>状态</th>
                      <th>创建时间</th>
                      <th class="col-actions">操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="row in teachers" :key="row.user_id">
                      <td class="cell-strong">{{ row.name }}</td>
                      <td><span class="mono">{{ row.username }}</span></td>
                      <td>{{ row.department || '-' }}</td>
                      <td>{{ row.class_name || '未分配' }}</td>
                      <td>{{ row.phone || '-' }}</td>
                      <td>
                        <span class="badge" :class="row.status === 1 ? 'badge-ok' : 'badge-off'">
                          {{ row.status === 1 ? '正常' : '已禁用' }}
                        </span>
                      </td>
                      <td class="cell-muted">{{ formatDateTime(row.create_time) }}</td>
                      <td>
                        <div class="row-actions">
                          <button type="button" class="btn btn-sm btn-soft-primary" @click="openAssignModal('teacher', row.teacher_id, row.name, row.class_id)">
                            分配班级
                          </button>
                          <button type="button" class="btn btn-sm btn-soft-primary" @click="openPwdModal(row.user_id, row.username)">
                            重置密码
                          </button>
                          <button
                            type="button"
                            class="btn btn-sm"
                            :class="row.status === 1 ? 'btn-soft-warn' : 'btn-soft-success'"
                            @click="toggleStatus(row)"
                          >
                            {{ row.status === 1 ? '禁用' : '启用' }}
                          </button>
                          <button type="button" class="btn btn-sm btn-soft-danger" @click="deleteTeacher(row)">
                            删除
                          </button>
                        </div>
                      </td>
                    </tr>
                    <tr v-if="teachers.length === 0">
                      <td colspan="8" class="empty-cell">暂无教师账户，请先在「新建教师」中创建</td>
                    </tr>
                  </tbody>
                </table>

                <table v-else class="data-table">
                  <thead>
                    <tr>
                      <th>学生姓名</th>
                      <th>学号</th>
                      <th>登录用户名</th>
                      <th>班级</th>
                      <th>手机号</th>
                      <th>状态</th>
                      <th>创建时间</th>
                      <th class="col-actions">操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="row in pagedStudents" :key="row.user_id">
                      <td class="cell-strong">{{ row.name }}</td>
                      <td><span class="mono">{{ row.student_no }}</span></td>
                      <td><span class="mono">{{ row.username }}</span></td>
                      <td>{{ row.class_name || '未分班' }}</td>
                      <td>{{ row.phone || '-' }}</td>
                      <td>
                        <span class="badge" :class="row.status === 1 ? 'badge-ok' : 'badge-off'">
                          {{ row.status === 1 ? '正常' : '已禁用' }}
                        </span>
                      </td>
                      <td class="cell-muted">{{ formatDateTime(row.create_time) }}</td>
                      <td>
                        <div class="row-actions">
                          <button type="button" class="btn btn-sm btn-soft-primary" @click="openAssignModal('student', row.student_id, row.name, row.class_id)">
                            分配班级
                          </button>
                          <button type="button" class="btn btn-sm btn-soft-primary" @click="openPwdModal(row.user_id, row.username)">
                            重置密码
                          </button>
                          <button
                            type="button"
                            class="btn btn-sm"
                            :class="row.status === 1 ? 'btn-soft-warn' : 'btn-soft-success'"
                            @click="toggleStatus(row)"
                          >
                            {{ row.status === 1 ? '禁用' : '启用' }}
                          </button>
                          <button type="button" class="btn btn-sm btn-soft-danger" @click="deleteStudent(row)">
                            删除
                          </button>
                        </div>
                      </td>
                    </tr>
                    <tr v-if="filteredStudents.length === 0">
                      <td colspan="8" class="empty-cell">
                        {{ students.length === 0 ? '暂无学生账户，请先在「新建学生」中创建' : '没有学号包含该关键字的账户' }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <div v-if="accountTab === 'student' && filteredStudents.length > 0" class="table-pager">
                <span class="pager-info">第 {{ studentPage }} / {{ studentTotalPages }} 页 · 每页 {{ studentPageSize }} 条 · 共 {{ filteredStudents.length }} 条</span>
                <div class="pager-actions">
                  <button type="button" class="btn btn-sm btn-soft-primary" :disabled="studentPage <= 1" @click="studentPage--">上一页</button>
                  <button type="button" class="btn btn-sm btn-soft-primary" :disabled="studentPage >= studentTotalPages" @click="studentPage++">下一页</button>
                </div>
              </div>
            </div>
          </section>

          <!-- ================= 新建教师 ================= -->
          <section v-show="activeTab === 'createTeacher'">
            <div class="card form-card">
              <div class="form-header">
                <h2>创建教师账户</h2>
                <p>创建后教师可使用用户名和密码登录系统，角色自动设置为教师。</p>
              </div>

              <div v-if="teacherAlert.show" class="alert" :class="teacherAlert.type" role="alert">
                <span class="alert-dot" aria-hidden="true"></span>
                {{ teacherAlert.message }}
              </div>

              <div class="form-grid">
                <div class="form-field">
                  <label for="t-username">登录用户名 <span class="required">*</span></label>
                  <input id="t-username" v-model="teacherForm.username" class="form-input" type="text" placeholder="例如 teacher03" autocomplete="off">
                </div>
                <div class="form-field">
                  <label for="t-password">初始密码 <span class="required">*</span></label>
                  <input id="t-password" v-model="teacherForm.password" class="form-input" type="text" placeholder="至少 6 位，建议字母加数字">
                </div>
                <div class="form-field">
                  <label for="t-name">教师姓名 <span class="required">*</span></label>
                  <input id="t-name" v-model="teacherForm.name" class="form-input" type="text" placeholder="例如 张老师">
                </div>
                <div class="form-field">
                  <label for="t-department">所属院系</label>
                  <input id="t-department" v-model="teacherForm.department" class="form-input" type="text" placeholder="例如 计算机学院">
                </div>
                <div class="form-field span-2">
                  <label for="t-phone">手机号</label>
                  <input id="t-phone" v-model="teacherForm.phone" class="form-input" type="tel" maxlength="11" placeholder="选填，11 位手机号">
                </div>
              </div>

              <div class="form-actions">
                <button type="button" class="btn btn-secondary" @click="clearTeacherForm">清空</button>
                <button type="button" class="btn btn-primary" :disabled="teacherSubmitting" @click="submitTeacher">
                  {{ teacherSubmitting ? '创建中…' : '创建教师账户' }}
                </button>
              </div>
            </div>
          </section>

          <!-- ================= 新建学生 ================= -->
          <section v-show="activeTab === 'createStudent'">
            <div class="card form-card">
              <div class="form-header">
                <h2>创建学生账户</h2>
                <p>学号与用户名均不可与已有账户重复，班级可选，后续可调整。</p>
              </div>

              <div v-if="studentAlert.show" class="alert" :class="studentAlert.type" role="alert">
                <span class="alert-dot" aria-hidden="true"></span>
                {{ studentAlert.message }}
              </div>

              <div class="form-grid">
                <div class="form-field">
                  <label for="s-username">登录用户名 <span class="required">*</span></label>
                  <input id="s-username" v-model="studentForm.username" class="form-input" type="text" placeholder="例如 student07" autocomplete="off">
                </div>
                <div class="form-field">
                  <label for="s-password">初始密码 <span class="required">*</span></label>
                  <input id="s-password" v-model="studentForm.password" class="form-input" type="text" placeholder="至少 6 位，建议字母加数字">
                </div>
                <div class="form-field">
                  <label for="s-no">学号 <span class="required">*</span></label>
                  <input id="s-no" v-model="studentForm.student_no" class="form-input" type="text" placeholder="例如 20240007">
                </div>
                <div class="form-field">
                  <label for="s-name">学生姓名 <span class="required">*</span></label>
                  <input id="s-name" v-model="studentForm.name" class="form-input" type="text" placeholder="例如 陈九">
                </div>
                <div class="form-field">
                  <label for="s-class">所属班级</label>
                  <CustomSelect v-model="studentForm.class_id" :options="studentClassOptions" placeholder="暂不分配班级" />
                </div>
                <div class="form-field">
                  <label for="s-phone">手机号</label>
                  <input id="s-phone" v-model="studentForm.phone" class="form-input" type="tel" maxlength="11" placeholder="选填，11 位手机号">
                </div>
              </div>

              <div class="form-actions">
                <button type="button" class="btn btn-secondary" @click="clearStudentForm">清空</button>
                <button type="button" class="btn btn-primary" :disabled="studentSubmitting" @click="submitStudent">
                  {{ studentSubmitting ? '创建中…' : '创建学生账户' }}
                </button>
              </div>
            </div>
          </section>

          <!-- ================= 新建课程 ================= -->
          <section v-show="activeTab === 'createCourse'">
            <div class="card form-card">
              <div class="form-header">
                <h2>创建课程</h2>
                <p>为指定教师和班级安排课程，可一次创建多天课程；上课日期与时间段用于学生端课表展示。</p>
              </div>

              <div v-if="courseAlert.show" class="alert" :class="courseAlert.type" role="alert">
                <span class="alert-dot" aria-hidden="true"></span>
                {{ courseAlert.message }}
              </div>

              <div class="form-grid">
                <div class="form-field span-2">
                  <label for="c-name">课程名称 <span class="required">*</span></label>
                  <input id="c-name" v-model="courseForm.name" class="form-input" type="text" placeholder="例如 高等数学">
                </div>
                <div class="form-field">
                  <label for="c-teacher">授课教师 <span class="required">*</span></label>
                  <CustomSelect v-model="courseForm.teacher_id" :options="teacherOptions" placeholder="请选择教师" />
                </div>
                <div class="form-field">
                  <label for="c-class">上课班级 <span class="required">*</span></label>
                  <CustomSelect v-model="courseForm.class_id" :options="classOptions" placeholder="请选择班级" />
                </div>
                <div class="form-field">
                  <label for="c-date">上课日期</label>
                  <input
                    id="c-date"
                    ref="courseDateInput"
                    v-model="courseForm.course_date"
                    class="form-input date-input"
                    type="date"
                    @change="syncCourseEndDate"
                    @click="openDatePicker(courseDateInput)"
                  >
                </div>
                <div class="form-field">
                  <label for="c-end-date">结束日期（多天重复）</label>
                  <input
                    id="c-end-date"
                    ref="courseEndDateInput"
                    v-model="courseForm.course_end_date"
                    class="form-input date-input"
                    type="date"
                    @click="openDatePicker(courseEndDateInput)"
                  >
                </div>
                <div class="form-field">
                  <label>上课开始时间</label>
                  <div class="time-select">
                    <template v-for="item in startTimeUnits" :key="item.key">
                      <div class="time-cell">
                        <input
                          :value="courseForm[item.key]"
                          class="time-value"
                          :class="{ 'is-empty': !courseForm[item.key], 'is-error': !!timeErrors[item.key] }"
                          type="text"
                          inputmode="numeric"
                          maxlength="2"
                          placeholder="--"
                          @input="onTimeInput(item.key, $event)"
                          @blur="onTimeBlur(item.key)"
                        >
                      </div>
                      <span class="time-sep">{{ item.unit }}</span>
                    </template>
                  </div>
                </div>
                <div class="form-field">
                  <label>上课结束时间</label>
                  <div class="time-select">
                    <template v-for="item in endTimeUnits" :key="item.key">
                      <div class="time-cell">
                        <input
                          :value="courseForm[item.key]"
                          class="time-value"
                          :class="{ 'is-empty': !courseForm[item.key], 'is-error': !!timeErrors[item.key] }"
                          type="text"
                          inputmode="numeric"
                          maxlength="2"
                          placeholder="--"
                          @input="onTimeInput(item.key, $event)"
                          @blur="onTimeBlur(item.key)"
                        >
                      </div>
                      <span class="time-sep">{{ item.unit }}</span>
                    </template>
                  </div>
                </div>
              </div>

              <div class="form-actions">
                <button type="button" class="btn btn-secondary" @click="clearCourseForm">清空</button>
                <button type="button" class="btn btn-primary" :disabled="courseSubmitting" @click="submitCourse">
                  {{ courseSubmitting ? '创建中…' : '创建课程' }}
                </button>
              </div>
            </div>

            <div class="card panel-card course-panel">
              <div class="panel-header">
                <h2>已排课程</h2>
                <button type="button" class="btn btn-secondary btn-sm" @click="fetchCourses">刷新</button>
              </div>
              <div class="table-toolbar">
                <label class="search-field">
                  <svg class="search-icon" viewBox="0 0 24 24" aria-hidden="true">
                    <circle cx="11" cy="11" r="7" />
                    <line x1="16.5" y1="16.5" x2="21" y2="21" />
                  </svg>
                  <input
                    v-model="courseKeyword"
                    class="search-input"
                    type="text"
                    placeholder="搜索课程 / 教师 / 班级 / 日期 / 时间段"
                    autocomplete="off"
                  >
                </label>
                <span class="toolbar-count">共 {{ padCount(filteredCourses.length) }} 门</span>
              </div>
              <div class="table-wrap">
                <table class="data-table">
                  <thead>
                    <tr>
                      <th>课程名称</th>
                      <th>授课教师</th>
                      <th>上课班级</th>
                      <th>上课日期</th>
                      <th>时间段</th>
                      <th class="col-actions">操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="item in pagedCourses" :key="item.id">
                      <td class="cell-strong">{{ item.name }}</td>
                      <td>{{ item.teacher_name }}</td>
                      <td>{{ item.class_name }}</td>
                      <td>{{ item.course_date || '-' }}</td>
                      <td><span class="mono">{{ item.time || '-' }}</span></td>
                      <td>
                        <button type="button" class="btn btn-sm btn-soft-danger" @click="deleteCourse(item)">
                          删除
                        </button>
                      </td>
                    </tr>
                    <tr v-if="filteredCourses.length === 0">
                      <td colspan="6" class="empty-cell">
                        {{ courses.length === 0 ? '暂无课程安排' : '没有包含该关键字的课程' }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div v-if="filteredCourses.length > 0" class="table-pager">
                <span class="pager-info">第 {{ coursePage }} / {{ courseTotalPages }} 页 · 每页 {{ coursePageSize }} 条 · 共 {{ filteredCourses.length }} 条</span>
                <div class="pager-actions">
                  <button type="button" class="btn btn-sm btn-soft-primary" :disabled="coursePage <= 1" @click="coursePage--">上一页</button>
                  <button type="button" class="btn btn-sm btn-soft-primary" :disabled="coursePage >= courseTotalPages" @click="coursePage++">下一页</button>
                </div>
              </div>
            </div>
          </section>

          <!-- ================= 班级管理 ================= -->
          <section v-show="activeTab === 'classManagement'">
            <div class="card form-card form-card-wide">
              <div class="form-header">
                <h2>创建班级</h2>
                <p>新建行政班级，可同时指定班主任（班主任为已创建的教师账户）。</p>
              </div>

              <div v-if="classAlert.show" class="alert" :class="classAlert.type" role="alert">
                <span class="alert-dot" aria-hidden="true"></span>
                {{ classAlert.message }}
              </div>

              <div class="form-grid">
                <div class="form-field">
                  <label for="cl-name">班级名称 <span class="required">*</span></label>
                  <input id="cl-name" v-model="classForm.name" class="form-input" type="text" placeholder="例如 软件2403班">
                </div>
                <div class="form-field">
                  <label for="cl-grade">年级</label>
                  <input id="cl-grade" v-model="classForm.grade" class="form-input" type="text" placeholder="例如 2024级">
                </div>
                <div class="form-field span-2">
                  <label for="cl-teacher">班主任（可选）</label>
                  <CustomSelect v-model="classForm.teacher_id" :options="classTeacherOptions" placeholder="暂不指定班主任" />
                </div>
              </div>

              <div class="form-actions">
                <button type="button" class="btn btn-secondary" @click="clearClassForm">清空</button>
                <button type="button" class="btn btn-primary" :disabled="classSubmitting" @click="submitClass">
                  {{ classSubmitting ? '创建中…' : '创建班级' }}
                </button>
              </div>
            </div>

            <div class="card panel-card class-panel">
              <div class="panel-header">
                <h2>班级列表</h2>
                <button type="button" class="btn btn-secondary btn-sm" @click="fetchClasses">刷新</button>
              </div>
              <div class="table-wrap">
                <table class="data-table">
                  <thead>
                    <tr>
                      <th>班级名称</th>
                      <th>年级</th>
                      <th>班主任</th>
                      <th>学生人数</th>
                      <th class="col-actions">操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="item in classes" :key="item.id">
                      <td class="cell-strong">{{ item.name }}</td>
                      <td>{{ item.grade || '-' }}</td>
                      <td>{{ item.teacher_name || '未指定' }}</td>
                      <td>{{ studentCountByClass(item.id) }}</td>
                      <td>
                        <button type="button" class="btn btn-sm btn-soft-danger" @click="deleteClass(item)">
                          删除
                        </button>
                      </td>
                    </tr>
                    <tr v-if="classes.length === 0">
                      <td colspan="5" class="empty-cell">暂无班级，请先创建班级</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </section>

          <!-- ================= 更新日志 ================= -->
          <section v-show="activeTab === 'updates'">
            <div class="card panel-card">
              <div class="panel-header">
                <h2>更新日志</h2>
                <button type="button" class="btn btn-primary btn-sm" @click="openUpdateModal()">新增更新</button>
              </div>

              <div class="table-toolbar">
                <label class="search-field">
                  <svg class="search-icon" viewBox="0 0 24 24" aria-hidden="true">
                    <circle cx="11" cy="11" r="7" />
                    <line x1="16.5" y1="16.5" x2="21" y2="21" />
                  </svg>
                  <input
                    v-model="updateKeyword"
                    class="search-input"
                    type="text"
                    placeholder="搜索类型 / 更新内容"
                    autocomplete="off"
                  >
                </label>
                <input
                  ref="updateFilterDateInput"
                  v-model="updateDate"
                  class="form-input date-input update-date-filter"
                  type="date"
                  aria-label="按日期查找"
                  @click="openDatePicker(updateFilterDateInput)"
                >
                <span class="toolbar-count">共 {{ padCount(filteredUpdates.length) }} 条</span>
              </div>

              <div class="table-wrap">
                <table class="data-table">
                  <thead>
                    <tr>
                      <th class="col-update-tag">类型</th>
                      <th>更新内容</th>
                      <th class="col-update-date">日期</th>
                      <th class="col-actions">操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="row in pagedUpdates" :key="row.update_id">
                      <td>
                        <span class="badge" :class="updateTagClass(row.tag)">{{ row.tag }}</span>
                      </td>
                      <td class="cell-strong">{{ row.content }}</td>
                      <td class="cell-muted">{{ row.created_at || '-' }}</td>
                      <td>
                        <div class="row-actions">
                          <button type="button" class="btn btn-sm btn-soft-primary" @click="openUpdateModal(row)">
                            编辑
                          </button>
                          <button type="button" class="btn btn-sm btn-soft-danger" @click="deleteUpdate(row)">
                            删除
                          </button>
                        </div>
                      </td>
                    </tr>
                    <tr v-if="filteredUpdates.length === 0">
                      <td colspan="4" class="empty-cell">
                        {{ updateEmptyText }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <div v-if="filteredUpdates.length > 0" class="table-pager">
                <span class="pager-info">第 {{ updatePage }} / {{ updateTotalPages }} 页 · 每页 {{ updatePageSize }} 条 · 共 {{ filteredUpdates.length }} 条</span>
                <div class="pager-actions">
                  <button type="button" class="btn btn-sm btn-soft-primary" :disabled="updatePage <= 1" @click="updatePage--">上一页</button>
                  <button type="button" class="btn btn-sm btn-soft-primary" :disabled="updatePage >= updateTotalPages" @click="updatePage++">下一页</button>
                </div>
              </div>
            </div>
          </section>

          <!-- ================= 跨站同步 ================= -->
          <section v-show="activeTab === 'sync'" class="sync-page">
            <div class="stats-grid">
              <div class="card stat-card">
                <div class="stat-head">
                  <span class="stat-label">待发送</span>
                  <span class="stat-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                      <path d="M12 19V5M5 12l7-7 7 7" />
                    </svg>
                  </span>
                </div>
                <div class="stat-number">{{ syncStatus?.pending_outbox ?? 0 }}</div>
                <div class="stat-caption">等待推送或重试的事件</div>
              </div>

              <div class="card stat-card">
                <div class="stat-head">
                  <span class="stat-label">发送失败</span>
                  <span class="stat-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                      <path d="M12 5v14M5 12l7 7 7-7" />
                    </svg>
                  </span>
                </div>
                <div class="stat-number">{{ syncOutboxFailed }}</div>
                <div class="stat-caption">超过重试上限，需人工重试</div>
              </div>

              <div class="card stat-card">
                <div class="stat-head">
                  <span class="stat-label">同步记录</span>
                  <span class="stat-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                      <path d="M4 7h16M4 12h16M4 17h10" />
                    </svg>
                  </span>
                </div>
                <div class="stat-number">{{ syncStatus?.cross_record?.total ?? 0 }}</div>
                <div class="stat-caption">异地签到入库总量 · 作废 {{ syncStatus?.cross_record?.voided ?? 0 }}</div>
              </div>

              <div class="card stat-card">
                <div class="stat-head">
                  <span class="stat-label">待处理冲突</span>
                  <span class="stat-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                      <path d="M12 9v4M12 17h.01" />
                      <path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z" />
                    </svg>
                  </span>
                </div>
                <div class="stat-number">{{ syncStatus?.pending_conflicts ?? 0 }}</div>
                <div class="stat-caption">同一门课多站签到，已按最早时间裁决</div>
              </div>
            </div>

            <div class="sync-toolbar">
              <div class="sync-site">
                <span class="sync-site-dot" :class="{ 'sync-site-dot-off': !syncStatus }" aria-hidden="true"></span>
                <span class="sync-site-code mono">{{ syncStatus?.site_code || '-' }}</span>
                <span class="sync-site-meta">{{ syncStatus?.site_name || '未配置站点名称' }} · 契约 v{{ syncStatus?.schema_version || '-' }}</span>
              </div>
              <div class="sync-toolbar-actions">
                <button type="button" class="btn btn-primary btn-sm" :disabled="syncBusy || syncCooldown" @click="triggerSync('sync')">立即同步</button>
                <button type="button" class="btn btn-soft-primary btn-sm" :disabled="syncBusy || syncCooldown" @click="triggerSync('reconcile')">执行对账</button>
                <button
                  type="button"
                  class="btn btn-sm"
                  :class="autoConnecting ? 'btn-soft-danger' : 'btn-soft-primary'"
                  :disabled="(!autoConnecting && syncBusy) || syncCooldown"
                  @click="toggleConnect"
                >{{ autoConnecting ? `连接中 ${autoConnectElapsed}s（点击停止）` : "连接对端" }}</button>
                <button type="button" class="btn btn-secondary btn-sm" :disabled="syncLoading || syncCooldown" @click="refreshSync">刷新</button>
              </div>
            </div>

            <div v-if="lastSyncError" class="sync-alert sync-alert-danger">
              <span class="sync-alert-icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 9v4M12 17h.01" />
                  <path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z" />
                </svg>
              </span>
              <div class="sync-alert-body">
                <p class="sync-alert-title">同步状态加载失败</p>
                <p class="sync-alert-text">{{ lastSyncError }}</p>
              </div>
            </div>

            <div v-if="offlinePeers.length" class="sync-alert sync-alert-warn">
              <span class="sync-alert-icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 9v4M12 17h.01" />
                  <path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z" />
                </svg>
              </span>
              <div class="sync-alert-body">
                <p class="sync-alert-title">部分对端站点当前不可达</p>
                <ul class="sync-alert-list">
                  <li v-for="peer in offlinePeers" :key="peer.code">
                    <span class="sync-peer-tag">{{ peer.name }}</span>
                    <span class="sync-alert-text">{{ peer.error || '连接失败，原因未知' }}</span>
                  </li>
                </ul>
              </div>
            </div>

            <!-- 对端站点 -->
            <div class="card panel-card">
              <div class="panel-header">
                <h2>对端站点</h2>
                <span class="toolbar-count">共 {{ syncPeers.length }} 个</span>
              </div>
              <div class="table-wrap">
                <table class="data-table">
                  <thead>
                    <tr>
                      <th>编码</th>
                      <th>名称</th>
                      <th>地址</th>
                      <th>连通性</th>
                      <th>对端时间</th>
                      <th>同步进度</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="peer in syncPeers" :key="peer.code">
                      <td class="mono">{{ peer.code }}</td>
                      <td class="cell-strong">{{ peer.site_name || peer.name }}</td>
                      <td class="cell-muted">{{ peer.base_url }}</td>
                      <td>
                        <span class="badge" :class="peer.online ? 'badge-ok' : 'badge-off'">
                          {{ peer.online ? '在线' : '离线' }}
                        </span>
                      </td>
                      <td class="mono">{{ peer.server_time || '-' }}</td>
                      <td>
                        <span
                          class="sync-progress"
                          :class="{ 'sync-progress-idle': !syncStatus?.cursors?.[peer.code] }"
                        >{{ cursorText(peer.code) }}</span>
                      </td>
                    </tr>
                    <tr v-if="!syncPeers.length">
                      <td colspan="6" class="empty-cell">未配置对端站点，请检查 main/BE/sync/config.py</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- 发送队列 -->
            <div class="card panel-card">
              <div class="panel-header">
                <h2>发送队列</h2>
                <span class="toolbar-count">最近 {{ outboxItems.length }} 条</span>
              </div>
              <div class="table-wrap">
                <table class="data-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>目标站点</th>
                      <th>事件</th>
                      <th>状态</th>
                      <th>重试</th>
                      <th>最近错误</th>
                      <th class="col-actions">操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="row in outboxItems" :key="row.id">
                      <td class="mono">{{ row.id }}</td>
                      <td class="cell-strong">{{ row.target_peer_name || row.target_peer }}</td>
                      <td class="cell-muted">{{ eventTypeText(row.event_type) }}</td>
                      <td>
                        <span class="badge" :class="outboxBadgeClass(row.status)">{{ outboxStatusText(row.status) }}</span>
                      </td>
                      <td class="mono">{{ row.retry_count }}</td>
                      <td class="cell-muted sync-err" :title="row.last_error || ''">{{ row.last_error || '-' }}</td>
                      <td>
                        <div class="row-actions">
                          <button
                            v-if="Number(row.status) === 2"
                            type="button"
                            class="btn btn-sm btn-soft-primary"
                            :disabled="syncBusy"
                            @click="retryOutbox(row.id)"
                          >重试</button>
                          <span v-else class="cell-muted">-</span>
                        </div>
                      </td>
                    </tr>
                    <tr v-if="!outboxItems.length">
                      <td colspan="7" class="empty-cell">队列为空，暂无待推送事件</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- 跨站冲突 -->
            <div class="card panel-card">
              <div class="panel-header">
                <h2>跨站冲突</h2>
                <span class="toolbar-count">共 {{ conflictTotal }} 条 · 待处理 {{ conflictPending }}</span>
              </div>

              <div class="table-toolbar">
                <!-- 「全部」按钮只在「待处理」视图有意义；隐藏时用 visibility 占位，
                     保证切换到其他状态时这一行不会重新排版 -->
                <div class="toolbar-left" :class="{ 'is-hidden': conflictState !== 0 }">
                  <button
                    type="button"
                    class="btn btn-soft-primary btn-sm"
                    :disabled="syncBusy || !conflictItems.length"
                    @click="batchHandleConflicts('resolve', true)"
                  >全部已裁决</button>
                  <button
                    type="button"
                    class="btn btn-soft-danger btn-sm"
                    :disabled="syncBusy || !conflictItems.length"
                    @click="batchHandleConflicts('ignore', true)"
                  >全部忽略</button>
                </div>
                <label class="search-field">
                  <svg class="search-icon" viewBox="0 0 24 24" aria-hidden="true">
                    <circle cx="11" cy="11" r="7" />
                    <line x1="16.5" y1="16.5" x2="21" y2="21" />
                  </svg>
                  <input
                    v-model="conflictKeyword"
                    class="search-input"
                    type="text"
                    placeholder="搜索学号 / 班级键 / 日期"
                    autocomplete="off"
                    @keyup.enter="loadSyncConflicts"
                  >
                </label>
                <div class="conflict-state-select">
                  <CustomSelect
                    v-model="conflictState"
                    :options="conflictStateOptions"
                    placeholder="全部状态"
                    size="sm"
                    @change="loadSyncConflicts"
                  />
                </div>
                <button type="button" class="btn btn-secondary btn-sm" :disabled="syncLoading" @click="loadSyncConflicts">查询</button>
                <span class="toolbar-count">已选 {{ conflictSelected.length }} 条</span>
                <div class="row-actions">
                  <button
                    type="button"
                    class="btn btn-soft-primary btn-sm"
                    :disabled="syncBusy || !conflictSelected.length"
                    @click="batchHandleConflicts('resolve')"
                  >批量已裁决</button>
                  <button
                    type="button"
                    class="btn btn-soft-danger btn-sm"
                    :disabled="syncBusy || !conflictSelected.length"
                    @click="batchHandleConflicts('ignore')"
                  >批量忽略</button>
                </div>
              </div>

              <div class="table-wrap">
                <table class="data-table">
                  <thead>
                    <tr>
                      <th class="col-check">
                        <input
                          type="checkbox"
                          :checked="conflictAllSelected"
                          :disabled="!conflictItems.length"
                          @change="toggleConflictAll"
                        >
                      </th>
                      <th>对齐键</th>
                      <th>获胜方</th>
                      <th>落败记录</th>
                      <th>状态</th>
                      <th>发生时间</th>
                      <th class="col-actions">操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="row in conflictItems" :key="row.id">
                      <td class="col-check">
                        <input
                          type="checkbox"
                          :checked="conflictSelected.includes(row.id)"
                          @change="toggleConflictRow(row.id)"
                        >
                      </td>
                      <td class="cell-muted mono">{{ row.align_key }}</td>
                      <td>
                        <span class="badge badge-new">{{ row.winner_site_name || row.winner_site }}</span>
                      </td>
                      <td class="cell-muted">{{ conflictLoserText(row) }}</td>
                      <td>
                        <span class="badge" :class="Number(row.state) === 0 ? 'badge-opt' : 'badge-ok'">
                          {{ conflictStateText(row.state) }}
                        </span>
                      </td>
                      <td class="cell-muted">{{ row.created_at || '-' }}</td>
                      <td>
                        <div class="row-actions">
                          <template v-if="Number(row.state) === 0">
                            <button type="button" class="btn btn-sm btn-soft-primary" :disabled="syncBusy" @click="handleConflict(row.id, 'resolve')">已裁决</button>
                            <button type="button" class="btn btn-sm btn-soft-danger" :disabled="syncBusy" @click="handleConflict(row.id, 'ignore')">忽略</button>
                          </template>
                          <span v-else class="cell-muted">{{ row.handled_at || '已处理' }}</span>
                        </div>
                      </td>
                    </tr>
                    <tr v-if="!conflictItems.length">
                      <td colspan="7" class="empty-cell">暂无冲突</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </section>
        </template>
      </main>
    </div>

    <!-- ================= 重置密码弹窗 ================= -->
    <div v-if="pwdModal.show" class="modal-mask" @click.self="closePwdModal">
      <div class="modal-card" role="dialog" aria-modal="true" aria-labelledby="pwd-title">
        <h3 id="pwd-title">重置密码</h3>
        <p class="modal-desc">
          将为账户 <span class="mono">{{ pwdModal.username }}</span> 设置新密码，保存后立即生效。
        </p>
        <div class="form-field">
          <label for="new-pwd">新密码 <span class="required">*</span></label>
          <input
            id="new-pwd"
            ref="pwdInputRef"
            v-model="pwdModal.password"
            class="form-input"
            type="text"
            placeholder="请输入至少 6 位新密码"
            @keyup.enter="confirmResetPwd"
          >
          <p v-if="pwdModal.error" class="field-error">{{ pwdModal.error }}</p>
        </div>
        <div class="modal-actions">
          <button type="button" class="btn btn-secondary" @click="closePwdModal">取消</button>
          <button type="button" class="btn btn-primary" :disabled="pwdModal.submitting" @click="confirmResetPwd">
            {{ pwdModal.submitting ? '保存中…' : '确认重置' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ================= 分配班级弹窗 ================= -->
    <div v-if="assignModal.show" class="modal-mask" @click.self="closeAssignModal">
      <div class="modal-card" role="dialog" aria-modal="true" aria-labelledby="assign-title">
        <h3 id="assign-title">分配班级</h3>
        <p class="modal-desc">
          为{{ assignModal.targetType === 'teacher' ? '教师' : '学生' }}
          <span class="mono">{{ assignModal.targetName }}</span>选择所属班级，选择「未分配」可解除绑定。
        </p>
        <div class="form-field">
          <label for="assign-class">所属班级</label>
          <CustomSelect v-model="assignModal.class_id" :options="assignClassOptions" placeholder="未分配" />
          <p v-if="assignModal.error" class="field-error">{{ assignModal.error }}</p>
        </div>
        <div class="modal-actions">
          <button type="button" class="btn btn-secondary" @click="closeAssignModal">取消</button>
          <button type="button" class="btn btn-primary" :disabled="assignModal.submitting" @click="confirmAssignClass">
            {{ assignModal.submitting ? '保存中…' : '确认分配' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ================= 更新日志编辑弹窗 ================= -->
    <div v-if="updateModal.show" class="modal-mask" @click.self="closeUpdateModal">
      <div class="modal-card" role="dialog" aria-modal="true" aria-labelledby="update-title">
        <h3 id="update-title">{{ updateModal.update_id ? '编辑更新日志' : '新增更新日志' }}</h3>
        <p class="modal-desc">
          类型标记本次改动属于「新增 / 优化 / 修复」，日期决定该日志归入哪一天的更新记录。
        </p>
        <div class="form-field">
          <label>类型 <span class="required">*</span></label>
          <CustomSelect v-model="updateModal.tag" :options="updateTagOptions" placeholder="请选择类型" />
        </div>
        <div class="form-field">
          <label for="update-date">日期 <span class="required">*</span></label>
          <input
            id="update-date"
            ref="updateDateInput"
            v-model="updateModal.date"
            class="form-input date-input"
            type="date"
            @click="openDatePicker(updateDateInput)"
          >
        </div>
        <div class="form-field">
          <label for="update-content">更新内容 <span class="required">*</span></label>
          <textarea
            id="update-content"
            v-model="updateModal.content"
            class="form-textarea"
            rows="4"
            maxlength="500"
            placeholder="请输入本次更新的内容（不超过 500 字）"
          ></textarea>
        </div>
        <p v-if="updateModal.error" class="field-error">{{ updateModal.error }}</p>
        <div class="modal-actions">
          <button type="button" class="btn btn-secondary" @click="closeUpdateModal">取消</button>
          <button type="button" class="btn btn-primary" :disabled="updateModal.submitting" @click="submitUpdate">
            {{ updateModal.submitting ? '保存中…' : '保存' }}
          </button>
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
import { reactive, ref, computed, watch, onMounted, nextTick, type Ref } from "vue"
import { useRouter } from "vue-router"
import request from "../api/request"
import CustomSelect from "../components/CustomSelect.vue"
import { errorMessage, isAuthError } from "../utils/error"
import { formatDateTime } from "../utils/format"

// =====================================================
// 类型定义
// =====================================================

interface TeacherRow {
  teacher_id: string
  user_id: string
  name: string
  department: string | null
  class_id: string | null
  class_name: string | null
  username: string
  phone: string | null
  status: number
  create_time?: string | null
}

interface StudentRow {
  student_id: string
  user_id: string
  student_no: string
  name: string
  class_id: string | null
  class_name: string | null
  username: string
  phone: string | null
  status: number
  create_time?: string | null
}

interface ClassRow {
  id: string
  name: string
  grade: string | null
  teacher_name: string | null
}

interface CourseRow {
  id: string
  name: string
  teacher_id: string
  class_id: string
  course_date: string | null
  time: string | null
  teacher_name: string
  class_name: string
}

interface UpdateRow {
  update_id: number
  tag: string
  content: string
  created_at?: string | null
}

interface ApiResult<T> {
  code: number
  message?: string
  data?: T
}

// -----------------------------------------------------
// 跨站同步：后端 /api/admin/sync/* 返回结构
// -----------------------------------------------------

interface SyncPeerStatus {
  code: string
  name: string
  base_url: string
  online: boolean
  site_name: string | null
  server_time: string | null
  error: string | null
}

interface SyncCursorRow {
  peer_code: string
  last_seq: number
  last_pull_at: string | null
  last_success_at: string | null
  fail_count: number
  last_error: string | null
}

interface SyncStatus {
  site_code: string
  site_name: string
  schema_version: string
  peers: SyncPeerStatus[]
  cursors: Record<string, SyncCursorRow>
  outbox: Record<string, number>
  pending_outbox: number
  pending_conflicts: number
  cross_record: { total: number; voided: number }
}

interface SyncOutboxRow {
  id: number
  target_peer: string
  target_peer_name?: string
  event_id: string
  event_type: string
  status: number
  retry_count: number
  next_retry_at: string | null
  last_error: string | null
  created_at: string | null
  sent_at: string | null
}

interface SyncConflictLoserEntry {
  site?: string
  site_name?: string
  record_id?: string
  sign_time?: string
  attendance_status?: number | null
  status_text?: string | null
}

// 后端 loser_json 存的是 { winner, losers[] } 嵌套结构
interface SyncConflictLoser {
  winner?: SyncConflictLoserEntry
  losers?: SyncConflictLoserEntry[]
}

interface SyncConflictRow {
  id: string
  align_key: string
  winner_record_id: string | null
  winner_site: string
  winner_site_name?: string
  loser_json: SyncConflictLoser | null
  state: number
  created_at: string | null
  handled_by: string | null
  handled_at: string | null
}

type TabKey = "accounts" | "createTeacher" | "createStudent" | "createCourse" | "classManagement" | "updates" | "sync"
type AlertType = "success" | "error"

interface FormAlert {
  show: boolean
  type: AlertType
  message: string
}

// =====================================================
// 页面状态
// =====================================================

const router = useRouter()

const activeTab = ref<TabKey>("accounts")
const accountTab = ref<"teacher" | "student">("teacher")
// 学生学号筛选关键字（支持模糊匹配）
const studentNoFilter = ref("")

const pageLoading = ref(true)
const pageError = ref("")

const adminUsername = ref("管理员")
const adminInitial = ref("管")

const teachers = ref<TeacherRow[]>([])
const students = ref<StudentRow[]>([])
// 学生模糊筛选：姓名 / 学号 / 用户名 / 班级 / 手机号 / 状态 任一包含关键字即显示
const filteredStudents = computed(() => {
  const keyword = studentNoFilter.value.trim().toLowerCase()
  if (!keyword) return students.value
  return students.value.filter((item) => {
    const statusText = item.status === 1 ? "正常 已启用" : "已禁用 禁用"
    return [item.name, item.student_no, item.username, item.class_name, item.phone, statusText].some(
      (field) => (field || "").toLowerCase().includes(keyword)
    )
  })
})
// 前端分页：数据量大时只渲染当前页，避免一次性渲染全部行导致卡顿
const studentPageSize = 20
const studentPage = ref(1)
const studentTotalPages = computed(() =>
  Math.max(1, Math.ceil(filteredStudents.value.length / studentPageSize))
)
const pagedStudents = computed(() => {
  const start = (studentPage.value - 1) * studentPageSize
  return filteredStudents.value.slice(start, start + studentPageSize)
})
// 筛选条件变化时回到第一页；数据减少导致页码越界时自动回退
watch(studentNoFilter, () => {
  studentPage.value = 1
})
watch(studentTotalPages, (total) => {
  if (studentPage.value > total) studentPage.value = total
})
// 人数显示：不足两位时补前导 0（如 5 → 05）
function padCount(value: number): string {
  return String(value).padStart(2, "0")
}
const classes = ref<ClassRow[]>([])
const courses = ref<CourseRow[]>([])
// 已排课程模糊筛选：课程名称 / 授课教师 / 上课班级 / 上课日期 / 时间段 任一包含关键字即显示
const courseKeyword = ref("")
const filteredCourses = computed(() => {
  const keyword = courseKeyword.value.trim().toLowerCase()
  if (!keyword) return courses.value
  return courses.value.filter((item) =>
    [item.name, item.teacher_name, item.class_name, item.course_date, item.time].some((field) =>
      (field || "").toLowerCase().includes(keyword)
    )
  )
})
// 已排课程前端分页
const coursePageSize = 20
const coursePage = ref(1)
const courseTotalPages = computed(() =>
  Math.max(1, Math.ceil(filteredCourses.value.length / coursePageSize))
)
const pagedCourses = computed(() => {
  const start = (coursePage.value - 1) * coursePageSize
  return filteredCourses.value.slice(start, start + coursePageSize)
})
watch(courseKeyword, () => {
  coursePage.value = 1
})
watch(courseTotalPages, (total) => {
  if (coursePage.value > total) coursePage.value = total
})

// 更新日志：类型 / 内容 模糊筛选
const updates = ref<UpdateRow[]>([])
const updateKeyword = ref("")
// 按天查找：默认今天，只看所选日期当天的更新
const updateDate = ref(todayText())
// 更新日志：先按日期过滤，再按关键字（类型 / 内容 / 日期）模糊过滤
const filteredUpdates = computed(() => {
  const keyword = updateKeyword.value.trim().toLowerCase()
  return updates.value.filter((item) => {
    if (updateDate.value && (item.created_at || "").slice(0, 10) !== updateDate.value) {
      return false
    }
    if (!keyword) return true
    return [item.tag, item.content, item.created_at].some((field) =>
      (field || "").toLowerCase().includes(keyword)
    )
  })
})
// 空态文案：区分「无数据」「今天暂无更新」「该日期暂无更新」「无关键字结果」
const updateEmptyText = computed(() => {
  if (updates.value.length === 0) {
    return "暂无更新日志，点击右上角「新增更新」添加"
  }
  if (updateKeyword.value.trim()) {
    return "没有包含该关键字的更新日志"
  }
  if (updateDate.value === todayText()) {
    return "今天暂无更新"
  }
  return updateDate.value ? `${updateDate.value} 暂无更新` : "暂无更新日志"
})
// 更新日志前端分页
const updatePageSize = 20
const updatePage = ref(1)
const updateTotalPages = computed(() =>
  Math.max(1, Math.ceil(filteredUpdates.value.length / updatePageSize))
)
const pagedUpdates = computed(() => {
  const start = (updatePage.value - 1) * updatePageSize
  return filteredUpdates.value.slice(start, start + updatePageSize)
})
watch(updateKeyword, () => {
  updatePage.value = 1
})
watch(updateDate, () => {
  updatePage.value = 1
})
watch(updateTotalPages, (total) => {
  if (updatePage.value > total) updatePage.value = total
})
const updateTagOptions = [
  { label: "新增", value: "新增" },
  { label: "优化", value: "优化" },
  { label: "修复", value: "修复" }
]

// =====================================================
// 跨站同步（管理页）
// =====================================================

const syncStatus = ref<SyncStatus | null>(null)
const outboxItems = ref<SyncOutboxRow[]>([])
const conflictItems = ref<SyncConflictRow[]>([])
const conflictTotal = ref(0)
const conflictPending = ref(0)
// 状态筛选：0 待处理 / 1 已裁决 / 2 已忽略 / -1 全部
const conflictStateOptions = [
  { label: "待处理", value: 0 },
  { label: "已裁决", value: 1 },
  { label: "已忽略", value: 2 },
  { label: "全部状态", value: -1 }
]
const conflictState = ref<number | string>(0)
const conflictKeyword = ref("")
const conflictSelected = ref<string[]>([])
const conflictAllSelected = computed(
  () => conflictItems.value.length > 0 && conflictSelected.value.length === conflictItems.value.length
)
const syncLoading = ref(false)
const syncBusy = ref(false)
const lastSyncError = ref("")

// 工具栏防连点：四个按钮（立即同步 / 执行对账 / 连接对端 / 刷新）任一次点击后
// 统一冷却 3s，避免用户反复点击重复触发请求。
const SYNC_COOLDOWN_MS = 3_000
const syncCooldown = ref(false)
let syncCooldownTimer: ReturnType<typeof setTimeout> | undefined

function startSyncCooldown(): void {
  syncCooldown.value = true
  if (syncCooldownTimer !== undefined) window.clearTimeout(syncCooldownTimer)
  syncCooldownTimer = window.setTimeout(() => {
    syncCooldown.value = false
    syncCooldownTimer = undefined
  }, SYNC_COOLDOWN_MS)
}

// 「连接对端」：手动点击或打开同步页时进入有界自动重试 —— 每 5s 连一次，
// 累计满 30s 仍未全部连通就自动取消，需用户重新点击。
const autoConnecting = ref(false)
const autoConnectElapsed = ref(0)
const AUTO_CONNECT_INTERVAL = 5_000
const AUTO_CONNECT_WINDOW = 30_000
let autoConnectTimer: ReturnType<typeof setTimeout> | undefined
let autoConnectTick: ReturnType<typeof setInterval> | undefined
let autoConnectStartedAt = 0

const syncPeers = computed(() => syncStatus.value?.peers || [])
// 发送失败数：outbox 统计按状态号分组，2 = OUTBOX_FAILED
const syncOutboxFailed = computed(() => Number(syncStatus.value?.outbox?.["2"] ?? 0))
// 离线对端列表：逐条展示离线原因，便于排查 base_url / token 配置
const offlinePeers = computed(() => syncPeers.value.filter((peer) => !peer.online))

const classOptions = computed(() =>
  classes.value.map((item) => ({
    label: item.grade ? `${item.name}（${item.grade}）` : item.name,
    value: item.id
  }))
)
const teacherOptions = computed(() =>
  teachers.value.map((item) => ({
    label: item.department ? `${item.name}（${item.department}）` : item.name,
    value: item.teacher_id
  }))
)
const studentClassOptions = computed(() => [{ label: "暂不分配班级", value: "" }, ...classOptions.value])
const classTeacherOptions = computed(() => [{ label: "暂不指定班主任", value: "" }, ...teacherOptions.value])
const assignClassOptions = computed(() => [{ label: "未分配", value: "" }, ...classOptions.value])

const tabMeta: Record<TabKey, { title: string; desc: string }> = {
  accounts: { title: "账户管理", desc: "管理教师与学生账户，可重置密码、分配班级、启用或禁用账号" },
  createTeacher: { title: "新建教师", desc: "创建教师登录账号并维护基本信息" },
  createStudent: { title: "新建学生", desc: "创建学生登录账号，学号全局唯一" },
  createCourse: { title: "新建课程", desc: "为教师与班级安排课程及上课时间" },
  classManagement: { title: "班级管理", desc: "创建与删除班级，维护班级基础信息" },
  updates: { title: "更新日志", desc: "维护登录页展示的更新日志，支持按类型 / 内容模糊搜索" },
  sync: { title: "跨站同步", desc: "查看同步状态与对端连通性，处理发送队列与跨站冲突" }
}

// =====================================================
// 表单状态
// =====================================================

const teacherForm = reactive({
  username: "",
  password: "",
  name: "",
  department: "",
  phone: ""
})

const studentForm = reactive({
  username: "",
  password: "",
  student_no: "",
  name: "",
  class_id: "",
  phone: ""
})

const courseForm = reactive({
  name: "",
  teacher_id: "",
  class_id: "",
  course_date: "",
  course_end_date: "",
  start_hour: "",
  start_minute: "",
  end_hour: "",
  end_minute: ""
})

type TimeFieldKey = "start_hour" | "start_minute" | "end_hour" | "end_minute"

interface TimeUnitConfig {
  key: TimeFieldKey
  unit: string
}

const startTimeUnits: TimeUnitConfig[] = [
  { key: "start_hour", unit: "时" },
  { key: "start_minute", unit: "分" }
]

const endTimeUnits: TimeUnitConfig[] = [
  { key: "end_hour", unit: "时" },
  { key: "end_minute", unit: "分" }
]

const TIME_FIELD_KEYS: TimeFieldKey[] = ["start_hour", "start_minute", "end_hour", "end_minute"]

// 各时间位的取值上限：小时 00-23，分 00-59
const TIME_MAX: Record<TimeFieldKey, number> = {
  start_hour: 23,
  start_minute: 59,
  end_hour: 23,
  end_minute: 59
}

const timeErrors = reactive<Record<TimeFieldKey, string>>({
  start_hour: "",
  start_minute: "",
  end_hour: "",
  end_minute: ""
})

const courseDateInput = ref<HTMLInputElement>()
const courseEndDateInput = ref<HTMLInputElement>()

const teacherSubmitting = ref(false)
const studentSubmitting = ref(false)
const courseSubmitting = ref(false)
const classSubmitting = ref(false)

const teacherAlert = ref<FormAlert>({ show: false, type: "success", message: "" })
const studentAlert = ref<FormAlert>({ show: false, type: "success", message: "" })
const courseAlert = ref<FormAlert>({ show: false, type: "success", message: "" })
const classAlert = ref<FormAlert>({ show: false, type: "success", message: "" })

// =====================================================
// 重置密码弹窗
// =====================================================

const pwdInputRef = ref<HTMLInputElement>()

const pwdModal = reactive({
  show: false,
  user_id: "",
  username: "",
  password: "",
  error: "",
  submitting: false
})

// =====================================================
// 分配班级弹窗（教师 / 学生共用）
// =====================================================

const assignModal = reactive({
  show: false,
  targetType: "teacher" as "teacher" | "student",
  targetId: "",
  targetName: "",
  class_id: "",
  submitting: false,
  error: ""
})

// =====================================================
// 更新日志编辑弹窗
// =====================================================

const updateDateInput = ref<HTMLInputElement>()
// 更新日志列表「按天查找」的日期输入框
const updateFilterDateInput = ref<HTMLInputElement>()

const updateModal = reactive({
  show: false,
  update_id: 0,
  tag: "新增",
  date: "",
  content: "",
  error: "",
  submitting: false
})

// =====================================================
// 创建班级表单
// =====================================================

const classForm = reactive({
  name: "",
  grade: "",
  teacher_id: ""
})

// =====================================================
// 全局提示
// =====================================================

const toast = reactive({
  show: false,
  type: "success" as AlertType,
  message: ""
})

let toastTimer: ReturnType<typeof setTimeout> | undefined

function showToast(message: string, type: AlertType = "success") {
  toast.message = message
  toast.type = type
  toast.show = true
  if (toastTimer) {
    clearTimeout(toastTimer)
  }
  toastTimer = setTimeout(() => {
    toast.show = false
  }, 2800)
}

function setAlert(alert: Ref<FormAlert>, type: AlertType, message: string) {
  alert.value = { show: true, type, message }
}

// =====================================================
// 工具函数
// =====================================================

function todayText(): string {
  const now = new Date()
  const month = String(now.getMonth() + 1).padStart(2, "0")
  const day = String(now.getDate()).padStart(2, "0")
  return `${now.getFullYear()}-${month}-${day}`
}

function validPhone(phone: string): boolean {
  return phone === "" || /^1\d{10}$/.test(phone)
}

// 拼接上课时间段：开始/结束时间均为 HH:mm:ss，结束须晚于开始；否则返回 null
function combineTimeRange(start: string, end: string): string | null {
  if (!start || !end || end <= start) return null
  return `${start}-${end}`
}

// 由时、分拼接为 HH:mm；任一未填返回 null
function buildTimeString(hour: string, minute: string): string | null {
  if (!hour || !minute) return null
  return `${hour}:${minute}`
}

// 仅保留两位数字并实时校验范围
function onTimeInput(key: TimeFieldKey, event: Event): void {
  const input = event.target as HTMLInputElement
  const digits = input.value.replace(/\D/g, "").slice(0, 2)
  courseForm[key] = digits
  input.value = digits
  checkTimeField(key)
}

// 失焦时把个位数补零（如 5 -> 05）并再次校验
function onTimeBlur(key: TimeFieldKey): void {
  if (/^\d$/.test(courseForm[key])) {
    courseForm[key] = `0${courseForm[key]}`
  }
  checkTimeField(key)
}

// 校验单个时间位是否在合法范围内
function checkTimeField(key: TimeFieldKey): void {
  const value = courseForm[key]
  if (value === "") {
    timeErrors[key] = ""
    return
  }
  timeErrors[key] = Number(value) <= TIME_MAX[key] ? "" : `范围 00-${TIME_MAX[key]}`
}

// 结束日期默认跟随上课日期（仅在结束日期为空或早于新上课日期时更新）
function syncCourseEndDate(): void {
  if (!courseForm.course_end_date || courseForm.course_end_date < courseForm.course_date) {
    courseForm.course_end_date = courseForm.course_date
  }
}

// 点击日期框任意位置唤起原生日期选择器
function openDatePicker(input?: HTMLInputElement): void {
  if (!input) return
  const picker = input as HTMLInputElement & { showPicker?: () => void }
  if (typeof picker.showPicker !== "function") return
  try {
    picker.showPicker()
  } catch {
    // 部分浏览器不允许多次触发，用户仍可点击日历图标
  }
}

function studentCountByClass(classId: string): number {
  return students.value.filter((s) => s.class_id === classId).length
}

// =====================================================
// 数据加载
// =====================================================

async function fetchProfile(): Promise<void> {
  const res = await request.get<ApiResult<{ username?: string }>>("/api/admin/profile")
  if (res.data.data?.username) {
    adminUsername.value = res.data.data.username
    adminInitial.value = res.data.data.username.slice(0, 1).toUpperCase()
  }
}

async function fetchTeachers(): Promise<void> {
  const res = await request.get<ApiResult<TeacherRow[]>>("/api/admin/teachers")
  teachers.value = res.data.data || []
}

async function fetchStudents(): Promise<void> {
  const res = await request.get<ApiResult<StudentRow[]>>("/api/admin/students")
  students.value = res.data.data || []
}

async function fetchClasses(): Promise<void> {
  const res = await request.get<ApiResult<ClassRow[]>>("/api/admin/classes")
  classes.value = res.data.data || []
}

async function fetchCourses(): Promise<void> {
  const res = await request.get<ApiResult<CourseRow[]>>("/api/admin/courses")
  courses.value = res.data.data || []
}

async function fetchUpdates(): Promise<void> {
  const res = await request.get<ApiResult<UpdateRow[]>>("/api/admin/updates")
  updates.value = res.data.data || []
}

async function loadAll(): Promise<void> {
  pageLoading.value = true
  pageError.value = ""
  try {
    await Promise.all([
      fetchProfile(),
      fetchTeachers(),
      fetchStudents(),
      fetchClasses(),
      fetchCourses(),
      fetchUpdates()
    ])
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
// 创建教师
// =====================================================

function resetTeacherForm() {
  teacherForm.username = ""
  teacherForm.password = ""
  teacherForm.name = ""
  teacherForm.department = ""
  teacherForm.phone = ""
}

function clearTeacherForm() {
  resetTeacherForm()
  teacherAlert.value.show = false
}

async function submitTeacher() {
  teacherAlert.value.show = false

  if (!teacherForm.username.trim() || !teacherForm.password || !teacherForm.name.trim()) {
    setAlert(teacherAlert, "error", "用户名、初始密码、教师姓名为必填项")
    return
  }
  if (teacherForm.password.length < 6) {
    setAlert(teacherAlert, "error", "初始密码至少 6 位")
    return
  }
  if (!validPhone(teacherForm.phone.trim())) {
    setAlert(teacherAlert, "error", "手机号格式不正确，请输入 11 位手机号")
    return
  }

  teacherSubmitting.value = true
  try {
    const res = await request.post<ApiResult<null>>("/api/admin/teacher/create", {
      username: teacherForm.username.trim(),
      password: teacherForm.password,
      name: teacherForm.name.trim(),
      department: teacherForm.department.trim() || null,
      phone: teacherForm.phone.trim() || null
    })
    if (res.data.code === 200) {
      setAlert(teacherAlert, "success", `教师「${teacherForm.name.trim()}」创建成功`)
      showToast("教师账户创建成功")
      resetTeacherForm()
      await Promise.all([fetchTeachers(), fetchClasses()])
    } else {
      setAlert(teacherAlert, "error", res.data.message || "创建失败")
    }
  } catch (error: unknown) {
    setAlert(teacherAlert, "error", errorMessage(error, "创建教师失败"))
  } finally {
    teacherSubmitting.value = false
  }
}

// =====================================================
// 创建学生
// =====================================================

function resetStudentForm() {
  studentForm.username = ""
  studentForm.password = ""
  studentForm.student_no = ""
  studentForm.name = ""
  studentForm.class_id = ""
  studentForm.phone = ""
}

function clearStudentForm() {
  resetStudentForm()
  studentAlert.value.show = false
}

async function submitStudent() {
  studentAlert.value.show = false

  if (
    !studentForm.username.trim() ||
    !studentForm.password ||
    !studentForm.student_no.trim() ||
    !studentForm.name.trim()
  ) {
    setAlert(studentAlert, "error", "用户名、初始密码、学号、学生姓名为必填项")
    return
  }
  if (studentForm.password.length < 6) {
    setAlert(studentAlert, "error", "初始密码至少 6 位")
    return
  }
  if (!validPhone(studentForm.phone.trim())) {
    setAlert(studentAlert, "error", "手机号格式不正确，请输入 11 位手机号")
    return
  }

  studentSubmitting.value = true
  try {
    const res = await request.post<ApiResult<null>>("/api/admin/student/create", {
      username: studentForm.username.trim(),
      password: studentForm.password,
      student_no: studentForm.student_no.trim(),
      name: studentForm.name.trim(),
      class_id: studentForm.class_id || null,
      phone: studentForm.phone.trim() || null
    })
    if (res.data.code === 200) {
      setAlert(studentAlert, "success", `学生「${studentForm.name.trim()}」创建成功`)
      showToast("学生账户创建成功")
      resetStudentForm()
      await fetchStudents()
    } else {
      setAlert(studentAlert, "error", res.data.message || "创建失败")
    }
  } catch (error: unknown) {
    setAlert(studentAlert, "error", errorMessage(error, "创建学生失败"))
  } finally {
    studentSubmitting.value = false
  }
}

// =====================================================
// 创建课程
// =====================================================

function resetCourseForm() {
  courseForm.name = ""
  courseForm.teacher_id = ""
  courseForm.class_id = ""
  courseForm.course_date = todayText()
  courseForm.course_end_date = todayText()
  courseForm.start_hour = ""
  courseForm.start_minute = ""
  courseForm.end_hour = ""
  courseForm.end_minute = ""
}

function clearCourseForm() {
  resetCourseForm()
  courseAlert.value.show = false
}

// 生成起始日期至结束日期之间的每一天（含首尾），格式 YYYY-MM-DD；非法或倒序返回 null
function buildCourseDates(start: string, end: string): string[] | null {
  const startDate = new Date(`${start}T00:00:00`)
  if (Number.isNaN(startDate.getTime())) return null
  const endDate = new Date(`${end}T00:00:00`)
  if (Number.isNaN(endDate.getTime()) || endDate < startDate) return null
  const dates: string[] = []
  const cursor = new Date(startDate)
  while (cursor <= endDate) {
    const year = cursor.getFullYear()
    const month = String(cursor.getMonth() + 1).padStart(2, "0")
    const day = String(cursor.getDate()).padStart(2, "0")
    dates.push(`${year}-${month}-${day}`)
    cursor.setDate(cursor.getDate() + 1)
  }
  return dates
}

async function submitCourse() {
  courseAlert.value.show = false

  if (!courseForm.name.trim()) {
    setAlert(courseAlert, "error", "请填写课程名称")
    return
  }
  if (!courseForm.teacher_id) {
    setAlert(courseAlert, "error", "请选择授课教师")
    return
  }
  if (!courseForm.class_id) {
    setAlert(courseAlert, "error", "请选择上课班级")
    return
  }

  let time: string | null = null
  const anyTime = TIME_FIELD_KEYS.some((key) => courseForm[key] !== "")
  if (anyTime) {
    for (const key of TIME_FIELD_KEYS) {
      if (/^\d$/.test(courseForm[key])) {
        courseForm[key] = `0${courseForm[key]}`
      }
      checkTimeField(key)
    }
    if (TIME_FIELD_KEYS.some((key) => !courseForm[key])) {
      setAlert(courseAlert, "error", "请完整填写开始与结束的时、分")
      return
    }
    if (TIME_FIELD_KEYS.some((key) => timeErrors[key])) {
      setAlert(courseAlert, "error", "时间超出范围：小时 00-23，分 00-59")
      return
    }
    const startTime = buildTimeString(courseForm.start_hour, courseForm.start_minute)
    const endTime = buildTimeString(courseForm.end_hour, courseForm.end_minute)
    if (!startTime || !endTime) {
      setAlert(courseAlert, "error", "请完整填写开始与结束的时、分")
      return
    }
    time = combineTimeRange(startTime, endTime)
    if (!time) {
      setAlert(courseAlert, "error", "上课结束时间必须晚于开始时间")
      return
    }
  }

  let dates: (string | null)[] = [courseForm.course_date || null]
  if (courseForm.course_end_date) {
    if (!courseForm.course_date) {
      setAlert(courseAlert, "error", "请选择上课日期")
      return
    }
    const range = buildCourseDates(courseForm.course_date, courseForm.course_end_date)
    if (!range) {
      setAlert(courseAlert, "error", "结束日期不能早于上课日期")
      return
    }
    dates = range
  }

  const courseName = courseForm.name.trim()
  courseSubmitting.value = true
  try {
    let successCount = 0
    for (const date of dates) {
      const res = await request.post<ApiResult<null>>("/api/admin/courses/create", {
        name: courseName,
        teacher_id: courseForm.teacher_id,
        class_id: courseForm.class_id,
        course_date: date,
        time
      })
      if (res.data.code === 200) {
        successCount += 1
      }
    }
    if (successCount === dates.length) {
      if (dates.length > 1) {
        setAlert(courseAlert, "success", `课程「${courseName}」已创建 ${successCount} 天（${dates[0]} ~ ${dates[dates.length - 1]}）`)
      } else {
        setAlert(courseAlert, "success", `课程「${courseName}」创建成功`)
      }
      showToast("课程创建成功")
      courseForm.name = ""
      courseForm.start_hour = ""
      courseForm.start_minute = ""
      courseForm.end_hour = ""
      courseForm.end_minute = ""
      courseForm.course_end_date = ""
      await fetchCourses()
    } else {
      setAlert(courseAlert, "error", `课程创建失败：共需创建 ${dates.length} 天，成功 ${successCount} 天`)
      await fetchCourses()
    }
  } catch (error: unknown) {
    setAlert(courseAlert, "error", errorMessage(error, "课程创建失败"))
  } finally {
    courseSubmitting.value = false
  }
}

// =====================================================
// 创建班级
// =====================================================

function resetClassForm() {
  classForm.name = ""
  classForm.grade = ""
  classForm.teacher_id = ""
}

function clearClassForm() {
  resetClassForm()
  classAlert.value.show = false
}

async function submitClass() {
  classAlert.value.show = false

  if (!classForm.name.trim()) {
    setAlert(classAlert, "error", "班级名称不能为空")
    return
  }

  classSubmitting.value = true
  try {
    const res = await request.post<ApiResult<{ class_id?: string }>>("/api/admin/class/create", {
      name: classForm.name.trim(),
      grade: classForm.grade.trim() || null,
      teacher_id: classForm.teacher_id || null
    })
    if (res.data.code === 200) {
      setAlert(classAlert, "success", `班级「${classForm.name.trim()}」创建成功`)
      showToast("班级创建成功")
      resetClassForm()
      await fetchClasses()
    } else {
      setAlert(classAlert, "error", res.data.message || "创建失败")
    }
  } catch (error: unknown) {
    setAlert(classAlert, "error", errorMessage(error, "班级创建失败"))
  } finally {
    classSubmitting.value = false
  }
}

// =====================================================
// 重置密码
// =====================================================

function openPwdModal(userId: string, username: string) {
  pwdModal.user_id = userId
  pwdModal.username = username
  pwdModal.password = ""
  pwdModal.error = ""
  pwdModal.submitting = false
  pwdModal.show = true
  nextTick(() => {
    pwdInputRef.value?.focus()
  })
}

function closePwdModal() {
  if (pwdModal.submitting) {
    return
  }
  pwdModal.show = false
}

async function confirmResetPwd() {
  pwdModal.error = ""
  if (!pwdModal.password) {
    pwdModal.error = "请输入新密码"
    return
  }
  if (pwdModal.password.length < 6) {
    pwdModal.error = "新密码至少 6 位"
    return
  }

  pwdModal.submitting = true
  try {
    const res = await request.put<ApiResult<null>>("/api/admin/user/password", {
      user_id: pwdModal.user_id,
      password: pwdModal.password
    })
    if (res.data.code === 200) {
      pwdModal.show = false
      showToast(`账户「${pwdModal.username}」密码已重置`)
    } else {
      pwdModal.error = res.data.message || "密码重置失败"
    }
  } catch (error: unknown) {
    if (isAuthError(error)) {
      pwdModal.show = false
      router.replace("/login")
      return
    }
    pwdModal.error = errorMessage(error, "密码重置失败")
  } finally {
    pwdModal.submitting = false
  }
}

// =====================================================
// 启用 / 禁用账户
// =====================================================

async function toggleStatus(row: TeacherRow | StudentRow) {
  const nextStatus = row.status === 1 ? 0 : 1
  const actionText = nextStatus === 1 ? "启用" : "禁用"
  try {
    const res = await request.put<ApiResult<null>>("/api/admin/user/status", {
      user_id: row.user_id,
      status: nextStatus
    })
    if (res.data.code === 200) {
      row.status = nextStatus
      showToast(`账户「${row.username}」已${actionText}`)
    } else {
      showToast(res.data.message || "状态修改失败", "error")
    }
  } catch (error: unknown) {
    if (isAuthError(error)) {
      router.replace("/login")
      return
    }
    showToast(errorMessage(error, "状态修改失败"), "error")
  }
}

// =====================================================
// 删除账户 / 课程 / 班级
// =====================================================

async function deleteTeacher(row: TeacherRow) {
  if (!window.confirm(`确认删除教师「${row.name}」？该账户及其创建的课程将被一并删除，此操作不可撤销。`)) {
    return
  }
  try {
    const res = await request.delete<ApiResult<null>>(`/api/admin/teacher/${row.teacher_id}`)
    if (res.data.code === 200) {
      teachers.value = teachers.value.filter((t) => t.teacher_id !== row.teacher_id)
      showToast(`教师「${row.name}」已删除`)
    } else {
      showToast(res.data.message || "删除失败", "error")
    }
  } catch (error: unknown) {
    if (isAuthError(error)) {
      router.replace("/login")
      return
    }
    showToast(errorMessage(error, "删除教师失败"), "error")
  }
}

async function deleteStudent(row: StudentRow) {
  if (!window.confirm(`确认删除学生「${row.name}」？该账户将被永久删除，此操作不可撤销。`)) {
    return
  }
  try {
    const res = await request.delete<ApiResult<null>>(`/api/admin/student/${row.student_id}`)
    if (res.data.code === 200) {
      students.value = students.value.filter((s) => s.student_id !== row.student_id)
      showToast(`学生「${row.name}」已删除`)
    } else {
      showToast(res.data.message || "删除失败", "error")
    }
  } catch (error: unknown) {
    if (isAuthError(error)) {
      router.replace("/login")
      return
    }
    showToast(errorMessage(error, "删除学生失败"), "error")
  }
}

async function deleteCourse(row: CourseRow) {
  if (!window.confirm(`确认删除课程「${row.name}」？该课程的签到任务与记录将被一并删除。`)) {
    return
  }
  try {
    const res = await request.delete<ApiResult<null>>(`/api/admin/course/${row.id}`)
    if (res.data.code === 200) {
      courses.value = courses.value.filter((c) => c.id !== row.id)
      showToast(`课程「${row.name}」已删除`)
    } else {
      showToast(res.data.message || "删除失败", "error")
    }
  } catch (error: unknown) {
    if (isAuthError(error)) {
      router.replace("/login")
      return
    }
    showToast(errorMessage(error, "删除课程失败"), "error")
  }
}

async function deleteClass(row: ClassRow) {
  if (!window.confirm(`确认删除班级「${row.name}」？该班级的课程将被删除，已分配的师生将解除班级绑定。`)) {
    return
  }
  try {
    const res = await request.delete<ApiResult<null>>(`/api/admin/class/${row.id}`)
    if (res.data.code === 200) {
      classes.value = classes.value.filter((c) => c.id !== row.id)
      showToast(`班级「${row.name}」已删除`)
    } else {
      showToast(res.data.message || "删除失败", "error")
    }
  } catch (error: unknown) {
    if (isAuthError(error)) {
      router.replace("/login")
      return
    }
    showToast(errorMessage(error, "删除班级失败"), "error")
  }
}

// =====================================================
// 分配班级（教师 / 学生）
// =====================================================

function openAssignModal(
  type: "teacher" | "student",
  id: string,
  name: string,
  currentClassId: string | null
) {
  assignModal.targetType = type
  assignModal.targetId = id
  assignModal.targetName = name
  assignModal.class_id = currentClassId || ""
  assignModal.error = ""
  assignModal.show = true
}

function closeAssignModal() {
  assignModal.show = false
}

async function confirmAssignClass() {
  assignModal.error = ""
  const endpoint = assignModal.targetType === "teacher"
    ? "/api/admin/teacher/class"
    : "/api/admin/student/class"
  const idField = assignModal.targetType === "teacher" ? "teacher_id" : "student_id"
  const label = assignModal.targetType === "teacher" ? "教师" : "学生"

  assignModal.submitting = true
  try {
    const res = await request.put<ApiResult<null>>(endpoint, {
      [idField]: assignModal.targetId,
      class_id: assignModal.class_id || null
    })
    if (res.data.code === 200) {
      assignModal.show = false
      showToast(`${label}「${assignModal.targetName}」班级已更新`)
      await Promise.all([
        fetchTeachers(),
        fetchStudents(),
        fetchClasses()
      ])
    } else {
      assignModal.error = res.data.message || "分配失败"
    }
  } catch (error: unknown) {
    if (isAuthError(error)) {
      assignModal.show = false
      router.replace("/login")
      return
    }
    assignModal.error = errorMessage(error, "班级分配失败")
  } finally {
    assignModal.submitting = false
  }
}

// =====================================================
// 更新日志（增 / 改 / 删）
// =====================================================

function updateTagClass(tag: string): string {
  if (tag === "新增") return "badge-new"
  if (tag === "优化") return "badge-opt"
  return "badge-fix"
}

function openUpdateModal(row?: UpdateRow) {
  if (row) {
    updateModal.update_id = row.update_id
    updateModal.tag = row.tag
    updateModal.date = (row.created_at || "").slice(0, 10)
    updateModal.content = row.content
  } else {
    updateModal.update_id = 0
    updateModal.tag = "新增"
    updateModal.date = todayText()
    updateModal.content = ""
  }
  updateModal.error = ""
  updateModal.submitting = false
  updateModal.show = true
}

function closeUpdateModal() {
  updateModal.show = false
}

async function submitUpdate() {
  updateModal.error = ""

  const content = updateModal.content.trim()

  if (!content) {
    updateModal.error = "请输入更新内容"
    return
  }
  if (!updateModal.date) {
    updateModal.error = "请选择日期"
    return
  }

  updateModal.submitting = true
  try {
    const payload = {
      tag: updateModal.tag,
      content,
      date: updateModal.date
    }
    const res = updateModal.update_id
      ? await request.put<ApiResult<null>>(`/api/admin/updates/${updateModal.update_id}`, payload)
      : await request.post<ApiResult<null>>("/api/admin/updates", payload)

    if (res.data.code === 200) {
      updateModal.show = false
      showToast(updateModal.update_id ? "更新日志已修改" : "更新日志已添加")
      await fetchUpdates()
    } else {
      updateModal.error = res.data.message || "保存失败"
    }
  } catch (error: unknown) {
    if (isAuthError(error)) {
      updateModal.show = false
      router.replace("/login")
      return
    }
    updateModal.error = errorMessage(error, "保存更新日志失败")
  } finally {
    updateModal.submitting = false
  }
}

async function deleteUpdate(row: UpdateRow) {
  if (!window.confirm(`确认删除这条「${row.tag}」更新日志？`)) {
    return
  }
  try {
    const res = await request.delete<ApiResult<null>>(`/api/admin/updates/${row.update_id}`)
    if (res.data.code === 200) {
      updates.value = updates.value.filter((item) => item.update_id !== row.update_id)
      showToast("更新日志已删除")
    } else {
      showToast(res.data.message || "删除失败", "error")
    }
  } catch (error: unknown) {
    if (isAuthError(error)) {
      router.replace("/login")
      return
    }
    showToast(errorMessage(error, "删除更新日志失败"), "error")
  }
}

// =====================================================
// 跨站同步（管理页）
// =====================================================

async function loadSyncStatus(): Promise<void> {
  syncLoading.value = true
  lastSyncError.value = ""
  try {
    const res = await request.get<ApiResult<SyncStatus>>("/api/admin/sync/status")
    if (res.data.code === 200) {
      syncStatus.value = res.data.data || null
    }
    // 详情表与总览并发拉取，互不阻塞
    await Promise.all([loadSyncOutbox(), loadSyncConflicts()])
  } catch (error: unknown) {
    if (isAuthError(error)) {
      showToast("登录已失效，请重新登录", "error")
      router.replace("/login")
      return
    }
    lastSyncError.value = errorMessage(error, "同步状态加载失败，请确认后端服务已启动")
  } finally {
    syncLoading.value = false
  }
}

// 「刷新」按钮：点击后同样进入 3s 冷却，拉取完成后提示
async function refreshSync(): Promise<void> {
  startSyncCooldown()
  await loadSyncStatus()
  if (!lastSyncError.value) showToast("刷新已完成")
}

async function loadSyncOutbox(): Promise<void> {
  const res = await request.get<ApiResult<{ items: SyncOutboxRow[] }>>("/api/admin/sync/outbox", {
    params: { limit: 100 }
  })
  outboxItems.value = res.data.data?.items || []
}

async function loadSyncConflicts(): Promise<void> {
  const res = await request.get<ApiResult<{ items: SyncConflictRow[]; total?: number; pending?: number }>>(
    "/api/admin/sync/conflicts",
    {
      params: {
        state: conflictState.value,
        keyword: conflictKeyword.value.trim() || undefined
      }
    }
  )
  const data = res.data.data
  conflictItems.value = data?.items || []
  conflictTotal.value = data?.total ?? conflictItems.value.length
  conflictPending.value = data?.pending ?? 0
  // 只保留仍在当前列表里的选中项，避免跨筛选残留
  conflictSelected.value = conflictSelected.value.filter((id) =>
    conflictItems.value.some((row) => row.id === id)
  )
}

function toggleConflictAll(event: Event): void {
  const checked = (event.target as HTMLInputElement).checked
  conflictSelected.value = checked ? conflictItems.value.map((row) => row.id) : []
}

function toggleConflictRow(id: string): void {
  const index = conflictSelected.value.indexOf(id)
  if (index >= 0) conflictSelected.value.splice(index, 1)
  else conflictSelected.value.push(id)
}

// 批处理：allPending=true 时不带 id，交给后端处理全部待处理行
async function batchHandleConflicts(action: "resolve" | "ignore", allPending = false): Promise<void> {
  if (!allPending && !conflictSelected.value.length) return
  syncBusy.value = true
  try {
    const res = await request.post<ApiResult<{ affected: number }>>("/api/admin/sync/conflicts/batch", {
      action,
      ids: allPending ? [] : conflictSelected.value
    })
    showToast(res.data.message || "已处理")
    conflictSelected.value = []
    await Promise.all([loadSyncConflicts(), loadSyncStatus()])
  } catch (error: unknown) {
    if (isAuthError(error)) {
      showToast("登录已失效，请重新登录", "error")
      router.replace("/login")
      return
    }
    showToast(errorMessage(error, "批量处理失败"), "error")
  } finally {
    syncBusy.value = false
  }
}

async function triggerSync(action: "sync" | "reconcile"): Promise<void> {
  startSyncCooldown()
  syncBusy.value = true
  try {
    await request.post<ApiResult<unknown>>("/api/admin/sync/trigger", { action })
    showToast(action === "reconcile" ? "执行对账已完成" : "立即同步已完成")
    // 异步同步在后台线程执行，稍后自动刷新一次结果
    window.setTimeout(() => {
      loadSyncStatus()
    }, 1500)
  } catch (error: unknown) {
    if (isAuthError(error)) {
      showToast("登录已失效，请重新登录", "error")
      router.replace("/login")
      return
    }
    showToast(errorMessage(error, "触发同步失败"), "error")
  } finally {
    syncBusy.value = false
  }
}

// 连接对端：手动点击 / 打开同步页时进入有界自动重试
function stopAutoConnect(): void {
  if (autoConnectTimer !== undefined) {
    window.clearTimeout(autoConnectTimer)
    autoConnectTimer = undefined
  }
  if (autoConnectTick !== undefined) {
    window.clearInterval(autoConnectTick)
    autoConnectTick = undefined
  }
  autoConnecting.value = false
  autoConnectElapsed.value = 0
}

// 连一次：真去触发一轮同步，再刷新对端连通性
async function connectOnce(): Promise<void> {
  try {
    await request.post<ApiResult<unknown>>("/api/admin/sync/trigger", { action: "sync" })
  } catch (error: unknown) {
    if (isAuthError(error)) {
      showToast("登录已失效，请重新登录", "error")
      router.replace("/login")
      stopAutoConnect()
      return
    }
  }
  await loadSyncStatus()
}

async function runAutoConnect(): Promise<void> {
  if (!autoConnecting.value) return

  const elapsed = Date.now() - autoConnectStartedAt

  // 到 30s 上限：自动取消，需用户重新点击「连接对端」
  if (elapsed >= AUTO_CONNECT_WINDOW) {
    stopAutoConnect()
    showToast("自动连接已取消，请重新点击「连接对端」", "error")
    return
  }

  await connectOnce()

  if (!autoConnecting.value) return

  // 全部对端已连通：提前结束
  if (syncPeers.value.length > 0 && syncPeers.value.every((peer) => peer.online)) {
    stopAutoConnect()
    showToast("连接对端已完成")
    return
  }

  const remaining = AUTO_CONNECT_WINDOW - (Date.now() - autoConnectStartedAt)
  autoConnectTimer = window.setTimeout(
    runAutoConnect,
    Math.max(0, Math.min(AUTO_CONNECT_INTERVAL, remaining))
  )
}

function startAutoConnect(): void {
  if (autoConnecting.value) return

  autoConnecting.value = true
  autoConnectStartedAt = Date.now()
  autoConnectElapsed.value = 0

  // 秒表：从 0s 连续跳到 30s
  autoConnectTick = window.setInterval(() => {
    const sec = Math.floor((Date.now() - autoConnectStartedAt) / 1000)
    autoConnectElapsed.value = Math.min(sec, Math.floor(AUTO_CONNECT_WINDOW / 1000))
  }, 1000)

  runAutoConnect()
}

function toggleConnect(): void {
  startSyncCooldown()
  if (autoConnecting.value) {
    stopAutoConnect()
    return
  }
  startAutoConnect()
}

async function retryOutbox(id: number): Promise<void> {
  syncBusy.value = true
  try {
    await request.post<ApiResult<unknown>>("/api/admin/sync/outbox/retry", { id })
    showToast("已重新入队")
    await loadSyncStatus()
  } catch (error: unknown) {
    if (isAuthError(error)) {
      showToast("登录已失效，请重新登录", "error")
      router.replace("/login")
      return
    }
    showToast(errorMessage(error, "重试失败"), "error")
  } finally {
    syncBusy.value = false
  }
}

async function handleConflict(id: string, action: "resolve" | "ignore"): Promise<void> {
  syncBusy.value = true
  try {
    await request.post<ApiResult<unknown>>("/api/admin/sync/conflicts/handle", { id, action })
    showToast(action === "resolve" ? "已标记为已裁决" : "已忽略该冲突")
    await Promise.all([loadSyncConflicts(), loadSyncStatus()])
  } catch (error: unknown) {
    if (isAuthError(error)) {
      showToast("登录已失效，请重新登录", "error")
      router.replace("/login")
      return
    }
    showToast(errorMessage(error, "处理冲突失败"), "error")
  } finally {
    syncBusy.value = false
  }
}

function outboxStatusText(status: number): string {
  const map: Record<number, string> = { 0: "待发送", 1: "已发送", 2: "发送失败" }
  return map[Number(status)] || "未知"
}

function outboxBadgeClass(status: number): string {
  const value = Number(status)
  if (value === 1) return "badge-ok"
  if (value === 2) return "badge-off"
  return "badge-opt"
}

function conflictStateText(state: number): string {
  const map: Record<number, string> = { 0: "待处理", 1: "已裁决", 2: "已忽略" }
  return map[Number(state)] || "未知"
}

// 事件类型：与 sync_contract 中的 event_type 保持一致
function eventTypeText(eventType: string): string {
  const map: Record<string, string> = {
    "attendance.signin": "签到",
    "attendance.update": "更新",
    "attendance.delete": "删除"
  }
  return map[eventType] || eventType || "-"
}

function conflictLoserText(row: SyncConflictRow): string {
  const losers = row.loser_json?.losers
  if (!losers || !losers.length) return "-"
  const lines = losers.map((entry) => {
    const parts: string[] = []
    const site = entry.site_name || entry.site
    if (site) parts.push(String(site))
    if (entry.sign_time) parts.push(String(entry.sign_time))
    if (entry.status_text) parts.push(String(entry.status_text))
    return parts.join(" · ")
  })
  const text = lines.filter((line) => line).join("；")
  return text || "-"
}

function cursorText(peerCode: string): string {
  const row = syncStatus.value?.cursors?.[peerCode]
  if (!row) return "未同步"
  const suffix = row.last_success_at ? ` · ${row.last_success_at}` : ""
  return `序号 ${row.last_seq ?? 0}${suffix}`
}

// 进入「跨站同步」页时才拉取数据，避免开屏即访问对端拖慢加载
watch(activeTab, (tab) => {
  if (tab === "sync") {
    // 打开同步页自动执行一次「连接对端」
    startAutoConnect()
  } else {
    // 离开同步页时停掉自动连接，避免后台空转
    stopAutoConnect()
  }
})

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

courseForm.course_date = todayText()
courseForm.course_end_date = todayText()

onMounted(() => {
  loadAll()
})
</script>

<style scoped>
/* =====================================================
   Corporate Clean 设计 token（与 STYLEKIT 精确对应）
   ===================================================== */

.admin-page {
  --blue-700: #1d4ed8;
  --blue-600: #2563eb;
  --blue-500: #3b82f6;
  --blue-100: #dbeafe;
  --blue-50: #eff6ff;

  --gray-900: #111827;
  --gray-700: #374151;
  --gray-600: #4b5563;
  --gray-500: #6b7280;
  --gray-400: #9ca3af;
  --gray-300: #d1d5db;
  --gray-200: #e5e7eb;
  --gray-100: #f3f4f6;
  --gray-50: #f9fafb;
  --slate-50: #f8fafc;

  --green-700: #15803d;
  --green-200: #bbf7d0;
  --green-100: #dcfce7;
  --green-50: #f0fdf4;
  --amber-700: #b45309;
  --amber-200: #fde68a;
  --amber-100: #fef3c7;
  --amber-50: #fffbeb;
  --red-700: #b91c1c;
  --red-200: #fecaca;
  --red-100: #fee2e2;
  --red-50: #fef2f2;

  --cyan-700: #0e7490;
  --cyan-200: #a5f3fc;
  --cyan-50: #ecfeff;

  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);

  min-height: 100vh;
  display: flex;
  background: var(--slate-50);
  color: var(--gray-700);
  font-family: system-ui, -apple-system, "Segoe UI", "PingFang SC",
    "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  font-size: 14px;
  line-height: 1.5;
  text-align: left;
}

:global(body) {
  margin: 0;
}

/* ================= 侧边导航 ================= */

.sidebar {
  width: 248px;
  flex: 0 0 248px;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-right: 1px solid var(--gray-200);
  padding: 24px 16px;
  position: sticky;
  top: 0;
  height: 95vh;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 8px;
}

.brand-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: var(--blue-600);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;
  box-shadow: var(--shadow-sm);
}

.brand-icon svg {
  width: 22px;
  height: 22px;
}

.brand-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--gray-900);
  letter-spacing: -0.01em;
}

.brand-sub {
  font-size: 12px;
  color: var(--gray-400);
  margin-top: 1px;
}

.nav {
  margin-top: 28px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 10px 14px;
  border: 1px solid transparent;
  border-radius: 8px;
  background: transparent;
  color: var(--gray-600);
  font-size: 14px;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  text-align: left;
  transition: all 0.15s ease-out;
}

.nav-item svg {
  width: 20px;
  height: 20px;
  flex: 0 0 auto;
}

.nav-item:hover {
  background: var(--gray-100);
  color: var(--gray-900);
}

.nav-item.active {
  background: var(--blue-50);
  color: var(--blue-700);
  font-weight: 600;
}

.nav-item:active {
  transform: scale(0.98);
}

.nav-item:focus-visible {
  outline: none;
  box-shadow: 0 0 0 2px #fff, 0 0 0 4px var(--blue-500);
}

.sidebar-footer {
  margin-top: auto;
}

.logout-item:hover {
  background: var(--red-50);
  color: var(--red-700);
}

/* ================= 主区域 ================= */

.main {
  flex: 1 1 auto;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 18px 32px;
  background: rgba(255, 255, 255, 0.92);
  border-bottom: 1px solid var(--gray-200);
  backdrop-filter: blur(6px);
}

.topbar-titles h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: var(--gray-900);
}

.topbar-titles p {
  margin: 2px 0 0;
  font-size: 13px;
  color: var(--gray-500);
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.admin-chip {
  display: flex;
  align-items: center;
  gap: 10px;
}

.admin-avatar {
  width: 38px;
  height: 38px;
  border-radius: 9999px;
  background: var(--blue-50);
  color: var(--blue-700);
  border: 1px solid var(--blue-100);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  font-weight: 600;
}

.admin-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--gray-900);
  line-height: 1.3;
}

.admin-role {
  font-size: 12px;
  color: var(--gray-400);
  line-height: 1.3;
}

.mobile-logout {
  display: none;
}

.content {
  padding: 28px 32px 40px;
}

/* ================= 通用卡片 ================= */

.card {
  background: #fff;
  border: 1px solid var(--gray-200);
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  padding: 20px;
  transition: all 0.2s ease-out;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.stat-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.stat-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--gray-500);
}

.stat-icon {
  width: 38px;
  height: 38px;
  border-radius: 8px;
  background: var(--blue-50);
  color: var(--blue-600);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease-out;
}

.stat-icon svg {
  width: 20px;
  height: 20px;
}

.stat-card:hover .stat-icon {
  background: var(--blue-500);
  color: #fff;
  transform: scale(1.1);
}

.stat-number {
  margin-top: 10px;
  font-size: 28px;
  font-weight: 600;
  letter-spacing: -0.02em;
  color: var(--gray-900);
}

.stat-caption {
  margin-top: 4px;
  font-size: 12px;
  color: var(--gray-400);
}

.panel-card {
  overflow: hidden;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  padding: 18px 24px;
  border-bottom: 1px solid var(--gray-200);
}

.panel-header h2 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--gray-900);
}

/* ================= 分段切换 ================= */

.sub-tabs {
  display: inline-flex;
  gap: 2px;
  padding: 3px;
  background: var(--gray-100);
  border-radius: 8px;
}

.sub-tabs button {
  padding: 6px 14px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: var(--gray-500);
  font-size: 13px;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.15s ease-out;
}

.sub-tabs button:hover {
  color: var(--gray-900);
}

.sub-tabs button.active {
  background: #fff;
  color: var(--gray-900);
  font-weight: 600;
  box-shadow: var(--shadow-sm);
}

.sub-tabs button:focus-visible {
  outline: none;
  box-shadow: 0 0 0 2px #fff, 0 0 0 4px var(--blue-500);
}

.sub-tabs button:active {
  transform: scale(0.98);
}

/* ================= 表格 ================= */

.table-wrap {
  overflow-x: auto;
}

/* ================= 列表筛选工具栏 ================= */

.table-toolbar {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 16px;
  flex-wrap: wrap;
  padding: 14px 24px;
  border-bottom: 1px solid var(--gray-200);
}

.table-toolbar .toolbar-count {
  font-size: 12px;
  color: var(--gray-500);
}

/* 「全部」按钮组：固定贴左；用 margin-right:auto 把其余控件顶到右侧 */
.table-toolbar .toolbar-left {
  display: flex;
  gap: 8px;
  margin-right: auto;
}

/* 隐藏时保留占位，避免切换状态时整行重排 */
.table-toolbar .toolbar-left.is-hidden {
  visibility: hidden;
}

/* 冲突状态下拉：给足宽度，避免「全部状态」等 3~4 字标签折行 */
.conflict-state-select {
  min-width: 104px;
  flex: none;
}

.search-field {
  position: relative;
  display: inline-flex;
  align-items: center;
  width: 100%;
  max-width: 340px;
}

.search-field .search-icon {
  position: absolute;
  left: 12px;
  width: 15px;
  height: 15px;
  fill: none;
  stroke: var(--gray-400);
  stroke-width: 1.8;
  stroke-linecap: round;
  pointer-events: none;
}

.search-field .search-input {
  width: 100%;
  box-sizing: border-box;
  padding: 8px 14px 8px 34px;
  font-size: 13px;
  font-family: inherit;
  color: var(--gray-900);
  background: var(--gray-50);
  border: 1px solid var(--gray-300);
  border-radius: 999px;
  transition: all 0.15s ease-out;
}

.search-field .search-input::placeholder {
  color: var(--gray-400);
}

.search-field .search-input:hover {
  border-color: var(--gray-400);
}

.search-field .search-input:focus {
  outline: none;
  background: #fff;
  border-color: var(--blue-500);
  box-shadow: 0 0 0 2px #fff, 0 0 0 4px var(--blue-500);
}

.update-date-filter {
  width: 170px;
  flex: 0 0 170px;
  padding: 7px 12px;
  font-size: 13px;
}

/* ================= 分页 ================= */

.table-pager {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  padding: 14px 24px;
  border-top: 1px solid var(--gray-200);
}

.table-pager .pager-info {
  font-size: 12px;
  color: var(--gray-500);
}

.table-pager .pager-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.table-pager button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  white-space: nowrap;
}

.data-table th {
  padding: 11px 16px;
  text-align: left;
  font-size: 12px;
  font-weight: 600;
  color: var(--gray-500);
  background: var(--gray-50);
  border-bottom: 1px solid var(--gray-200);
}

.data-table td {
  padding: 13px 16px;
  color: var(--gray-700);
  border-bottom: 1px solid var(--gray-100);
  vertical-align: middle;
}

.data-table tbody tr {
  transition: background-color 0.15s ease-out;
}

.data-table tbody tr:hover {
  background: var(--gray-50);
}

.data-table tbody tr:last-child td {
  border-bottom: none;
}

.cell-strong {
  font-weight: 600;
  color: var(--gray-900);
}

.cell-muted {
  color: var(--gray-400);
}

.mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 12.5px;
  color: var(--gray-600);
}

.col-actions {
  min-width: 150px;
}

.col-update-tag {
  width: 96px;
}

.col-update-date {
  width: 150px;
}

.row-actions {
  display: flex;
  gap: 8px;
}

.col-check {
  width: 40px;
  text-align: center;
}

.col-check input[type="checkbox"] {
  width: 15px;
  height: 15px;
  cursor: pointer;
  accent-color: var(--blue-500);
}

.empty-cell {
  text-align: center;
  color: var(--gray-400);
  padding: 40px 16px !important;
}

/* ================= 状态徽标 ================= */

.badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 2px 10px;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 500;
  border: 1px solid transparent;
}

.badge::before {
  content: "";
  width: 6px;
  height: 6px;
  border-radius: 9999px;
  background: currentColor;
}

.badge-ok {
  color: var(--green-700);
  background: var(--green-50);
  border-color: var(--green-200);
}

.badge-off {
  color: var(--red-700);
  background: var(--red-50);
  border-color: var(--red-200);
}

.badge-new {
  color: var(--blue-700);
  background: var(--blue-50);
  border-color: var(--blue-100);
}

.badge-opt {
  color: var(--amber-700);
  background: var(--amber-50);
  border-color: var(--amber-200);
}

.badge-fix {
  color: var(--red-700);
  background: var(--red-50);
  border-color: var(--red-200);
}

.badge-cyan {
  color: var(--cyan-700);
  background: var(--cyan-50);
  border-color: var(--cyan-200);
}

/* ================= 跨站同步 ================= */

.sync-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 10px 16px;
  margin-bottom: 16px;
}

/* 左侧一行的本站信息胶囊 */
.sync-site {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
  padding: 6px 14px;
  border-radius: 999px;
  border: 1px solid var(--gray-200);
  background: linear-gradient(180deg, #ffffff, var(--gray-50));
  box-shadow: var(--shadow-sm);
}

.sync-site-dot {
  width: 8px;
  height: 8px;
  flex: none;
  border-radius: 999px;
  background: var(--green-700);
  box-shadow: 0 0 0 3px var(--green-100);
}

.sync-site-dot-off {
  background: var(--gray-400);
  box-shadow: 0 0 0 3px var(--gray-100);
}

.sync-site-code {
  font-weight: 650;
  color: var(--gray-900);
}

.sync-site-meta {
  font-size: 12px;
  color: var(--gray-500);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 右侧按钮组 */
.sync-toolbar-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin-left: auto;
}

/* 跨站同步 · 提示条（离线对端 / 加载失败） */
.sync-alert {
  display: flex;
  gap: 12px;
  margin: 12px 0;
  padding: 12px 14px;
  border-radius: 10px;
  border: 1px solid var(--gray-200);
  background: var(--gray-50);
}

.sync-alert-warn {
  border-color: var(--amber-200);
  background: var(--amber-50);
  color: var(--amber-700);
}

.sync-alert-danger {
  border-color: var(--red-200);
  background: var(--red-50);
  color: var(--red-700);
}

.sync-alert-icon {
  flex: none;
  width: 20px;
  height: 20px;
  margin-top: 1px;
}

.sync-alert-icon svg {
  width: 20px;
  height: 20px;
}

.sync-alert-body {
  min-width: 0;
}

.sync-alert-title {
  margin: 0;
  font-size: 13px;
  font-weight: 600;
}

.sync-alert-text {
  margin: 3px 0 0;
  font-size: 12.5px;
  color: var(--gray-600);
  word-break: break-word;
}

.sync-alert-list {
  margin: 6px 0 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 5px;
}

.sync-alert-list li {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 6px;
}

.sync-alert-list li .sync-alert-text {
  margin: 0;
}

.sync-peer-tag {
  flex: none;
  padding: 1px 8px;
  border-radius: 9999px;
  font-size: 11.5px;
  font-weight: 600;
  background: #fff;
  border: 1px solid currentColor;
}

/* 同步进度 */
.sync-progress {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 12.5px;
  color: var(--gray-600);
}

.sync-progress-idle {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-family: inherit;
  color: var(--gray-400);
}

.sync-progress-idle::before {
  content: "";
  width: 6px;
  height: 6px;
  border-radius: 9999px;
  background: var(--gray-300);
}

/* 在线对端绿点做轻微呼吸，强化「在线」感知 */
.sync-page .badge-ok::before {
  animation: sync-dot-pulse 1.8s ease-out infinite;
}

@keyframes sync-dot-pulse {
  0% { box-shadow: 0 0 0 0 rgba(21, 128, 61, 0.35); }
  70% { box-shadow: 0 0 0 5px rgba(21, 128, 61, 0); }
  100% { box-shadow: 0 0 0 0 rgba(21, 128, 61, 0); }
}

.sync-err {
  max-width: 260px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ================= 按钮 ================= */

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 8px;
  border: 1px solid transparent;
  font-family: inherit;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  box-shadow: var(--shadow-sm);
  transition: all 0.15s ease-out;
}

.btn svg {
  width: 18px;
  height: 18px;
}

.btn:focus-visible {
  outline: none;
  box-shadow: 0 0 0 2px #fff, 0 0 0 4px var(--blue-500);
}

.btn:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn:active {
  transform: scale(0.98) translateY(0);
  box-shadow: var(--shadow-sm);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: var(--shadow-sm);
}

.btn-primary {
  background: var(--blue-600);
  color: #fff;
}

.btn-primary:hover {
  background: var(--blue-700);
}

.btn-secondary {
  background: #fff;
  color: var(--gray-700);
  border-color: var(--gray-300);
}

.btn-secondary:hover {
  background: var(--gray-50);
  color: var(--gray-900);
}

.btn-sm {
  padding: 5px 10px;
  font-size: 12.5px;
  border-radius: 6px;
}

.btn-icon {
  padding: 8px;
}

.btn-soft-primary {
  background: var(--blue-50);
  color: var(--blue-700);
  border-color: var(--blue-100);
  box-shadow: none;
}

.btn-soft-primary:hover {
  background: var(--blue-600);
  color: #fff;
  border-color: var(--blue-600);
}

.btn-soft-warn {
  background: var(--amber-50);
  color: var(--amber-700);
  border-color: var(--amber-200);
  box-shadow: none;
}

.btn-soft-warn:hover {
  background: #f59e0b;
  color: #fff;
  border-color: #f59e0b;
}

.btn-soft-success {
  background: var(--green-50);
  color: var(--green-700);
  border-color: var(--green-200);
  box-shadow: none;
}

.btn-soft-success:hover {
  background: #16a34a;
  color: #fff;
  border-color: #16a34a;
}

.btn-soft-danger {
  background: var(--red-50);
  color: var(--red-700);
  border-color: var(--red-200);
  box-shadow: none;
}

.btn-soft-danger:hover {
  background: #dc2626;
  color: #fff;
  border-color: #dc2626;
}

/* ================= 表单 ================= */

.form-card {
  padding: 28px;
  max-width: 880px;
}

/* 班级管理：表单卡与下方列表卡等宽，上下两块对齐，避免一窄一宽的错位感 */
.form-card-wide {
  max-width: none;
}

@media (min-width: 901px) {
  /* 表单变宽后让三个字段并排一行，输入框不至于被拉得过长 */
  .form-card-wide .form-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .form-card-wide .form-grid .span-2 {
    grid-column: span 1;
  }
}

.form-header {
  margin-bottom: 22px;
}

.form-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: var(--gray-900);
}

.form-header p {
  margin: 6px 0 0;
  font-size: 13px;
  color: var(--gray-500);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px 24px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.span-2 {
  grid-column: span 2;
}

.form-field label {
  font-size: 13px;
  font-weight: 500;
  color: var(--gray-700);
}

.required {
  color: #ef4444;
}

.form-input {
  width: 100%;
  box-sizing: border-box;
  padding: 8px 12px;
  font-size: 14px;
  font-family: inherit;
  color: var(--gray-900);
  background: #fff;
  border: 1px solid var(--gray-300);
  border-radius: 8px;
  transition: all 0.15s ease-out;
}

.form-input::placeholder {
  color: var(--gray-400);
}

.form-input:hover {
  border-color: #9ca3af;
}

.form-input:focus {
  outline: none;
  border-color: var(--blue-500);
  box-shadow: 0 0 0 2px #fff, 0 0 0 4px var(--blue-500);
}

.form-textarea {
  width: 100%;
  box-sizing: border-box;
  padding: 8px 12px;
  font-size: 14px;
  font-family: inherit;
  line-height: 1.6;
  color: var(--gray-900);
  background: #fff;
  border: 1px solid var(--gray-300);
  border-radius: 8px;
  resize: vertical;
  transition: all 0.15s ease-out;
}

.form-textarea::placeholder {
  color: var(--gray-400);
}

.form-textarea:hover {
  border-color: #9ca3af;
}

.form-textarea:focus {
  outline: none;
  border-color: var(--blue-500);
  box-shadow: 0 0 0 2px #fff, 0 0 0 4px var(--blue-500);
}

.cs {
  --cs-accent: var(--blue-500);
  --cs-border: var(--gray-300);
  --cs-border-hover: var(--gray-400);
  --cs-bg-hover: var(--gray-50);
  --cs-text: var(--gray-900);
}

.date-input {
  cursor: pointer;
}

.time-select {
  display: flex;
  align-items: center;
  gap: 4px;
}

.time-cell {
  position: relative;
  flex: 1 1 0;
  min-width: 0;
}

.time-value {
  width: 100%;
  box-sizing: border-box;
  padding: 8px 6px;
  font-size: 14px;
  font-family: inherit;
  color: var(--gray-900);
  text-align: center;
  background: #fff;
  border: 1px solid var(--gray-300);
  border-radius: 8px;
  outline: none;
  transition: all 0.15s ease-out;
}

.time-value:hover {
  border-color: #9ca3af;
}

.time-value:focus {
  border-color: var(--blue-500);
  box-shadow: 0 0 0 2px #fff, 0 0 0 4px var(--blue-500);
}

.time-value.is-empty {
  color: var(--gray-400);
}

.time-value.is-error {
  border-color: var(--red-700);
  color: var(--red-700);
}

.time-value.is-error:focus {
  box-shadow: 0 0 0 2px #fff, 0 0 0 4px var(--red-700);
}

.time-sep {
  flex: 0 0 auto;
  font-size: 13px;
  color: var(--gray-600);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 26px;
  padding-top: 22px;
  border-top: 1px solid var(--gray-200);
}

.field-error {
  margin: 0;
  font-size: 12px;
  color: var(--red-700);
}

.field-hint {
  margin: 0;
  font-size: 12px;
  color: var(--gray-500);
}

/* ================= 提示条 ================= */

.alert {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  border: 1px solid transparent;
  margin-bottom: 20px;
}

.alert-dot {
  width: 8px;
  height: 8px;
  border-radius: 9999px;
  background: currentColor;
  flex: 0 0 auto;
}

.alert.success {
  color: var(--green-700);
  background: var(--green-50);
  border-color: var(--green-200);
}

.alert.error {
  color: var(--red-700);
  background: var(--red-50);
  border-color: var(--red-200);
}

/* ================= 课程面板 ================= */

/* 表单卡与下方列表卡之间留出统一间距（与「新建课程」页保持一致） */
.course-panel,
.class-panel {
  margin-top: 24px;
}

/* ================= 状态页 ================= */

.state-card {
  background: #fff;
  border: 1px solid var(--gray-200);
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
  padding: 64px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  color: var(--gray-500);
  font-size: 14px;
}

.state-error {
  color: var(--red-700);
  margin: 0;
}

.spinner {
  width: 28px;
  height: 28px;
  border-radius: 9999px;
  border: 3px solid var(--gray-200);
  border-top-color: var(--blue-600);
  animation: admin-spin 0.7s linear infinite;
}

@keyframes admin-spin {
  to {
    transform: rotate(360deg);
  }
}

/* ================= 弹窗 ================= */

.modal-mask {
  position: fixed;
  inset: 0;
  z-index: 50;
  background: rgba(17, 24, 39, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.modal-card {
  width: 100%;
  max-width: 420px;
  background: #fff;
  border: 1px solid var(--gray-200);
  border-radius: 12px;
  box-shadow: var(--shadow-md);
  padding: 24px;
}

.modal-card h3 {
  margin: 0;
  font-size: 17px;
  font-weight: 600;
  color: var(--gray-900);
}

.modal-desc {
  margin: 8px 0 18px;
  font-size: 13px;
  color: var(--gray-500);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 22px;
}

/* ================= Toast ================= */

.toast-wrap {
  position: fixed;
  top: 20px;
  right: 24px;
  z-index: 60;
}

.toast {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 11px 16px;
  background: #fff;
  border: 1px solid var(--gray-200);
  border-radius: 10px;
  box-shadow: var(--shadow-md);
  font-size: 13.5px;
  font-weight: 500;
  color: var(--gray-900);
}

.toast-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  flex: 0 0 auto;
}

.toast-icon svg {
  width: 18px;
  height: 18px;
}

.toast.success .toast-icon {
  color: #16a34a;
}

.toast.error .toast-icon {
  color: #dc2626;
}

/* ================= 响应式 ================= */

@media (max-width: 1100px) {
  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 900px) {
  .admin-page {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    flex-basis: auto;
    position: static;
    height: auto;
    border-right: none;
    border-bottom: 1px solid var(--gray-200);
    padding: 14px 16px;
    gap: 12px;
  }

  .nav {
    margin-top: 0;
    flex-direction: row;
    overflow-x: auto;
  }

  .nav-item {
    width: auto;
    flex: 0 0 auto;
  }

  .sidebar-footer {
    display: none;
  }

  .mobile-logout {
    display: inline-flex;
  }

  .admin-meta {
    display: none;
  }

  .topbar {
    padding: 14px 18px;
  }

  .content {
    padding: 20px 18px 32px;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .span-2 {
    grid-column: span 1;
  }

  .form-card {
    padding: 20px;
  }
}

@media (max-width: 560px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .topbar-titles p {
    display: none;
  }

  .form-actions,
  .modal-actions {
    flex-direction: column-reverse;
  }

  .form-actions .btn,
  .modal-actions .btn {
    width: 100%;
  }
}

/* ================= 无障碍：减少动态效果 ================= */

@media (prefers-reduced-motion: reduce) {
  .admin-page *,
  .admin-page *::before,
  .admin-page *::after {
    transition-duration: 0.01ms !important;
    animation-duration: 0.01ms !important;
  }

  .btn:hover,
  .stat-card:hover,
  .btn:active,
  .stat-card:hover .stat-icon {
    transform: none;
  }
}
</style>
