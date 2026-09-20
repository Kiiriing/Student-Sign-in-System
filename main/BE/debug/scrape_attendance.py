import os
import sys
import time
import csv
from datetime import datetime

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

try:
    from webdriver_manager.chrome import ChromeDriverManager
    AUTO_DRIVER = True
except ImportError:
    AUTO_DRIVER = False


# ============================================================
# 配置
# ============================================================

# 外部签到页面
EXT_URL = "http://10.32.54.172:8080/attendance"
EXT_ROW_XPATH = '//*[@id="app"]/section/main/div/div/div[2]/div[2]/div[3]/table/tbody/tr[23]'

# 自己的学生仪表盘
OWN_URL = "http://10.32.54.193:5173/student/dashboard"
OWN_ROW_XPATH = '//*[@id="app"]/div/main/section[4]/div[2]/div/table/tbody/tr[23]'

# 登录配置（学生账号）
LOGIN_URL = "http://10.32.54.193:5173/"  # 前端首页，会重定向到登录
LOGIN_API = "http://10.32.54.193:5000/api/auth/login"
STUDENT_USERNAME = "253201323"
STUDENT_PASSWORD = "123456"

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    f"attendance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
)

HEADERS = ["序号", "姓名", "学号", "班级", "状态", "签到时间", "IP"]

# 等待时长（秒）
WAIT_TIMEOUT = 30


# ============================================================
# 主逻辑
# ============================================================

def build_driver():
    """构建 Chrome driver"""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--lang=zh-CN")
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    if AUTO_DRIVER:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
    else:
        service = Service()
        driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.set_page_load_timeout(60)
    return driver


def wait_row_stable(driver, xpath, max_wait=15):
    """等待行内容稳定（处理异步渲染）"""
    last_text = ""
    stable_ticks = 0
    waited = 0
    while stable_ticks < 3 and waited < max_wait:
        try:
            rows = driver.find_elements(By.XPATH, xpath)
            current_text = " | ".join([r.text for r in rows])
            if current_text == last_text and current_text:
                stable_ticks += 1
            else:
                stable_ticks = 0
                last_text = current_text
        except Exception:
            pass
        time.sleep(0.5)
        waited += 0.5


def parse_row(row):
    """解析单行，返回字段列表"""
    try:
        cells = row.find_elements(By.XPATH, "./td")
    except Exception:
        return None

    # 单元格内的换行符替换为空格，避免 CSV 解析错位
    values = [c.text.strip().replace("\n", " ").replace("\r", " ") for c in cells]

    if len(values) < 7:
        values = values + [""] * (7 - len(values))
    elif len(values) > 7:
        values = values[:6] + [" ".join(values[6:])]

    return values


def fetch_external(driver):
    """抓取外部签到页面第 23 行"""
    print(f"[INFO] 正在加载外部签到页面: {EXT_URL}")
    driver.get(EXT_URL)

    try:
        WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH, EXT_ROW_XPATH))
        )
    except Exception:
        print("[错误] 等待外部表格超时")
        debug_path = os.path.join(OUTPUT_DIR, "debug_external.html")
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source or "")
        print(f"[INFO] 页面源码已保存到: {debug_path}")
        return None

    wait_row_stable(driver, EXT_ROW_XPATH)

    try:
        row = driver.find_element(By.XPATH, EXT_ROW_XPATH)
        parsed = parse_row(row)
        print(f"[INFO] 外部页面抓取成功: {parsed}")
        return parsed
    except Exception as e:
        print(f"[错误] 外部页面抓取失败: {e}")
        return None


def login_student(driver):
    """登录学生系统，将 JWT 写入 localStorage"""
    import json

    print(f"[INFO] 正在登录学生系统: {STUDENT_USERNAME}")

    # 先访问前端，让 localStorage 域生效
    driver.get(LOGIN_URL)
    time.sleep(2)

    # 调用登录 API
    login_script = f"""
    var callback = arguments[arguments.length - 1];
    fetch('{LOGIN_API}', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{
            username: '{STUDENT_USERNAME}',
            password: '{STUDENT_PASSWORD}',
            device_id: 'scraper-' + Date.now()
        }})
    }})
    .then(r => r.json())
    .then(data => callback(data))
    .catch(err => callback({{error: err.toString()}}));
    """

    try:
        result = driver.execute_async_script(login_script)
        if not result or result.get("code") != 200:
            print(f"[错误] 登录失败: {result}")
            return False

        access_token = result.get("access_token", "")
        user_data = {
            "user_id": result.get("user_id", ""),
            "username": result.get("username", ""),
            "role": result.get("role", 0),
            "student_id": result.get("student_id", ""),
            "student_no": result.get("student_no", ""),
            "student_name": result.get("student_name", ""),
            "class_name": result.get("class_name", ""),
        }

        # 写入 localStorage
        set_ls_script = f"""
        localStorage.setItem('access_token', '{access_token}');
        localStorage.setItem('user', JSON.stringify({json.dumps(user_data, ensure_ascii=False)}));
        """
        driver.execute_script(set_ls_script)
        print(f"[INFO] 登录成功: {user_data.get('student_name', '')} ({user_data.get('student_no', '')})")
        return True

    except Exception as e:
        print(f"[错误] 登录异常: {e}")
        return False


