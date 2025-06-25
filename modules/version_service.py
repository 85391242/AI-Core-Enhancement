import hashlib
import difflib
import shutil
import logging
from datetime import datetime
from pathlib import Path
import json
from typing import Dict, List, Optional, Tuple, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("version_service.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("VersionService")

class VersionError(Exception):
    """版本控制相关错误的基类"""
    pass

class VersionNotFoundError(VersionError):
    """指定版本不存在时抛出"""
    pass

class VersionIntegrityError(VersionError):
    """版本完整性验证失败时抛出"""
    pass

class StandardVersionControl:
    """
    标准版本控制系统
    
    负责管理AI核心行为准则的版本控制，包括创建、激活、验证、回滚和比较版本。
    """
    VERSION_FILE = "standards_versions.json"
    BACKUP_DIR = "version_backups"
    
    def __init__(self, repo_path="."):
        """
        初始化版本控制系统
        
        参数:
            repo_path (str): 仓库路径，默认为当前目录
        """
        self.repo = Path(repo_path)
        self.backup_dir = self.repo / self.BACKUP_DIR
        self.backup_dir.mkdir(exist_ok=True)
        self.versions = self._load_versions()
        logger.info(f"版本控制系统初始化完成，已加载 {len(self.versions['versions'])} 个版本")
        
    def _load_versions(self) -> Dict:
        """
        加载版本信息
        
        返回:
            Dict: 包含所有版本信息的字典
        """
        version_file = self.repo / self.VERSION_FILE
        if version_file.exists():
            try:
                with open(version_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"版本文件解析错误: {e}")
                # 创建备份并返回空版本列表
                self._backup_corrupt_file(version_file)
                return {"versions": [], "history": []}
        return {"versions": [], "history": []}
    
    def _backup_corrupt_file(self, file_path: Path) -> None:
        """
        备份损坏的文件
        
        参数:
            file_path (Path): 文件路径
        """
        backup_name = f"{file_path.name}.{datetime.now().strftime('%Y%m%d%H%M%S')}.bak"
        backup_path = self.backup_dir / backup_name
        shutil.copy2(file_path, backup_path)
        logger.warning(f"已创建损坏文件备份: {backup_path}")
    
    def create_version(self, standard_path: str, description: str, version_type: str = "minor") -> Dict:
        """
        创建新准则版本
        
        参数:
            standard_path (str): 标准文件路径
            description (str): 版本描述
            version_type (str): 版本类型，可选值为 "major"、"minor" 或 "patch"
            
        返回:
            Dict: 新创建的版本信息
            
        异常:
            FileNotFoundError: 标准文件不存在时抛出
        """
        file_path = self.repo / standard_path
        if not file_path.exists():
            error_msg = f"标准文件不存在: {standard_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
            
        # 计算文件哈希值
        with open(file_path, 'rb') as f:
            content_hash = hashlib.sha256(f.read()).hexdigest()
        
        # 生成版本号
        last_version = self._get_latest_version()
        if last_version:
            version_id = self._increment_version(last_version["version_id"], version_type)
        else:
            version_id = "v1.0.0"
            
        # 创建版本信息
        new_version = {
            "version_id": version_id,
            "timestamp": datetime.now().isoformat(),
            "file": standard_path,
            "hash": content_hash,
            "description": description,
            "active": False,
            "stable": False,
            "compatibility": ["v1.0.0"]  # 默认与基础版本兼容
        }
        
        # 添加版本并保存
        self.versions['versions'].append(new_version)
        
        # 记录历史
        history_entry = {
            "action": "create",
            "version_id": version_id,
            "timestamp": datetime.now().isoformat(),
            "user": self._get_current_user()
        }
        self._add_history(history_entry)
        
        self._save_versions()
        self._backup_version(standard_path, version_id)
        
        logger.info(f"已创建新版本: {version_id}")
        return new_version
    
    def _get_current_user(self) -> str:
        """
        获取当前用户名
        
        返回:
            str: 当前用户名
        """
        import os
        try:
            return os.getlogin()
        except:
            return "unknown"
    
    def _get_latest_version(self) -> Optional[Dict]:
        """
        获取最新版本
        
        返回:
            Optional[Dict]: 最新版本信息，如果没有版本则返回None
        """
        if not self.versions['versions']:
            return None
        return sorted(
            self.versions['versions'], 
            key=lambda v: [int(x) for x in v['version_id'].lstrip('v').split('.')],
            reverse=True
        )[0]
    
    def _increment_version(self, version: str, version_type: str) -> str:
        """
        递增版本号
        
        参数:
            version (str): 当前版本号，格式为 "vX.Y.Z"
            version_type (str): 版本类型，可选值为 "major"、"minor" 或 "patch"
            
        返回:
            str: 新版本号
        """
        # 移除前缀 "v"
        version = version.lstrip('v')
        parts = [int(x) for x in version.split('.')]
        
        # 确保版本号有三部分
        while len(parts) < 3:
            parts.append(0)
            
        major, minor, patch = parts[:3]
        
        if version_type == "major":
            return f"v{major + 1}.0.0"
        elif version_type == "minor":
            return f"v{major}.{minor + 1}.0"
        else:  # patch
            return f"v{major}.{minor}.{patch + 1}"
    
    def activate_version(self, version_id: str) -> None:
        """
        激活指定版本
        
        参数:
            version_id (str): 版本ID
            
        异常:
            VersionNotFoundError: 指定版本不存在时抛出
            VersionIntegrityError: 版本完整性验证失败时抛出
        """
        # 验证版本是否存在
        version = self._find_version(version_id)
        if not version:
            error_msg = f"版本不存在: {version_id}"
            logger.error(error_msg)
            raise VersionNotFoundError(error_msg)
        
        # 验证版本完整性
        if not self._verify_version_integrity(version):
            error_msg = f"版本完整性验证失败: {version_id}"
            logger.error(error_msg)
            raise VersionIntegrityError(error_msg)
        
        # 更新激活状态
        for v in self.versions['versions']:
            v['active'] = (v['version_id'] == version_id)
        
        # 记录历史
        history_entry = {
            "action": "activate",
            "version_id": version_id,
            "timestamp": datetime.now().isoformat(),
            "user": self._get_current_user()
        }
        self._add_history(history_entry)
        
        self._save_versions()
        logger.info(f"已激活版本: {version_id}")
    
    def _find_version(self, version_id: str) -> Optional[Dict]:
        """
        查找指定版本
        
        参数:
            version_id (str): 版本ID
            
        返回:
            Optional[Dict]: 版本信息，如果不存在则返回None
        """
        for version in self.versions['versions']:
            if version['version_id'] == version_id:
                return version
        return None
    
    def _verify_version_integrity(self, version: Dict) -> bool:
        """
        验证版本完整性
        
        参数:
            version (Dict): 版本信息
            
        返回:
            bool: 是否通过验证
        """
        file_path = self.repo / version['file']
        if not file_path.exists():
            logger.warning(f"版本文件不存在: {version['file']}")
            return False
            
        with open(file_path, 'rb') as f:
            current_hash = hashlib.sha256(f.read()).hexdigest()
            
        if current_hash != version['hash']:
            logger.warning(f"版本哈希值不匹配: {version['version_id']}")
            return False
            
        return True
    
    def _save_versions(self) -> None:
        """保存版本信息到文件"""
        try:
            with open(self.repo / self.VERSION_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.versions, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存版本信息失败: {e}")
    
    def _add_history(self, entry: Dict) -> None:
        """
        添加历史记录
        
        参数:
            entry (Dict): 历史记录条目
        """
        if 'history' not in self.versions:
            self.versions['history'] = []
        self.versions['history'].append(entry)
    
    def get_active_version(self) -> Optional[Dict]:
        """
        获取当前激活版本
        
        返回:
            Optional[Dict]: 当前激活版本信息，如果没有激活版本则返回None
        """
        for version in self.versions['versions']:
            if version.get('active'):
                return version
        return None
    
    def mark_as_stable(self, version_id: str) -> None:
        """
        将指定版本标记为稳定版本
        
        参数:
            version_id (str): 版本ID
            
        异常:
            VersionNotFoundError: 指定版本不存在时抛出
        """
        version = self._find_version(version_id)
        if not version:
            error_msg = f"版本不存在: {version_id}"
            logger.error(error_msg)
            raise VersionNotFoundError(error_msg)
        
        version['stable'] = True
        
        # 记录历史
        history_entry = {
            "action": "mark_stable",
            "version_id": version_id,
            "timestamp": datetime.now().isoformat(),
            "user": self._get_current_user()
        }
        self._add_history(history_entry)
        
        self._save_versions()
        logger.info(f"已将版本 {version_id} 标记为稳定版本")
    
    def get_stable_versions(self) -> List[Dict]:
        """
        获取所有稳定版本
        
        返回:
            List[Dict]: 稳定版本列表
        """
        return [v for v in self.versions['versions'] if v.get('stable')]
    
    def rollback_to_version(self, version_id: str) -> None:
        """
        回滚到指定版本
        
        参数:
            version_id (str): 版本ID
            
        异常:
            VersionNotFoundError: 指定版本不存在时抛出
            VersionIntegrityError: 版本完整性验证失败时抛出
        """
        # 验证版本是否存在
        version = self._find_version(version_id)
        if not version:
            error_msg = f"版本不存在: {version_id}"
            logger.error(error_msg)
            raise VersionNotFoundError(error_msg)
        
        # 验证版本完整性
        if not self._verify_version_integrity(version):
            # 尝试从备份恢复
            if self._restore_from_backup(version_id):
                logger.info(f"已从备份恢复版本: {version_id}")
            else:
                error_msg = f"版本完整性验证失败且无法从备份恢复: {version_id}"
                logger.error(error_msg)
                raise VersionIntegrityError(error_msg)
        
        # 激活指定版本
        self.activate_version(version_id)
        
        # 记录历史
        history_entry = {
            "action": "rollback",
            "version_id": version_id,
            "timestamp": datetime.now().isoformat(),
            "user": self._get_current_user()
        }
        self._add_history(history_entry)
        
        logger.info(f"已回滚到版本: {version_id}")
    
    def rollback_to_last_stable(self) -> Optional[str]:
        """
        回滚到最后一个稳定版本
        
        返回:
            Optional[str]: 回滚到的版本ID，如果没有稳定版本则返回None
        """
        stable_versions = self.get_stable_versions()
        if not stable_versions:
            logger.warning("没有找到稳定版本，无法回滚")
            return None
        
        # 按版本号排序，获取最新的稳定版本
        latest_stable = sorted(
            stable_versions,
            key=lambda v: [int(x) for x in v['version_id'].lstrip('v').split('.')],
            reverse=True
        )[0]
        
        self.rollback_to_version(latest_stable['version_id'])
        return latest_stable['version_id']
    
    def _backup_version(self, file_path: str, version_id: str) -> None:
        """
        备份指定版本的文件
        
        参数:
            file_path (str): 文件路径
            version_id (str): 版本ID
        """
        source_path = self.repo / file_path
        if not source_path.exists():
            logger.warning(f"无法备份不存在的文件: {file_path}")
            return
            
        backup_name = f"{source_path.name}.{version_id}"
        backup_path = self.backup_dir / backup_name
        
        try:
            shutil.copy2(source_path, backup_path)
            logger.info(f"已创建版本备份: {backup_path}")
        except Exception as e:
            logger.error(f"创建版本备份失败: {e}")
    
    def _restore_from_backup(self, version_id: str) -> bool:
        """
        从备份恢复指定版本
        
        参数:
            version_id (str): 版本ID
            
        返回:
            bool: 是否成功恢复
        """
        version = self._find_version(version_id)
        if not version:
            logger.error(f"版本不存在，无法恢复: {version_id}")
            return False
            
        file_path = version['file']
        backup_name = f"{Path(file_path).name}.{version_id}"
        backup_path = self.backup_dir / backup_name
        
        if not backup_path.exists():
            logger.error(f"备份文件不存在: {backup_path}")
            return False
            
        try:
            target_path = self.repo / file_path
            shutil.copy2(backup_path, target_path)
            logger.info(f"已从备份恢复文件: {file_path}")
            return True
        except Exception as e:
            logger.error(f"从备份恢复失败: {e}")
            return False
    
    def compare_versions(self, version_id1: str, version_id2: str) -> Dict:
        """
        比较两个版本的差异
        
        参数:
            version_id1 (str): 第一个版本ID
            version_id2 (str): 第二个版本ID
            
        返回:
            Dict: 包含差异信息的字典
            
        异常:
            VersionNotFoundError: 指定版本不存在时抛出
        """
        version1 = self._find_version(version_id1)
        version2 = self._find_version(version_id2)
        
        if not version1:
            error_msg = f"版本不存在: {version_id1}"
            logger.error(error_msg)
            raise VersionNotFoundError(error_msg)
            
        if not version2:
            error_msg = f"版本不存在: {version_id2}"
            logger.error(error_msg)
            raise VersionNotFoundError(error_msg)
            
        file_path1 = self.repo / version1['file']
        file_path2 = self.repo / version2['file']
        
        if not file_path1.exists() or not file_path2.exists():
            # 尝试从备份恢复
            if not file_path1.exists():
                self._restore_from_backup(version_id1)
            if not file_path2.exists():
                self._restore_from_backup(version_id2)
                
            # 再次检查
            if not file_path1.exists() or not file_path2.exists():
                error_msg = "无法比较版本，文件不存在且无法从备份恢复"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
        
        # 读取文件内容
        with open(file_path1, 'r', encoding='utf-8') as f1:
            content1 = f1.readlines()
            
        with open(file_path2, 'r', encoding='utf-8') as f2:
            content2 = f2.readlines()
            
        # 计算差异
        diff = list(difflib.unified_diff(
            content1, 
            content2, 
            fromfile=f"版本 {version_id1}", 
            tofile=f"版本 {version_id2}",
            n=3
        ))
        
        # 计算相似度
        matcher = difflib.SequenceMatcher(None, ''.join(content1), ''.join(content2))
        similarity = matcher.ratio() * 100
        
        # 统计变更
        additions = len([line for line in diff if line.startswith('+')])
        deletions = len([line for line in diff if line.startswith('-')])
        
        result = {
            "version1": version_id1,
            "version2": version_id2,
            "similarity": similarity,
            "additions": additions,
            "deletions": deletions,
            "diff": ''.join(diff)
        }
        
        logger.info(f"已比较版本 {version_id1} 和 {version_id2}，相似度: {similarity:.2f}%")
        return result
    
    def generate_changelog(self, from_version: Optional[str] = None, to_version: Optional[str] = None) -> str:
        """
        生成版本变更日志
        
        参数:
            from_version (Optional[str]): 起始版本ID，如果为None则从第一个版本开始
            to_version (Optional[str]): 结束版本ID，如果为None则到最新版本
            
        返回:
            str: 变更日志
        """
        versions = sorted(
            self.versions['versions'],
            key=lambda v: [int(x) for x in v['version_id'].lstrip('v').split('.')]
        )
        
        if not versions:
            return "没有可用的版本记录"
            
        # 确定起始和结束版本
        start_idx = 0
        end_idx = len(versions) - 1
        
        if from_version:
            for i, v in enumerate(versions):
                if v['version_id'] == from_version:
                    start_idx = i
                    break
                    
        if to_version:
            for i, v in enumerate(versions):
                if v['version_id'] == to_version:
                    end_idx = i
                    break
        
        # 生成变更日志
        changelog = []
        changelog.append(f"# 变更日志 ({versions[start_idx]['version_id']} 到 {versions[end_idx]['version_id']})\n")
        
        for i in range(start_idx, end_idx + 1):
            v = versions[i]
            timestamp = datetime.fromisoformat(v['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            stability = "稳定版" if v.get('stable') else "开发版"
            active = "当前激活" if v.get('active') else ""
            
            changelog.append(f"## {v['version_id']} ({timestamp}) [{stability}] {active}\n")
            changelog.append(f"{v['description']}\n")
            
            # 如果不是第一个版本，添加与前一个版本的差异
            if i > 0 and i > start_idx:
                prev_v = versions[i-1]
                try:
                    diff = self.compare_versions(prev_v['version_id'], v['version_id'])
                    changelog.append(f"- 相似度: {diff['similarity']:.2f}%\n")
                    changelog.append(f"- 添加: {diff['additions']} 行\n")
                    changelog.append(f"- 删除: {diff['deletions']} 行\n")
                except Exception as e:
                    changelog.append(f"- 无法计算差异: {str(e)}\n")
            
            changelog.append("\n")
            
        return ''.join(changelog)


def main():
    """
    版本控制系统的示例用法
    """
    try:
        # 初始化版本控制系统
        vc = StandardVersionControl()
        logger.info("版本控制系统初始化完成")
        
        # 创建初始版本
        initial_version = vc.create_version(
            "core_standards.md",
            "初始版本：基础AI行为准则框架",
            "major"
        )
        logger.info(f"创建初始版本：{initial_version['version_id']}")
        
        # 激活初始版本
        vc.activate_version(initial_version['version_id'])
        logger.info(f"激活初始版本：{initial_version['version_id']}")
        
        # 标记为稳定版本
        vc.mark_as_stable(initial_version['version_id'])
        logger.info(f"将版本 {initial_version['version_id']} 标记为稳定版本")
        
        # 创建次要版本
        minor_version = vc.create_version(
            "core_standards.md",
            "更新：添加错误处理和用户交互准则",
            "minor"
        )
        logger.info(f"创建次要版本：{minor_version['version_id']}")
        
        # 比较版本差异
        diff = vc.compare_versions(
            initial_version['version_id'],
            minor_version['version_id']
        )
        logger.info(f"版本差异：\n{diff['diff']}")
        
        # 生成变更日志
        changelog = vc.generate_changelog()
        logger.info(f"变更日志：\n{changelog}")
        
    except Exception as e:
        logger.error(f"版本控制操作失败：{e}")
        raise


if __name__ == "__main__":
    main()