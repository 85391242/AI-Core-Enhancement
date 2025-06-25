# 变更日志

## [1.1.0] - 2023-11-20

### 新增
- 新增policy_enforcer模块：负责安全策略执行
- 新增permission_manager模块：实现权限管理功能
- 新增audit_logger模块：处理审计日志记录

### 变更
- security_policy.py标记为废弃(DeprecationWarning)
- 添加模块间依赖关系说明

### 迁移说明
1. 导入新模块替代原security_policy
2. 测试各模块基础功能
3. 逐步迁移业务调用代码

## [1.0.0] - 2023-11-15
- 初始版本发布