import sys
import subprocess
import importlib

def check_python():
    print("\n=== Python环境检查 ===")
    print(f"Python路径: {sys.executable}")
    print(f"版本: {sys.version}")
    print(f"系统路径: {sys.path}")

def check_dependencies():
    print("\n=== 依赖检查 ===")
    deps = ['watchdog', 'psutil', 'pywin32', 'python-dotenv']
    for dep in deps:
        try:
            module = importlib.import_module(dep)
            print(f"✅ {dep:10} 版本: {module.__version__ if hasattr(module, '__version__') else '未知'}")
        except ImportError as e:
            print(f"❌ {dep:10} 未安装: {e}")

def check_virtualenv():
    print("\n=== 虚拟环境检查 ===")
    try:
        import venv
        print("✅ venv模块可用")
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            print("✅ 当前在虚拟环境中运行")
        else:
            print("⚠️ 未检测到虚拟环境")
    except Exception as e:
        print(f"❌ 虚拟环境检查失败: {e}")

def suggest_fixes():
    print("\n=== 修复建议 ===")
    if 'watchdog' not in sys.modules:
        print("1. 安装缺失依赖:")
        print("   pip install watchdog psutil pywin32 python-dotenv")
        
    if not (hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)):
        print("\n2. 建议使用虚拟环境:")
        print("   python -m venv .venv")
        print("   # Windows:")
        print("   .\\.venv\\Scripts\\activate")
        print("   # Linux/Mac:")
        print("   source .venv/bin/activate")

    print("\n3. 验证修复:")
    print("   python check_environment.py")

if __name__ == "__main__":
    check_python()
    check_virtualenv()
    check_dependencies()
    suggest_fixes()