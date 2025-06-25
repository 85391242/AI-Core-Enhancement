#!/usr/bin/env python3
# 全自动部署安装器 v1.0
import os
import sys
import shutil
import subprocess
from pathlib import Path

class AutoInstaller:
    def __init__(self, silent=False):
        self.silent = silent
        self.install_dir = "/opt/ai-autopilot" if os.name == 'posix' else "C:\\AI-Autopilot"
        self.backup_dir = None

    def prepare_environment(self):
        """准备安装环境"""
        if not self.silent:
            print("🔍 检测系统环境...")
        
        # 创建备份目录
        self.backup_dir = f"{self.install_dir}_backup_{int(time.time())}"
        
        # 检查管理员权限
        if os.name == 'posix' and os.geteuid() != 0:
            print("❌ 需要root权限执行安装")
            sys.exit(1)

    def backup_existing(self):
        """备份现有安装"""
        if os.path.exists(self.install_dir):
            if not self.silent:
                print(f"📦 备份现有安装到 {self.backup_dir}...")
            shutil.copytree(self.install_dir, self.backup_dir)

    def install_files(self):
        """安装工程文件"""
        if not self.silent:
            print("🚀 安装系统文件中...")
        
        os.makedirs(self.install_dir, exist_ok=True)
        
        # 核心文件列表
        files_to_install = [
            '.ai-autopilot.py',
            '.knowledge-mgr.py',
            '.craft-config.json',
            'modules/'
        ]
        
        for file in files_to_install:
            src = Path(file)
            dst = Path(self.install_dir) / file
            if src.is_dir():
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)

    def setup_services(self):
        """配置系统服务"""
        if os.name == 'posix':
            # Linux系统服务配置
            service_content = f"""
[Unit]
Description=AI Autopilot Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 {self.install_dir}/.ai-autopilot.py
WorkingDirectory={self.install_dir}
Restart=always
User=root

[Install]
WantedBy=multi-user.target
"""
            with open("/etc/systemd/system/ai-autopilot.service", "w") as f:
                f.write(service_content)
            
            subprocess.run(["systemctl", "daemon-reload"])
            subprocess.run(["systemctl", "enable", "--now", "ai-autopilot"])
        else:
            # Windows计划任务
            import win32com.client
            scheduler = win32com.client.Dispatch("Schedule.Service")
            scheduler.Connect()
            root_folder = scheduler.GetFolder("\\")
            
            task_def = scheduler.NewTask(0)
            task_def.RegistrationInfo.Description = "AI Autopilot Service"
            
            # 配置触发器(系统启动时)
            trigger = task_def.Triggers.Create(8)  # 8表示启动触发器
            trigger.Enabled = True
            
            # 配置操作
            action = task_def.Actions.Create(0)
            action.Path = "python.exe"
            action.Arguments = f"{self.install_dir}\\.ai-autopilot.py"
            action.WorkingDirectory = self.install_dir
            
            # 注册任务
            root_folder.RegisterTaskDefinition(
                "AI Autopilot", 
                task_def, 
                6,  # 6表示创建或更新
                "", "", 3  # 3表示不管用户是否登录都运行
            )

    def post_install(self):
        """安装后检查"""
        if not self.silent:
            print("✅ 验证安装结果...")
        
        check_cmds = [
            f"python {self.install_dir}/.knowledge-mgr.py --validate",
            f"python {self.install_dir}/.ai-autopilot.py --health-check"
        ]
        
        for cmd in check_cmds:
            if subprocess.call(cmd, shell=True) != 0:
                print(f"⚠️ 安装验证失败: {cmd}")
                self.rollback()
                sys.exit(1)

    def rollback(self):
        """安装失败回滚"""
        if self.backup_dir and os.path.exists(self.backup_dir):
            if not self.silent:
                print("🔄 恢复备份...")
            shutil.rmtree(self.install_dir)
            shutil.move(self.backup_dir, self.install_dir)

    def run(self):
        """执行安装流程"""
        try:
            self.prepare_environment()
            self.backup_existing()
            self.install_files()
            self.setup_services()
            self.post_install()
            
            if not self.silent:
                print(f"🎉 安装成功！服务已启动")
                print(f"安装目录: {self.install_dir}")
                if self.backup_dir:
                    print(f"备份目录: {self.backup_dir}")
        except Exception as e:
            print(f"❌ 安装失败: {str(e)}")
            self.rollback()
            sys.exit(1)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--silent", action="store_true", help="静默模式安装")
    args = parser.parse_args()
    
    installer = AutoInstaller(silent=args.silent)
    installer.run()