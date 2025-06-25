"""
权限管理模块 - 负责系统权限的分配和验证

主要功能：
1. 管理用户角色和权限
2. 验证操作权限
3. 支持权限动态调整
4. 权限缓存优化

注意：从原security_policy.py拆分而来，版本1.0.0
"""

class PermissionManager:
    def __init__(self, role_config, audit_logger=None):
        """初始化权限管理器
        参数:
            role_config: 角色权限配置
            audit_logger: 审计日志器实例
        """
        self.roles = role_config
        self.permission_cache = {}
        self.audit_logger = audit_logger
    
    def check_permission(self, user_role, action):
        """检查用户是否有执行操作的权限"""
        # 检查缓存
        cache_key = f"{user_role}:{action}"
        if cache_key in self.permission_cache:
            return self.permission_cache[cache_key]
            
        # 检查角色权限
        has_permission = False
        if user_role in self.roles:
            has_permission = action in self.roles[user_role]
            
        # 更新缓存
        self.permission_cache[cache_key] = has_permission
        
        # 记录审计日志
        if self.audit_logger:
            self.audit_logger.log_operation(
                operation=f"permission_check:{action}",
                user=user_role,
                status="allowed" if has_permission else "denied",
                action=action,
                cached=False
            )
            
        return has_permission
    
    def update_role_permission(self, role, permissions):
        """动态更新角色权限"""
        # 获取当前权限配置
        old_permissions = self.roles.get(role, set())
        
        # 验证新权限配置
        if not isinstance(permissions, (set, list)):
            raise ValueError("权限配置必须是set或list类型")
            
        # 转换为set确保唯一性
        new_permissions = set(permissions)
        
        # 记录变更差异
        added = new_permissions - old_permissions
        removed = old_permissions - new_permissions
        
        # 执行权限更新
        self.roles[role] = new_permissions
        
        # 清除相关缓存
        self._clear_role_cache(role)
        
        # 记录审计日志
        if self.audit_logger:
            self.audit_logger.log_operation(
                operation="permission_update",
                user="system_admin",  # 实际应用中应从上下文中获取
                status="success",
                role=role,
                added=list(added),
                removed=list(removed),
                total_count=len(new_permissions)
            )
            
        return {
            "role": role,
            "added": list(added),
            "removed": list(removed),
            "total": len(new_permissions)
        }

    def _clear_role_cache(self, role):
        """清除指定角色的权限缓存"""
        keys_to_remove = [k for k in self.permission_cache if k.startswith(f"{role}:")]
        for key in keys_to_remove:
            del self.permission_cache[key]