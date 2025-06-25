from fastapi import APIRouter, Depends
from .security_policy import LeastPrivilegeEnforcer
from .command_executor import SecureCommandExecutor
from typing import List

security_router = APIRouter()
enforcer = LeastPrivilegeEnforcer()
executor = SecureCommandExecutor()

@security_router.get("/security/audit-logs")
async def get_audit_logs(limit: int = 100):
    """获取安全审计日志"""
    return enforcer.audit_log[-limit:]

@security_router.post("/security/execute")
async def secure_execute(
    command: str, 
    operation_type: str,
    scope: str = None
):
    """安全命令执行端点"""
    success, output = executor.execute(
        command=command,
        operation_type=operation_type,
        scope_constraint=scope
    )
    return {
        "approved": success,
        "output": output,
        "original_command": command,
        "executed_command": executor.last_actual_command if success else None
    }

@security_router.post("/security/emergency-mode")
async def set_emergency_mode(enable: bool, auth: str):
    """紧急模式开关（需管理员权限）"""
    if auth != "ADMIN_TOKEN":
        return {"error": "Unauthorized"}
    
    executor.emergency_mode = enable
    return {"status": "Emergency mode " + ("enabled" if enable else "disabled")}

# 在原有FastAPI应用中添加路由
app.include_router(security_router, prefix="/api/v2")

# 添加安全中间件
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response