# -*- coding: utf-8 -*-
"""
测试脚本签到检测系统

目的：
    验证 student.py 的 _is_script_signin_request() 能否正确识别
    selenium 自动签到，并把签到记录标记为"脚本签到"（is_script=1，
    前端显示红色 badge）。

工作流程：
    1. 用 selenium 启动 Chrome，UA 故意包含 "selenium" 关键字
    2. 在浏览器里走完整登录流程（填表 → 点登录按钮）
    3. 进入学生仪表盘后点击"立即签到"按钮
    4. 前端发出 POST /api/student/signin 请求
    5. 后端 _is_script_signin_request() 命中 UA 关键字 → is_script=1
    6. 用 selenium 执行 JS 拉取 /api/student/records，打印最新一条
       记录的 is_script 和 status_text，看是否为 1 / "脚本签到"

预期结果：
    - 后端签到接口返回 status_text="脚本签到"
    - 签到记录列表最新一条 is_script=1，status_text="脚本签到"
    - 学生仪表盘和教师签到名册该条记录显示为红色

依赖：
    pip install selenium
    pip install webdriver-manager  (可选，自动下载 chromedriver)

运行：
    python test_script_signin.py

注意：
    本脚本 UA 含 "selenium" 是为了让检测系统识别，是测试用。
    如果想验证"默认 selenium 是否会漏检"，把 SCRIPT_USER_AGENT
    改成普通 Chrome UA 即可（此时检测系统可能识别不到）。
"""

import os
import sys
import time
import json
from datetime import datetime

# Windows UTF-8
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Selenium
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError:
    print("[错误] 未安装 selenium，请先执行：")
    print("    pip install selenium")
    sys.exit(1)

# 自动管理 chromedriver（可选）
try:
    from webdriver_manager.chrome import ChromeDriverManager
    AUTO_DRIVER = True
except ImportError:
    AUTO_DRIVER = False


# ============================================================
# 配置
# ============================================================

# 前端地址（学生端）
FRONTEND_URL = "http://10.32.54.193:5173/login"

# 外部签到系统地址
ATTENDANCE_URL = "http://10.32.54.172:8080/checkin"

# 学生账号
STUDENT_USERNAME = "253201323"
STUDENT_PASSWORD = "123456"

# 外部签到系统学生信息
ATTENDANCE_NAME = "刘佳博"
ATTENDANCE_STUDENT_NO = "253201323"

# 等待时长（秒）
WAIT_TIMEOUT = 5
SHORT_WAIT = 3

# 关键：UA 故意包含 "selenium" 关键字
# 让 student.py 的 _SCRIPT_UA_PATTERNS 命中
#
# 如果想测试"默认 selenium 是否漏检"，把下面这行改成：
#   SCRIPT_USER_AGENT = None
# 此时脚本不设置 UA，Chrome 用默认 UA（不含 selenium），
# 检测系统可能识别不到（取决于其他特征是否触发）。
SCRIPT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "Selenium/ChromeDriver Automation"
)

# 截图目录
SHOT_DIR = os.path.dirname(os.path.abspath(__file__))


# ============================================================
# 工具函数
# ============================================================

def log(msg: str):
    """带时间戳的日志"""
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")


def create_driver() -> webdriver.Chrome:
    """创建 Chrome driver"""
    options = Options()
    # 不使用无头模式：方便观察 + 更接近真实作弊场景
    # options.add_argument("--headless=new")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")

    # 关键：UA 含 selenium，主动让检测系统识别
    if SCRIPT_USER_AGENT:
        options.add_argument(f"--user-agent={SCRIPT_USER_AGENT}")
        log(f"UA 已设置为: {SCRIPT_USER_AGENT}")

    if AUTO_DRIVER:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    else:
        driver = webdriver.Chrome(options=options)

    driver.implicitly_wait(SHORT_WAIT)
    return driver


def signin_external(driver: webdriver.Chrome):
    """打开外部签到系统，自动填写姓名学号并签到"""
    log(f"打开签到系统: {ATTENDANCE_URL}")
    driver.get(ATTENDANCE_URL)
    time.sleep(2)

    wait = WebDriverWait(driver, WAIT_TIMEOUT)

    # 定位姓名输入框（placeholder="请输入姓名"）
    log("定位姓名输入框...")
    name_input = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='姓名']"))
    )
    name_input.clear()
    name_input.send_keys(ATTENDANCE_NAME)
    log(f"已填姓名: {ATTENDANCE_NAME}")

    # 定位学号输入框（placeholder="2532013XX"）
    log("定位学号输入框...")
    no_input = driver.find_element(
        By.CSS_SELECTOR, "input[placeholder*='2532013']"
    )
    no_input.clear()
    no_input.send_keys(ATTENDANCE_STUDENT_NO)
    log(f"已填学号: {ATTENDANCE_STUDENT_NO}")

    # 定位签到按钮（Element Plus，按钮文本在 <span> 内）
    log("定位签到按钮...")
    buttons = driver.find_elements(By.CSS_SELECTOR, "button.el-button")
    signin_btn = None
    for btn in buttons:
        if btn.text.strip() == "签到":
            signin_btn = btn
            break

    if not signin_btn:
        log("[警告] 未找到签到按钮，尝试点击第一个按钮")
        signin_btn = buttons[0] if buttons else None

    if not signin_btn:
        log("[错误] 页面上没有可点击的按钮")
        return

    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});", signin_btn
    )
    time.sleep(0.5)

    log("点击签到按钮...")
    signin_btn.click()

    # 等待签到结果
    time.sleep(2)
    try:
        page_text = driver.find_element(By.TAG_NAME, "body").text
        log(f"签到结果: {page_text[:200]}")
    except Exception:
        log("[警告] 未能读取页面结果")

    log("外部签到系统签到完成")


