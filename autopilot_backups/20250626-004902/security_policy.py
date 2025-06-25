"""
[已废弃] 安全策略模块 - 该模块已拆分为三个独立模块

注意：此文件已废弃，将在v2.0.0中移除
新模块结构：
1. policy_enforcer.py - 策略执行和模式验证
2. permission_manager.py - 权限验证和管理
3. audit_logger.py - 审计日志记录

迁移指南：
1. 导入新模块替代本模块
2. 功能对应关系：
   - 安全模式检查 → PolicyEnforcer
   - 权限验证 → PermissionManager
   - 审计日志 → AuditLogger
3. 测试迁移后的功能

示例替换：
原: from .security_policy import LeastPrivilegeEnforcer
新: from .policy_enforcer import PolicyEnforcer
     from .permission_manager import PermissionManager
     from .audit_logger import AuditLogger
"""
import warnings
warnings.warn(
    "security_policy.py is deprecated and will be removed in v2.0.0. "
    "Use the new modularized components instead.",
    DeprecationWarning,
    stacklevel=2
)

import re
from typing import List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class PermissionRequest:
    operation: str
    required_perms: List[str]
    minimal_alternative: Optional[str] = None
    scope_constraint: Optional[str] = None

class LeastPrivilegeEnforcer:
    # 安全操作正则规则库
    SAFETY_PATTERNS = {
        'file_ops': r'^(chmod\s[0-7][0-5][0-5]|'
                   r'chown\s[\w-]+:[\w-]+\s|'
                   r'mv\s[^\*]+\s[^\*]+)$',
        'network': r'^(curl\s-H\s[^\|]+\s|'
                  r'wget\s--header=[^\|]+\s)',
        'process': r'^(docker\sexec\s-it\s\w+\s|'
                  r'kill\s-[1-9]|1[0-5]\s\d+)$'
    }

    def __init__(self):
        self.audit_log = []

    def validate_operation(self, request: PermissionRequest) -> Tuple[bool, str]:
        """执行三级权限验证"""
        # 第一级：权限需求声明
        if not request.required_perms:
            return False, "必须声明所需权限"

        # 第二级：最小化验证
        if request.minimal_alternative:
            pattern = self._get_safety_pattern(request.operation)
            if not re.match(pattern, request.minimal_alternative):
                return False, "替代方案不符合安全规范"

        # 第三级：范围限定
        if request.scope_constraint:
            if not self._check_scope(request.operation, request.scope_constraint):
                return False, "操作超出限定范围"

        self.audit_log.append(request)
        return True, "验证通过"

    def _get_safety_pattern(self, operation_type: str) -> str:
        """获取对应操作类型的安全正则"""
        for op_type, pattern in self.SAFETY_PATTERNS.items():
            if operation_type.startswith(op_type):
                return pattern
        return r'^((?!sudo|rm\s-rf|chmod\s[0-9][0-9][0-9][0-9]).)*$'

    def _check_scope(self, operation: str, constraint: str) -> bool:
        """检查操作范围约束"""
        if 'file' in operation.lower():
            return constraint in operation
        return True

    @staticmethod
    def generate_alternative(command: str) -> str:
        """生成最小权限替代方案"""
        replacements = {
            'rm -rf': 'find . -type f -delete',
            'chmod 777': 'chmod 755',
            'docker run --privileged': 'docker run --cap-add=NET_ADMIN'
        }
        for risky, safe in replacements.items():
            command = command.replace(risky, safe)
        return command

if __name__ == "__main__":
    # 示例用法
    enforcer = LeastPrivilegeEnforcer()
    
    sample_request = PermissionRequest(
        operation="file_ops:delete",
        required_perms=["当前目录写权限"],
        minimal_alternative="find ./target -type f -delete",
        scope_constraint="./target"
    )

    is_valid, msg = enforcer.validate_operation(sample_request)
    print(f"验证结果: {is_valid}, 信息: {msg}")