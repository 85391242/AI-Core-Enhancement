@echo off
REM 自动启动AI自治代理的批处理脚本
set VENV_PATH=D:\AI-Core-Enhancement\.venv\Scripts\activate
set PYTHON_SCRIPT=D:\AI-Core-Enhancement\.ai-autopilot.py

echo 正在启动AI自治代理...
call %VENV_PATH%
python %PYTHON_SCRIPT%
pause