def fetch_own(driver):
    """抓取自己仪表盘的班级签到表第 23 行 + 签到记录的签到时间和 IP"""
    print(f"[INFO] 正在加载学生仪表盘: {OWN_URL}")

    # 登录
    if not login_student(driver):
        return None

    # 导航到仪表盘
    driver.get(OWN_URL)
    time.sleep(2)

    # ------------------------------------------------------------
    # 1. 抓取班级签到表第 23 行
    # ------------------------------------------------------------
    try:
        WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH, OWN_ROW_XPATH))
        )
    except Exception:
        print("[错误] 等待班级签到表超时")
        debug_path = os.path.join(OUTPUT_DIR, "debug_own.html")
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source or "")
        print(f"[INFO] 页面源码已保存到: {debug_path}")
        try:
            driver.save_screenshot(os.path.join(OUTPUT_DIR, "debug_own.png"))
        except Exception:
            pass
        return None

    wait_row_stable(driver, OWN_ROW_XPATH)

    try:
        row = driver.find_element(By.XPATH, OWN_ROW_XPATH)
        parsed = parse_row(row)
        print(f"[INFO] 仪表盘抓取成功: {parsed}")
    except Exception as e:
        print(f"[错误] 仪表盘抓取失败: {e}")
        return None

    # ------------------------------------------------------------
    # 2. 抓取签到记录表中的签到时间和 IP
    #
    # XPath:
    #   时间: //*[@id="app"]/div/main/section[3]/div[2]/table/tbody/tr/td[3]/span
    #   IP:   //*[@id="app"]/div/main/section[3]/div[2]/table/tbody/tr/td[4]/span
    #
    # 多行多单元格，合并所有匹配文本
    # ------------------------------------------------------------
    time_xpath = '//*[@id="app"]/div/main/section[3]/div[2]/table/tbody/tr/td[3]/span'
    ip_xpath = '//*[@id="app"]/div/main/section[3]/div[2]/table/tbody/tr/td[4]/span'

    try:
        time_elements = driver.find_elements(By.XPATH, time_xpath)
        sign_time = " ".join(
            [t.text.strip().replace("\n", " ").replace("\r", " ")
             for t in time_elements if t.text.strip()]
        )
        print(f"[INFO] 签到时间: {sign_time}")
    except Exception as e:
        print(f"[WARN] 签到时间抓取失败: {e}")
        sign_time = ""

    try:
        ip_elements = driver.find_elements(By.XPATH, ip_xpath)
        sign_ip = " ".join(
            [t.text.strip().replace("\n", " ").replace("\r", " ")
             for t in ip_elements if t.text.strip()]
        )
        print(f"[INFO] 签到IP: {sign_ip}")
    except Exception as e:
        print(f"[WARN] 签到IP抓取失败: {e}")
        sign_ip = ""

    # ------------------------------------------------------------
    # 3. 拼接到第 23 行解析结果后
    #
    # parsed 格式: [序号, 姓名, 学号, 班级, 状态, 签到时间, IP]
    # 直接替换第 5、6 列（签到时间、IP）
    # ------------------------------------------------------------
    if parsed and len(parsed) >= 7:
        parsed[5] = sign_time or parsed[5]
        parsed[6] = sign_ip or parsed[6]

    return parsed


def save_csv(rows):
    """保存到 CSV（UTF-8 BOM，Excel 可直接打开）"""
    output = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    with open(output, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(HEADERS)
        for r in rows:
            if r:
                writer.writerow(r)
    print(f"[INFO] 已保存: {output}")
    print(f"[INFO] 共写入 {len([r for r in rows if r])} 行数据")


def main():
    print("=" * 60)
    print("  签到表爬虫（双源）")
    print(f"  外部源: {EXT_URL}")
    print(f"  自有源: {OWN_URL}")
    print(f"  输出: {OUTPUT_FILE}")
    print("=" * 60)

    if not AUTO_DRIVER:
        print("[WARN] 未安装 webdriver-manager，将使用系统 PATH 中的 chromedriver")
        print("       建议执行: pip install webdriver-manager")

    driver = None
    try:
        driver = build_driver()

        # 1. 抓取外部签到页面
        print("\n--- [1/2] 抓取外部签到页面 ---")
        ext_data = fetch_external(driver)

        # 2. 抓取自己仪表盘的班级签到表
        print("\n--- [2/2] 抓取自己仪表盘 ---")
        own_data = fetch_own(driver)

        # 汇总
        all_data = []
        if ext_data:
            all_data.append(ext_data)
        if own_data:
            all_data.append(own_data)

        if not all_data:
            print("[错误] 两个源均未抓取到数据")
            return

        save_csv(all_data)

        # 控制台预览
        print("-" * 60)
        print("预览：")
        print(" | ".join(HEADERS))
        for d in all_data:
            print(" | ".join(d))

    except Exception as e:
        print(f"[错误] {e}")
        if driver:
            try:
                debug_path = os.path.join(OUTPUT_DIR, "debug_error.png")
                driver.save_screenshot(debug_path)
                print(f"[INFO] 错误截图已保存: {debug_path}")
            except Exception:
                pass
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


if __name__ == "__main__":
    main()
