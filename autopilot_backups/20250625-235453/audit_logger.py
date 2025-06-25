"""
审计日志模块 - 负责系统安全事件的记录和监控

主要功能：
1. 记录安全相关操作
2. 生成结构化审计日志
3. 提供实时告警功能
4. 生成操作指纹

注意：从原security_policy.py拆分而来，版本1.0.0
"""

import hashlib
import json
from datetime import datetime

class AuditLogger:
    def __init__(self, log_file='security_audit.log'):
        """初始化审计日志器"""
        self.log_file = log_file
        self.alert_rules = []
    
    def log_operation(self, operation, user, status, **kwargs):
        """记录操作日志
        参数:
            operation: 操作类型 (如: file_ops:delete)
            user: 执行用户
            status: 操作状态 (success/failed)
            **kwargs: 额外日志字段
        """
        # 敏感信息脱敏
        sanitized_op = self._sanitize_operation(operation)
        
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'operation': sanitized_op,
            'user': self._mask_sensitive(user),
            'status': status,
            'fingerprint': self._generate_fingerprint(operation, user),
            **{k: self._mask_sensitive(v) for k, v in kwargs.items()}
        }
        
        # 写入结构化日志
        with open(self.log_file, 'a') as f:
            json.dump(log_entry, f, ensure_ascii=False)
            f.write('\n')
            
        # 触发告警检查
        self._check_alerts(log_entry)
        
    def _generate_fingerprint(self, operation, user):
        """生成操作指纹"""
        data = f"{operation}-{user}-{datetime.utcnow().timestamp()}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def add_alert_rule(self, rule):
        """添加告警规则"""
        self.alert_rules.append(rule)
        
    def _mask_sensitive(self, value):
        """敏感信息脱敏处理"""
        if not value or not isinstance(value, str):
            return value
            
        # 邮箱脱敏: user@domain.com -> u***@domain.com
        if '@' in value and '.' in value:
            parts = value.split('@')
            return f"{parts[0][0]}***@{parts[1]}"
            
        # 密码/密钥脱敏: password=secret -> password=***
        if 'password=' in value.lower() or 'secret=' in value.lower():
            return re.sub(r'(password|secret)=[^&\s]+', r'\1=***', value, flags=re.I)
            
        # 长密钥脱敏: ABC123XYZ456 -> ABC1...Y456
        if len(value) > 16 and any(c.isupper() for c in value) and any(c.isdigit() for c in value):
            return f"{value[:4]}...{value[-4:]}"
            
        return value

    def _sanitize_operation(self, operation):
        """清洗操作字符串中的敏感路径"""
        import re
        return re.sub(r'(/home/|/root/|/etc/)\w+', r'\1***', operation)

    def _check_alerts(self, log_entry):
        """检查日志条目是否触发告警规则"""
        critical_ops = ['sudo', 'chmod', 'rm', 'docker exec']
        if any(op in log_entry['operation'] for op in critical_ops) and log_entry['status'] == 'failed':
            self._trigger_alert(log_entry)

    def _trigger_alert(self, log_entry):
        """触发告警通知"""
        alert_msg = f"安全告警: 关键操作失败 - {log_entry['operation']}"
        print(f"[SECURITY ALERT] {alert_msg}")
        # TODO: 实现邮件/短信告警集成