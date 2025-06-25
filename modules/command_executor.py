import subprocess
from typing import Tuple
from .security_policy import LeastPrivilegeEnforcer, PermissionRequest

class SecureCommandExecutor:
    def __init__(self):
        self.enforcer = LeastPrivilegeEnforcer()
        self.emergency_mode = False

    def execute(self, command: str, 
               operation_type: str,
               scope_constraint: str = None) -> Tuple[bool, str]:
        """
        安全命令执行流程：
        1. 构建权限请求
        2. 验证并获取最小权限方案
        3. 执行安全命令
        """
        if self.emergency_mode:
            return self._raw_execute(command)
            
        # 构建权限请求
        request = PermissionRequest(
            operation=operation_type,
            required_perms=self._detect_required_perms(command),
            minimal_alternative=None,
            scope_constraint=scope_constraint
        )
        
        # 生成并验证最小权限方案
        request.minimal_alternative = self.enforcer.generate_alternative(command)
        is_valid, msg = self.enforcer.validate_operation(request)
        
        if not is_valid:
            return False, f"安全审查失败: {msg}"
            
        return self._raw_execute(request.minimal_alternative)

    def _raw_execute(self, command: str) -> Tuple[bool, str]:
        """原始命令执行（内部使用）"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr

    @staticmethod
    def _detect_required_perms(command: str) -> List[str]:
        """自动检测所需权限"""
        perms = []
        if 'chmod' in command:
            perms.append("文件权限修改")
        if 'curl' in command or 'wget' in command:
            perms.append("网络访问")
        if 'docker' in command:
            perms.append("容器管理")
        return perms or ["基础执行权限"]

if __name__ == "__main__":
    executor = SecureCommandExecutor()
    
    # 测试安全执行
    print("== 安全执行测试 ==")
    success, output = executor.execute(
        command="rm -rf /tmp/*",
        operation_type="file_ops:delete",
        scope_constraint="/tmp"
    )
    print(f"结果: {success}, 输出: {output}")
    
    # 测试紧急模式
    print("\n== 紧急模式测试 ==")
    executor.emergency_mode = True
    success, output = executor.execute(
        command="chmod 777 config.ini",
        operation_type="file_ops:modify"
    )
    print(f"结果: {success}, 输出: {output}")