def login(driver: webdriver.Chrome):
    """在浏览器里走完登录流程"""
    log(f"打开登录页: {FRONTEND_URL}")
    driver.get(FRONTEND_URL)

    wait = WebDriverWait(driver, WAIT_TIMEOUT)

    # 等用户名输入框出现
    log("等待登录页加载...")
    username_input = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='学号']"))
    )

    # 填用户名
    username_input.clear()
    username_input.send_keys(STUDENT_USERNAME)
    log(f"已填用户名: {STUDENT_USERNAME}")

    # 填密码
    password_input = driver.find_element(
        By.CSS_SELECTOR, "input[type='password']"
    )
    password_input.clear()
    password_input.send_keys(STUDENT_PASSWORD)
    log("已填密码")

    # 点登录按钮
    login_btn = driver.find_element(By.CSS_SELECTOR, "button.login-btn")
    login_btn.click()
    log("已点击登录按钮")

    # 等跳转到 /student/dashboard（URL 变化）
    log("等待跳转到学生仪表盘...")
    wait.until(lambda d: "/student" in d.current_url)
    log(f"已登录，当前 URL: {driver.current_url}")

    # 等课程列表加载
    try:
        WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".course-card"))
        )
        log("课程列表已加载")
    except Exception:
        log("[警告] 未发现课程卡片，可能今天没有课程")


def click_signin(driver: webdriver.Chrome):
    """点击第一个'立即签到'按钮"""
    wait = WebDriverWait(driver, WAIT_TIMEOUT)

    # 找所有"立即签到"按钮（btn-primary + course-action 内）
    btns = driver.find_elements(
        By.CSS_SELECTOR, ".course-action button.btn-primary"
    )
    log(f"找到 {len(btns)} 个可签到按钮")

    if not btns:
        log("[警告] 没有进行中的签到任务，无法测试签到")
        return False

    btn = btns[0]
    # 滚动到可见
    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});", btn
    )
    time.sleep(0.5)

    log("点击'立即签到'...")
    btn.click()

    # 等 toast 出现
    try:
        toast = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".toast")))
        # toast 文案可能动态变化，给 1 秒稳定
        time.sleep(1)
        toast_text = toast.text
        log(f"Toast 提示: {toast_text}")
    except Exception:
        log("[警告] 没看到 toast 提示")

    return True


def fetch_latest_record(driver: webdriver.Chrome):
    """通过浏览器 fetch 拉取最新签到记录，验证 is_script"""
    log("通过浏览器 fetch /api/student/records 验证最新记录...")

    js = """
    return (async () => {
        const token = localStorage.getItem('access_token');
        if (!token) return { error: 'no token in localStorage' };
        try {
            const resp = await fetch('/api/student/records', {
                headers: { 'Authorization': 'Bearer ' + token }
            });
            const data = await resp.json();
            return data;
        } catch (e) {
            return { error: String(e) };
        }
    })();
    """

    result = driver.execute_async_script(
        """
        var callback = arguments[arguments.length - 1];
        (async () => {
            const token = localStorage.getItem('access_token');
            if (!token) { callback({error: 'no token'}); return; }
            try {
                const resp = await fetch('/api/student/records', {
                    headers: { 'Authorization': 'Bearer ' + token }
                });
                const data = await resp.json();
                callback(data);
            } catch (e) {
                callback({error: String(e)});
            }
        })();
        """
    )

    if not result or result.get("code") != 200:
        log(f"[错误] /api/student/records 返回: {json.dumps(result, ensure_ascii=False)[:300]}")
        return None

    records = result.get("data") or []
    if not records:
        log("没有签到记录")
        return None

    latest = records[0]
    log("=== 最新一条签到记录 ===")
    log(f"  课程: {latest.get('course_name')}")
    log(f"  状态: {latest.get('status')} ({latest.get('status_text')})")
    log(f"  签到时间: {latest.get('sign_time')}")
    log(f"  IP: {latest.get('ip')}")
    log(f"  is_script: {latest.get('is_script')}")

    if int(latest.get("is_script") or 0) == 1:
        log("[OK] 检测系统识别成功：记录被标记为脚本签到")
    else:
        log("[FAIL] 检测系统漏检：is_script=0，未识别为脚本签到")

    return latest


def main():
    log("=== 测试脚本签到检测系统 ===")
    log(f"脚本运行目录: {SHOT_DIR}")

    driver = None
    try:
        driver = create_driver()
        login(driver)
        click_signin(driver)
        fetch_latest_record(driver)

        # 外部签到系统自动签到
        signin_external(driver)

    except Exception as e:
        log(f"[异常] {e}")
        if driver:
            try:
                driver.save_screenshot(os.path.join(SHOT_DIR, "error.png"))
                log("已保存错误截图: error.png")
            except Exception:
                pass
        raise

    finally:
        if driver:
            log("关闭浏览器...")
            try:
                driver.quit()
            except Exception:
                pass
        log("=== 测试结束 ===")


if __name__ == "__main__":
    main()
