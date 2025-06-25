from datetime import datetime, timedelta
from typing import List, Dict
import json

class MigrationPlanner:
    def __init__(self):
        self.phases = self._load_default_plan()
        
    def _load_default_plan(self) -> List[Dict]:
        """默认的渐进式迁移计划"""
        return [
            {
                "name": "知识图谱试验",
                "start_date": datetime.now().strftime("%Y-%m-%d"),
                "duration": 14,
                "target": "建立10万实体规模的测试图谱",
                "rollback_plan": "恢复静态知识源配置"
            },
            {
                "name": "优化器并行运行",
                "start_date": (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d"),
                "duration": 21,
                "target": "新旧优化器结果对比验证",
                "rollback_plan": "停用RL优化器"
            },
            {
                "name": "全量切换",
                "start_date": (datetime.now() + timedelta(days=37)).strftime("%Y-%m-%d"),
                "duration": 7,
                "target": "完全过渡到v2.0系统",
                "rollback_plan": "版本回退脚本v1.2"
            }
        ]
    
    def generate_gantt_chart(self) -> str:
        """生成迁移甘特图"""
        chart = ["迁移计划甘特图".center(50, "=")]
        for phase in self.phases:
            start = datetime.strptime(phase["start_date"], "%Y-%m-%d")
            end = start + timedelta(days=phase["duration"])
            chart.append(
                f"{phase['name']}: {start.strftime('%m/%d')}-{end.strftime('%m/%d')}"
                f" | {'#' * phase['duration']}"
            )
        return "\n".join(chart)
    
    def get_current_phase(self, when: datetime = None) -> Dict:
        """获取当前所处的迁移阶段"""
        when = when or datetime.now()
        for phase in self.phases:
            start = datetime.strptime(phase["start_date"], "%Y-%m-%d")
            end = start + timedelta(days=phase["duration"])
            if start <= when <= end:
                return phase
        return {}

if __name__ == "__main__":
    planner = MigrationPlanner()
    print("=== 迁移计划 ===")
    print(json.dumps(planner.phases, indent=2))
    print("\n" + planner.generate_gantt_chart())
    
    current = planner.get_current_phase()
    if current:
        print(f"\n当前阶段: {current['name']} (剩余{(datetime.strptime(current['start_date'], '%Y-%m-%d') + timedelta(days=current['duration']) - datetime.now()).days}天)")