"""最小化可视化组件实现"""
class VisualComponents:
    def __init__(self):
        self.components = {
            'status_panel': None,
            'decision_tree': None,
            'progress_bar': None
        }
    
    def get_feedback(self):
        """提供默认可视化反馈"""
        return {
            'ready': True,
            'components': list(self.components.keys())
        }
    
    def update_progress(self, progress):
        """空进度更新方法"""
        pass