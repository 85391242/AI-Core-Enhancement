#!/usr/bin/env python3
# 自动化卸载程序 v1.0
import os
import shutil
import sys
import platform

class Uninstaller:
    def __init__(self, silent=False):
        self.silent = silent
        self.install_dir = "/opt/ai-autopilot" if os.name == 'posix' else "C:\\AI-Autopilot"
        self.backup_dir = None

    def stop_services(self):
        """停止运行中的服务"""
        if not self.silent:
            print("🛑 停止AI自治服务...")
        
        if platform.system() == "Linux":
            os.system("systemctl stop ai-autopilot")
            os.system("systemctl disable ai-autopilot")
            os.remove("/etc/systemd/system/ai-autopilot.service")
            os.system("systemctl daemon-reload")
        elif platform.system() == "Windows":
            import win32com.client
            scheduler = win32com.client.Dispatch("Schedule.Service")
            scheduler.Connect()
            scheduler.GetFolder("\\").DeleteTask("AI Autopilot", 0)

    def remove_files(self):
        """删除安装文件"""
        if not self.silent:
            print("🗑️ 删除安装文件...")
        
        if os.path.exists(self.install_dir):
            # 创建卸载备份
            self.backup_dir = f"{self.install_dir}_uninstalled_{int(time.time())}"
            shutil.move(self.install_dir, self.backup_dir)

    def cleanup(self):
        """清理残留"""
        if not self.silent:
            print("🧹 清理系统残留...")
        
        # 删除日志文件
        log_files = [
            "/var/log/ai-autopilot.log",
            "C:\\ProgramData\\AI-Autopilot\\autopilot.log"
        ]
        
        for log_file in log_files:
            if os.path.exists(log_file):
                os.remove(log_file)

    def run(self):
        """执行卸载流程"""
        try:
            self.stop_services()
            self.remove_files()
            self.cleanup()
            
            if not self.silent:
                print("✅ 卸载完成")
                if self.backup_dir:
                    print(f"备份已保存到: {self.backup_dir}")
        except Exception as e:
            print(f"❌ 卸载失败: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--silent", action="store_true", help="静默模式卸载")
    args = parser.parse_args()
    
    uninstaller = Uninstaller(silent=args.silent)
    uninstaller.run()