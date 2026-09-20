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
                      <td class="cell-muted">{{ formatTime(row.create_time) }}</td>
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
                    <tr v-for="row in students" :key="row.user_id">
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
                      <td class="cell-muted">{{ formatTime(row.create_time) }}</td>
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
                    <tr v-if="students.length === 0">
                      <td colspan="8" class="empty-cell">暂无学生账户，请先在「新建学生」中创建</td>
                    </tr>
                  </tbody>
                </table>
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
                  <select id="s-class" v-model="studentForm.class_id" class="form-input form-select">
                    <option value="">暂不分配班级</option>
                    <option v-for="item in classes" :key="item.id" :value="item.id">
                      {{ item.name }}{{ item.grade ? '（' + item.grade + '）' : '' }}
                    </option>
                  </select>
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
                <p>为指定教师和班级安排一次课程，上课日期与时间段用于学生端课表展示。</p>
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
                  <select id="c-teacher" v-model="courseForm.teacher_id" class="form-input form-select">
                    <option value="" disabled>请选择教师</option>
                    <option v-for="item in teachers" :key="item.teacher_id" :value="item.teacher_id">
                      {{ item.name }}{{ item.department ? '（' + item.department + '）' : '' }}
                    </option>
                  </select>
                </div>
                <div class="form-field">
                  <label for="c-class">上课班级 <span class="required">*</span></label>
                  <select id="c-class" v-model="courseForm.class_id" class="form-input form-select">
                    <option value="" disabled>请选择班级</option>
                    <option v-for="item in classes" :key="item.id" :value="item.id">
                      {{ item.name }}{{ item.grade ? '（' + item.grade + '）' : '' }}
                    </option>
                  </select>
                </div>
                <div class="form-field">
                  <label for="c-date">上课日期</label>
                  <input id="c-date" v-model="courseForm.course_date" class="form-input" type="date">
                </div>
                <div class="form-field">
                  <label for="c-time">上课时间段</label>
                  <input id="c-time" v-model="courseForm.time" class="form-input" type="text" placeholder="请输入，格式为 08:00-09:40">
                  <p class="field-hint">请按 <span class="mono">HH:mm-HH:mm</span> 格式填写，例如 <span class="mono">08:00-09:40</span></p>
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
                    <tr v-for="item in courses" :key="item.id">
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
                    <tr v-if="courses.length === 0">
                      <td colspan="6" class="empty-cell">暂无课程安排</td>
                    </tr>
                  </tbody>
                </table>
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
                  <select id="cl-teacher" v-model="classForm.teacher_id" class="form-input form-select">
                    <option value="">暂不指定班主任</option>
                    <option v-for="item in teachers" :key="item.teacher_id" :value="item.teacher_id">
                      {{ item.name }}{{ item.department ? '（' + item.department + '）' : '' }}
                    </option>
                  </select>
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
          <select id="assign-class" v-model="assignModal.class_id" class="form-input form-select">
            <option value="">未分配</option>
            <option v-for="item in classes" :key="item.id" :value="item.id">
              {{ item.name }}{{ item.grade ? '（' + item.grade + '）' : '' }}
            </option>
          </select>
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
import { reactive, ref, onMounted, nextTick, type Ref } from "vue"
import { useRouter } from "vue-router"
import request from "../api/request"

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

interface ApiResult<T> {
  code: number
  message?: string
  data?: T
}

type TabKey = "accounts" | "createTeacher" | "createStudent" | "createCourse" | "classManagement"
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

const pageLoading = ref(true)
const pageError = ref("")

const adminUsername = ref("管理员")
const adminInitial = ref("管")

const teachers = ref<TeacherRow[]>([])
const students = ref<StudentRow[]>([])
const classes = ref<ClassRow[]>([])
const courses = ref<CourseRow[]>([])

const tabMeta: Record<TabKey, { title: string; desc: string }> = {
  accounts: { title: "账户管理", desc: "管理教师与学生账户，可重置密码、分配班级、启用或禁用账号" },
  createTeacher: { title: "新建教师", desc: "创建教师登录账号并维护基本信息" },
  createStudent: { title: "新建学生", desc: "创建学生登录账号，学号全局唯一" },
  createCourse: { title: "新建课程", desc: "为教师与班级安排课程及上课时间" },
  classManagement: { title: "班级管理", desc: "创建与删除班级，维护班级基础信息" }
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
  time: ""
})

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

function formatTime(value?: string | null): string {
  if (!value) {
    return "-"
  }
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return value
  }
  const month = String(date.getMonth() + 1).padStart(2, "0")
  const day = String(date.getDate()).padStart(2, "0")
  const hour = String(date.getHours()).padStart(2, "0")
  const minute = String(date.getMinutes()).padStart(2, "0")
  return `${date.getFullYear()}-${month}-${day} ${hour}:${minute}`
}

function validPhone(phone: string): boolean {
  return phone === "" || /^1\d{10}$/.test(phone)
}

// 校验时间段格式 HH:mm-HH:mm（小时 00-23，分钟 00-59），且结束时间不早于开始时间
function validTimeRange(value: string): boolean {
  const m = /^([01]\d|2[0-3]):([0-5]\d)-([01]\d|2[0-3]):([0-5]\d)$/.exec(value.trim())
  if (!m) return false
  const startMin = parseInt(m[1], 10) * 60 + parseInt(m[2], 10)
  const endMin = parseInt(m[3], 10) * 60 + parseInt(m[4], 10)
  return endMin >= startMin
}

function errorMessage(error: unknown, fallback: string): string {
  const err = error as { response?: { data?: { message?: string } } }
  return err?.response?.data?.message || fallback
}

function isAuthError(error: unknown): boolean {
  const status = (error as { response?: { status?: number } })?.response?.status
  return status === 401 || status === 403
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

async function loadAll(): Promise<void> {
  pageLoading.value = true
  pageError.value = ""
  try {
    await Promise.all([
      fetchProfile(),
      fetchTeachers(),
      fetchStudents(),
      fetchClasses(),
      fetchCourses()
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
  courseForm.time = ""
}

function clearCourseForm() {
  resetCourseForm()
  courseAlert.value.show = false
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
  if (courseForm.time.trim() && !validTimeRange(courseForm.time)) {
    setAlert(courseAlert, "error", "上课时间段格式不正确，请按 HH:mm-HH:mm 填写（例如 08:00-09:40），且结束时间不早于开始时间")
    return
  }

  courseSubmitting.value = true
  try {
    const res = await request.post<ApiResult<null>>("/api/admin/courses/create", {
      name: courseForm.name.trim(),
      teacher_id: courseForm.teacher_id,
      class_id: courseForm.class_id,
      course_date: courseForm.course_date || null,
      time: courseForm.time.trim() || null
    })
    if (res.data.code === 200) {
      setAlert(courseAlert, "success", `课程「${courseForm.name.trim()}」创建成功`)
      showToast("课程创建成功")
      courseForm.name = ""
      courseForm.time = ""
      await fetchCourses()
    } else {
      setAlert(courseAlert, "error", res.data.message || "创建失败")
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

.row-actions {
  display: flex;
  gap: 8px;
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

.form-select {
  appearance: none;
  padding-right: 36px;
  cursor: pointer;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%236b7280' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
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
