#!/usr/bin/env python3
# 应急恢复系统 v1.2
import os
import sys
import subprocess
from pathlib import Path

class RecoverySystem:
    def __init__(self):
        self.install_dir = Path(__file__).parent.parent
        self.checklist = self.install_dir / "execution-checklist.md"
        self.log_file = self.install_dir / "recovery.log"

    def check_services(self):
        """检测关键服务状态"""
        try:
            if os.name == 'nt':  # Windows
                cmd = f"Get-Process python | Where-Object {{ $_.CommandLine -match 'ai-autopilot' }}"
                result = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
                return "python.exe" in result.stdout
            else:  # Linux/macOS
                result = subprocess.run(["systemctl", "is-active", "ai-autopilot"], 
                                      capture_output=True, text=True)
                return "active" in result.stdout
        except Exception as e:
            self._log_error(f"服务检测失败: {str(e)}")
            return False

    def resume_automation(self):
        """恢复自动化流程"""
        try:
            # 重启核心服务
            if os.name == 'nt':
                subprocess.run(["powershell", "-Command", 
                              f"Start-Process -NoNewWindow -FilePath python -ArgumentList '{self.install_dir}/.ai-autopilot.py'"],
                              check=True)
            else:
                subprocess.run(["systemctl", "restart", "ai-autopilot"], check=True)
            
            # 更新执行清单
            with open(self.checklist, 'r+') as f:
                content = f.read()
                content = content.replace("- [ ]", "- [x]")
                f.seek(0)
                f.write(content)
                f.truncate()
            
            self._log_status("自动化流程已恢复")
            return True
        except subprocess.CalledProcessError as e:
            self._log_error(f"流程恢复失败: {str(e)}")
            return False

    def _log_status(self, message):
        """记录状态日志"""
        with open(self.log_file, 'a') as f:
            f.write(f"[SUCCESS] {message}\n")

    def _log_error(self, message):
        """记录错误日志"""
        with open(self.log_file, 'a') as f:
            f.write(f"[ERROR] {message}\n")

    def run(self, args):
        """执行恢复操作"""
        if '--resume-all' in args:
            if not self.check_services():
                return self.resume_automation()
            print("所有服务运行正常，无需恢复")
            return True
        else:
            print("可用参数: --resume-all")
            return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume-all", action="store_true", help="恢复所有自动化流程")
    args = parser.parse_args()
    
    recovery = RecoverySystem()
    if not recovery.run(sys.argv[1:]):
        sys.exit(1)