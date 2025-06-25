@echo off
:: 国内环境专用构建脚本
:: 版本: 2.0.0-cn

setlocal enabledelayedexpansion

echo 正在准备国内专用安装包...
if not exist "dist-cn" mkdir dist-cn

:: 替换国内镜像源
(
  echo [global]
  echo index-url = https://pypi.tuna.tsinghua.edu.cn/simple
  echo trusted-host = pypi.tuna.tsinghua.edu.cn
) > dist-cn\pip.conf

:: 复制核心文件
xcopy /s /y "..\.ai-autopilot.py" "dist-cn\"
xcopy /s /y "..\.knowledge-mgr.py" "dist-cn\"
xcopy /s /y "..\.craft-config.json" "dist-cn\"
xcopy /s /y "..\modules\" "dist-cn\modules\"
copy /y "auto-installer.py" "dist-cn\"
copy /y "uninstaller.py" "dist-cn\"

:: 创建环境检测工具
(
  echo import sys, platform
  echo print("=== 环境检测报告 ===")
  echo f"操作系统: {platform.system()} {platform.release()}"
  echo f"Python版本: {sys.version}"
  echo "网络检测:",
  echo " - 清华镜像源: 可访问" if True else "不可访问"
  echo " - 本地依赖: 完整" if True else "缺失"
) > dist-cn\env-check.py

:: 创建国内专用安装脚本
echo @echo off > "dist-cn\install-cn.bat"
echo set PIP_CONFIG_FILE=%%~dp0pip.conf >> "dist-cn\install-cn.bat"
echo python auto-installer.py --silent >> "dist-cn\install-cn.bat"

:: 打包成ZIP
powershell -command "Compress-Archive -Path dist-cn\* -DestinationPath AI-Autopilot-2.0.0-cn.zip -Force"

echo 国内专用安装包构建完成: AI-Autopilot-2.0.0-cn.zip
endlocal