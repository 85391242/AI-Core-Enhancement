@echo off
REM 静默启动AI自治代理的批处理脚本
set VENV_PATH=D:\AI-Core-Enhancement\.venv\Scripts\activate
set PYTHON_SCRIPT=D:\AI-Core-Enhancement\.ai-autopilot.py

call %VENV_PATH%
start "" python %PYTHON_SCRIPT%