#!/usr/bin/env python3
# 知识库管理系统 v1.0
import os
import hashlib
import json
from datetime import datetime

KNOWLEDGE_DIR = "knowledge_base"
BACKUP_DIR = "backups"

class KnowledgeManager:
    def __init__(self):
        os.makedirs(KNOWLEDGE_DIR, exist_ok=True)
        os.makedirs(BACKUP_DIR, exist_ok=True)
        
    def add_solution(self, problem, solution):
        """添加问题解决方案"""
        problem_hash = hashlib.md5(problem.encode()).hexdigest()
        solution_file = f"{KNOWLEDGE_DIR}/{problem_hash}.json"
        
        data = {
            "problem": problem,
            "solution": solution,
            "timestamp": datetime.now().isoformat(),
            "verified": False
        }
        
        with open(solution_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
    def find_solution(self, problem):
        """查找已有解决方案"""
        problem_hash = hashlib.md5(problem.encode()).hexdigest()
        solution_file = f"{KNOWLEDGE_DIR}/{problem_hash}.json"
        
        if os.path.exists(solution_file):
            with open(solution_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def smart_backup(self, files):
        """智能备份"""
        backup_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{BACKUP_DIR}/{backup_id}"
        os.makedirs(backup_path)
        
        for file in files:
            if os.path.exists(file):
                os.link(file, f"{backup_path}/{os.path.basename(file)}")
                
    def safe_clean(self, days=30):
        """安全清理旧备份"""
        now = datetime.now()
        for backup in os.listdir(BACKUP_DIR):
            backup_date = datetime.strptime(backup[:8], "%Y%m%d")
            if (now - backup_date).days > days:
                backup_path = f"{BACKUP_DIR}/{backup}"
                try:
                    for root, _, files in os.walk(backup_path):
                        for file in files:
                            os.chmod(os.path.join(root, file), 0o777)
                    os.system(f'rmdir /S /Q "{backup_path}"')
                except Exception as e:
                    print(f"清理失败 {backup_path}: {str(e)}")

if __name__ == "__main__":
    km = KnowledgeManager()
    # 示例：添加终端乱码解决方案
    km.add_solution(
        "终端显示乱码问题",
        {"solution": "统一使用UTF-8编码", "command": "chcp 65001"}
    )