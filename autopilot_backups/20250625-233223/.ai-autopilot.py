#!/usr/bin/env python3
# AI自治代理 v1.0
import os
import time
import subprocess
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class AutopilotConfig:
    def __init__(self):
        self.auto_fix = True
        self.auto_backup = True
        self.max_retries = 3
        self.health_check_interval = 3600  # 1小时
        self.storage_max_size = 10  # GB
        self.backup_retention_days = 7

class StorageManager:
    def __init__(self, config):
        self.config = config
        
    def check_disk_usage(self):
        """检查磁盘使用情况"""
        total, used, free = shutil.disk_usage(".")
        return {
            "total_gb": total // (2**30),
            "used_gb": used // (2**30),
            "free_gb": free // (2**30)
        }
        
    def cleanup_old_backups(self):
        """清理过期备份"""
        backup_dir = "autopilot_backups"
        if not os.path.exists(backup_dir):
            return
            
        now = time.time()
        for dirname in os.listdir(backup_dir):
            dirpath = os.path.join(backup_dir, dirname)
            if os.path.isdir(dirpath):
                # 检查备份目录日期
                try:
                    dir_time = time.mktime(
                        time.strptime(dirname[:15], "%Y%m%d-%H%M%S"))
                    if (now - dir_time) > self.config.backup_retention_days * 86400:
                        shutil.rmtree(dirpath)
                        print(f"清理过期备份: {dirname}")
                except ValueError:
                    continue

class AIAutopilot(FileSystemEventHandler):
    def __init__(self):
        self.config = AutopilotConfig()
        self.last_health_check = 0
        self.storage_manager = StorageManager(self.config)
        
    def on_modified(self, event):
        """文件变更自动处理"""
        if not event.is_directory:
            self.auto_backup_if_needed(event.src_path)
            
    def auto_backup_if_needed(self, filepath):
        if self.config.auto_backup:
            try:
                # 规范化路径
                filepath = os.path.normpath(filepath)
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                backup_dir = os.path.normpath(f"autopilot_backups/{timestamp}")
                os.makedirs(backup_dir, exist_ok=True)
                
                # 目标文件路径
                dest_path = os.path.join(backup_dir, os.path.basename(filepath))
                
                # 检查是否相同文件
                if os.path.exists(dest_path):
                    if os.path.samefile(filepath, dest_path):
                        return
                
                if os.name == 'nt':  # Windows
                    shutil.copy2(filepath, dest_path)
                else:  # Unix
                    subprocess.run(f"cp {filepath} {dest_path}", shell=True)
            except Exception as e:
                print(f"[备份失败] {str(e)}")
            
    def run_health_check(self):
        """系统健康检查"""
        checks = [
            ("编码检查", "bash .encoding-check.sh" if os.name != 'nt' else 
             f"python -c \"import os, locale; print('=== 系统编码检测 ===\\n控制台编码:', os.getenv('PYTHONIOENCODING', 'utf-8'), '\\n系统区域设置:', locale.getlocale())\""),
            ("知识库验证", "python .knowledge-mgr.py --validate"),
            ("权限审计", "python modules/permission_manager.py --audit")
        ]
        
        for name, cmd in checks:
            for attempt in range(self.config.max_retries):
                result = subprocess.run(cmd, shell=True)
                if result.returncode == 0:
                    break
                elif self.config.auto_fix:
                    self.attempt_repair(name, cmd)
                    
    def attempt_repair(self, issue_name, cmd):
        """尝试自动修复"""
        print(f"尝试修复 {issue_name}...")
        fix_cmd = {
            "编码检查": "python .encoding-check.sh --repair",
            "知识库验证": "python .knowledge-mgr.py --rebuild-index",
            "权限审计": "python modules/permission_manager.py --repair"
        }.get(issue_name, None)
        
        if fix_cmd:
            subprocess.run(fix_cmd, shell=True)
            
    def start(self):
        """启动自治代理"""
        observer = Observer()
        observer.schedule(self, ".", recursive=True)
        observer.start()
        
        try:
            while True:
                current_time = time.time()
                # 执行健康检查
                if current_time - self.last_health_check > self.config.health_check_interval:
                    self.run_health_check()
                    self.last_health_check = current_time
                
                # 执行存储管理检查（每小时一次）
                if current_time - getattr(self, 'last_storage_check', 0) > 3600:
                    disk_usage = self.storage_manager.check_disk_usage()
                    print(f"存储状态: 已用 {disk_usage['used_gb']}GB / 总共 {disk_usage['total_gb']}GB")
                    
                    if disk_usage["used_gb"] > self.config.storage_max_size:
                        print("存储空间超过阈值，开始清理旧备份...")
                        self.storage_manager.cleanup_old_backups()
                    
                    self.last_storage_check = current_time
                
                time.sleep(60)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

if __name__ == "__main__":
    print("AI自治代理启动...")
    autopilot = AIAutopilot()
    autopilot.start()