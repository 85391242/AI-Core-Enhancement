#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import platform
import locale
import datetime
import json
import socket
import requests
from typing import Dict, Optional

class EnvironmentDetector:
    def __init__(self):
        self.report = {
            "system": {},
            "network": {},
            "user": {}
        }

    def detect_system(self) -> Dict:
        """检测系统基础环境"""
        self.report["system"] = {
            "platform": platform.platform(),
            "system": platform.system(),
            "release": platform.release(),
            "architecture": platform.architecture(),
            "locale": locale.getdefaultlocale(),
            "timezone": str(datetime.datetime.now().astimezone().tzinfo),
            "time_format": datetime.datetime.now().strftime("%x %X"),
            "python_version": platform.python_version()
        }
        return self.report["system"]

    def detect_network(self) -> Dict:
        """检测网络环境"""
        try:
            # 国内环境检测
            resp = requests.get('https://ipapi.co/json/', timeout=3)
            data = resp.json()
            
            self.report["network"] = {
                "ip": data.get("ip"),
                "country": data.get("country_name"),
                "country_code": data.get("country_code"),
                "region": data.get("region"),
                "city": data.get("city"),
                "isp": data.get("org"),
                "is_china": data.get("country_code") == "CN",
                "hostname": socket.gethostname(),
                "local_ip": socket.gethostbyname(socket.gethostname())
            }
        except Exception as e:
            self.report["network"] = {
                "error": str(e),
                "is_china": True  # 默认按国内环境处理
            }
        return self.report["network"]

    def detect_user_profile(self) -> Dict:
        """收集用户画像信息"""
        print("\n=== 用户技术背景调查 ===")
        self.report["user"] = {
            "experience": input("1. 编程经验 [1]小白 [2]初级 [3]中级 [4]高级: "),
            "languages": input("2. 常用编程语言(用逗号分隔): ").split(","),
            "env_type": input("3. 网络环境 [1]家庭 [2]企业 [3]教育网 [4]其他: "),
            "special_needs": input("4. 特殊需求(无障碍/语言等): ")
        }
        return self.report["user"]

    def generate_report(self, format: str = "markdown") -> str:
        """生成环境报告"""
        if format == "json":
            return json.dumps(self.report, indent=2, ensure_ascii=False)
        
        # Markdown格式报告
        report = "# 环境检测报告\n\n"
        report += "## 系统信息\n"
        report += f"- 操作系统: {self.report['system']['platform']}\n"
        report += f"- 系统语言: {self.report['system']['locale'][0]}\n"
        report += f"- 时区: {self.report['system']['timezone']}\n"
        
        report += "\n## 网络环境\n"
        if "error" in self.report["network"]:
            report += f"- 检测失败: {self.report['network']['error']}\n"
        else:
            report += f"- 国家/地区: {self.report['network']['country']} ({self.report['network']['country_code']})\n"
            report += f"- 网络类型: {'国内' if self.report['network']['is_china'] else '国际'}\n"
            report += f"- ISP提供商: {self.report['network']['isp']}\n"
        
        report += "\n## 用户画像\n"
        report += f"- 技术等级: {self.report['user'].get('experience', '未填写')}\n"
        report += f"- 常用语言: {', '.join(self.report['user'].get('languages', []))}\n"
        report += f"- 特殊需求: {self.report['user'].get('special_needs', '无')}\n"
        
        return report

if __name__ == "__main__":
    detector = EnvironmentDetector()
    print("正在检测系统环境...")
    detector.detect_system()
    
    print("\n正在检测网络环境...")
    detector.detect_network()
    
    detector.detect_user_profile()
    
    print("\n" + detector.generate_report())
    
    # 保存报告到文件
    with open("environment_report.md", "w", encoding="utf-8") as f:
        f.write(detector.generate_report())
    print("报告已保存到 environment_report.md")