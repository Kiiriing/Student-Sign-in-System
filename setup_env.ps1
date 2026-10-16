# =========================================
# 学生签到系统 - 一键环境初始化脚本
# 功能：
#   1. 放开 PowerShell 执行策略（当前用户）
#   2. 用 Anaconda Python 安装后端依赖
# =========================================

Write-Host "==== 学生签到系统环境初始化 ====" -ForegroundColor Cyan

# ---------- 1. 放开执行策略 ----------
Write-Host "`n[1/2] 设置 PowerShell 执行策略为 RemoteSigned (CurrentUser)..." -ForegroundColor Yellow

try {
    Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
    Write-Host "  [OK] 执行策略已设置为 RemoteSigned" -ForegroundColor Green
} catch {
    Write-Host "  [警告] 设置执行策略失败：$_" -ForegroundColor Red
    Write-Host "  请手动以管理员身份运行：Set-ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Red
}

# 显示当前策略
$policy = Get-ExecutionPolicy -Scope CurrentUser
Write-Host "  当前 CurrentUser 策略：$policy" -ForegroundColor Gray

# ---------- 2. 安装 Python 依赖 ----------
Write-Host "`n[2/2] 安装 Python 后端依赖..." -ForegroundColor Yellow

$python = "C:/ProgramData/anaconda3/python.exe"

if (-not (Test-Path $python)) {
    Write-Host "  [错误] 找不到 Python：$python" -ForegroundColor Red
    Write-Host "  请确认 Anaconda 安装路径，或修改脚本里的 `$python 变量" -ForegroundColor Red
    exit 1
}

Write-Host "  使用解释器：$python" -ForegroundColor Gray

$packages = @(
    "flask",
    "flask-cors",
    "flask-jwt-extended",
    "pymysql",
    "cryptography"
)

$mirror = "https://pypi.tuna.tsinghua.edu.cn/simple"

& $python -m pip install @packages -i $mirror

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n  [OK] 所有依赖安装完成" -ForegroundColor Green
} else {
    Write-Host "`n  [错误] 依赖安装失败，退出码：$LASTEXITCODE" -ForegroundColor Red
    exit 1
}

# ---------- 验证 ----------
Write-Host "`n[验证] 检查关键包是否可导入..." -ForegroundColor Yellow

& $python -c "import flask, flask_cors, flask_jwt_extended, pymysql, cryptography; print('  所有包导入成功')"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n==== 初始化完成，可以启动后端了 ====" -ForegroundColor Cyan
} else {
    Write-Host "`n==== 部分包导入失败，请检查上面的输出 ====" -ForegroundColor Red
}