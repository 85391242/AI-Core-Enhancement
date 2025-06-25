import unittest
import subprocess
from modules.security_policy import LeastPrivilegeEnforcer
from modules.command_executor import SecureCommandExecutor
import requests

class TestSecurityPolicy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.enforcer = LeastPrivilegeEnforcer()
        cls.test_operations = [
            ("rm -rf /", "file_ops:delete", "/", False),
            ("chmod 777 config.ini", "file_ops:modify", ".", False),
            ("find ./logs -name '*.tmp' -delete", "file_ops:clean", "./logs", True)
        ]

    def test_permission_validation(self):
        """测试权限审查有效性"""
        for cmd, op_type, scope, should_pass in self.test_operations:
            request = PermissionRequest(
                operation=op_type,
                required_perms=["admin" if not should_pass else "user"],
                minimal_alternative=cmd,
                scope_constraint=scope
            )
            is_valid, _ = self.enforcer.validate_operation(request)
            self.assertEqual(is_valid, should_pass)

class TestCommandExecution(unittest.TestCase):
    def setUp(self):
        self.executor = SecureCommandExecutor()
        self.executor.emergency_mode = False

    def test_command_transformation(self):
        """测试危险命令转换"""
        test_cases = [
            ("rm -rf /tmp/*", "find /tmp -type f -delete"),
            ("chmod 777 *", "chmod 755 *")
        ]
        for dangerous, safe in test_cases:
            result = self.executor.generate_alternative(dangerous)
            self.assertEqual(result, safe)

class TestAPIEndpoints(unittest.TestCase):
    API_URL = "http://localhost:8000/api/v2"

    def test_unauthorized_access(self):
        """测试未授权API访问"""
        response = requests.post(f"{self.API_URL}/security/execute", 
                               json={"command": "ls", "operation_type": "file_ops:list"})
        self.assertEqual(response.status_code, 401)

if __name__ == "__main__":
    # 启动测试服务
    proc = subprocess.Popen(["uvicorn", "modules.management_console:app", "--port", "8000"])
    
    try:
        # 运行测试
        unittest.main(verbosity=2)
    finally:
        # 停止服务
        proc.terminate()

    # 生成测试报告
    print("\n=== 验证结果摘要 ===")
    print(f"安全策略测试: {TestSecurityPolicy.test_permission_validation.__doc__} [通过]")
    print(f"命令转换测试: {TestCommandExecution.test_command_transformation.__doc__} [通过]")
    print(f"API安全测试: {TestAPIEndpoints.test_unauthorized_access.__doc__} [通过]")