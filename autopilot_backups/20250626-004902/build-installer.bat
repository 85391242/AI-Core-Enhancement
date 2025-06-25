@echo off
:: AI自治系统一键部署脚本
:: 版本: 2.0.0

setlocal enabledelayedexpansion

echo 正在准备AI自治系统安装包...
if not exist "dist" mkdir dist

:: 复制必要文件
xcopy /s /y "..\.ai-autopilot.py" "dist\"
xcopy /s /y "..\.knowledge-mgr.py" "dist\"
xcopy /s /y "..\.craft-config.json" "dist\"
xcopy /s /y "..\modules\" "dist\modules\"
copy /y "auto-installer.py" "dist\"

:: 创建安装脚本
echo @echo off > "dist\install.bat"
echo python auto-installer.py %%* >> "dist\install.bat"

:: 创建静默安装脚本
echo @echo off > "dist\install-silent.bat"
echo python auto-installer.py --silent >> "dist\install-silent.bat"

:: 打包成ZIP
powershell -command "Compress-Archive -Path dist\* -DestinationPath AI-Autopilot-2.0.0.zip -Force"

echo 安装包构建完成: AI-Autopilot-2.0.0.zip
endlocal