@echo off
echo === AI-Core-Enhancement 本地一键部署脚本 ===
echo 正在检查Python环境...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误：未检测到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo 正在创建虚拟环境...
python -m venv .venv
if %errorlevel% neq 0 (
    echo 错误：创建虚拟环境失败
    pause
    exit /b 1
)

echo 激活虚拟环境...
call .venv\Scripts\activate
if %errorlevel% neq 0 (
    echo 错误：激活虚拟环境失败
    pause
    exit /b 1
)

echo 安装依赖包...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 错误：依赖安装失败
    pause
    exit /b 1
)

echo 启动应用程序...
python start_autopilot.py
if %errorlevel% neq 0 (
    echo 错误：启动应用失败
    pause
    exit /b 1
)

pause