#!/usr/bin/env python3
# 环境修复工具 v1.3
import os
import sys
import platform
import subprocess
from pathlib import Path

class PythonEnvFixer:
    REQUIRED_VERSION = (3, 11)
    WINDOWS_PATHS = [
        r"C:\Python311",
        r"C:\Program Files\Python311",
        r"C:\Users\{}\AppData\Local\Programs\Python\Python311".format(os.getenv("USERNAME"))
    ]

    def __init__(self):
        self.system = platform.system()
        self.python_path = sys.executable
        self.is_admin = self.check_admin()

    def check_admin(self):
        """检查管理员权限"""
        try:
            if self.system == "Windows":
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.getuid() == 0
        except:
            return False

    def verify_python(self):
        """验证Python环境"""
        try:
            version = sys.version_info
            if version >= self.REQUIRED_VERSION:
                print(f"✅ Python {version.major}.{version.minor}.{version.micro} 已正确安装")
                return True
            else:
                print(f"❌ 需要Python 3.11+，当前版本: {version.major}.{version.minor}.{version.micro}")
                return False
        except Exception as e:
            print(f"Python检测失败: {str(e)}")
            return False

    def fix_windows_path(self):
        """修复Windows PATH环境变量"""
        if not self.is_admin:
            print("⚠️ 需要管理员权限来修改系统PATH")
            return False

        python_dir = str(Path(self.python_path).parent)
        try:
            import winreg
            with winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE) as hklm:
                with winreg.OpenKey(hklm, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment", 0, winreg.KEY_ALL_ACCESS) as key:
                    path_value = winreg.QueryValueEx(key, "PATH")[0]
                    if python_dir not in path_value:
                        new_path = f"{path_value};{python_dir}"
                        winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
                        print(f"✅ 已添加Python目录到系统PATH: {python_dir}")
                        return True
                    else:
                        print("✅ Python目录已在系统PATH中")
                        return True
        except Exception as e:
            print(f"PATH修改失败: {str(e)}")
            return False

    def refresh_environment(self):
        """刷新环境变量"""
        print("\n⚠️ 请执行以下操作使更改生效：")
        if self.system == "Windows":
            print("1. 打开新的PowerShell窗口")
            print("2. 运行: refreshenv 或 重启电脑")
        else:
            print("1. 运行: source ~/.bashrc 或重启终端")

    def run(self):
        """执行修复流程"""
        print("=== Python环境诊断 ===")
        if not self.verify_python():
            print("\n请从官网下载Python 3.11+并安装:")
            print("https://www.python.org/downloads/")
            return False

        if self.system == "Windows":
            if not self.fix_windows_path():
                self.refresh_environment()
                return False

        self.refresh_environment()
        return True

if __name__ == "__main__":
    fixer = PythonEnvFixer()
    if not fixer.run():
        sys.exit(1)