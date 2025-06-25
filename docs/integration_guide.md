# 智能权限管理系统集成指南

## 系统概述
本系统提供完整的权限管理和审计日志功能，主要特性包括：
- 基于角色的权限控制
- 详细操作审计日志
- 自动化配置管理
- 智能缓存管理

## 快速开始

1. 初始化系统
```python
from modules.audit_logger import AuditLogger
from modules.permission_manager import PermissionManager

# 使用默认配置
audit_logger = AuditLogger()
permission_manager = PermissionManager(audit_logger=audit_logger)

# 或使用自定义配置
audit_logger = AuditLogger({
    "log_file": "custom_audit.log",
    "max_size_mb": 20
})
```

2. 权限检查
```python
if permission_manager.check_permission("user", "edit_content"):
    print("有权限")
else:
    print("无权限")
```

## 配置说明

### 审计日志配置
编辑 `config/audit_config.yaml`：
```yaml
log_file: "security_audit.log"
max_size_mb: 10
backup_count: 5
alert_rules:
  - pattern: ".*敏感操作.*"
    level: "high"
```

### 权限配置
编辑 `config/permission_config.yaml`：
```yaml
role_config:
  admin:
    - "all_permissions"
cache_ttl: 3600
```

## 自动化管理
系统自动处理：
- 日志轮转
- 缓存刷新
- 配置热加载

手动触发管理：
```python
audit_logger.auto_manage()
permission_manager.auto_manage()
```

## 最佳实践
1. 生产环境建议：
   - 设置更严格的告警规则
   - 缩短自动刷新间隔(300秒)
   - 使用加密日志存储

2. 开发建议：
   - 开启详细日志模式
   - 使用内存缓存加速测试
```