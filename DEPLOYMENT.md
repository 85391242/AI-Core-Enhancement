# AI-Core-Enhancement 部署指南

## 系统要求
- Windows 10/11 或 Linux/macOS
- Python 3.8+
- Git 2.30+

## 快速开始

### 1. 克隆仓库
```bash
git clone https://github.com/85391242/AI-Core-Enhancement.git
cd AI-Core-Enhancement
```

### 2. 设置Python虚拟环境
```bash
python -m venv .venv
```

#### Windows激活环境：
```bash
.venv\Scripts\activate
```

#### Linux/macOS激活环境：
```bash
source .venv/bin/activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 运行系统
```bash
python start_autopilot.py
```

## 一键部署脚本 (Windows)
将以下内容保存为`setup.bat`并运行：

```bat
@echo off
git clone https://github.com/85391242/AI-Core-Enhancement.git || (echo 克隆失败 && pause && exit /b 1)
cd AI-Core-Enhancement

python -m venv .venv || (echo 创建虚拟环境失败 && pause && exit /b 1)
call .venv\Scripts\activate || (echo 激活环境失败 && pause && exit /b 1)

pip install -r requirements.txt || (echo 依赖安装失败 && pause && exit /b 1)

echo 部署完成！输入以下命令启动系统：
echo python start_autopilot.py
pause
```

## 常见问题
1. **Python未找到**：请确保已安装Python并添加到PATH
2. **依赖安装失败**：尝试升级pip `python -m pip install --upgrade pip`
3. **权限问题**：在Linux/macOS上可能需要使用`sudo`

如需更多帮助，请参考项目文档或提交Issue。