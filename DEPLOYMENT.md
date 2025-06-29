# AI-Core-Enhancement 部署指南

## 系统要求
- Windows 10/11 或 Linux/macOS
- Python 3.8+
- Git 2.30+

## 本地部署指南

### 一键部署 (推荐)
```bash
# Windows系统直接双击运行
deploy_local.bat

# 或命令行执行
./deploy_local.bat

# 如果出现乱码问题：
# 1. 确保系统区域设置为中文(简体，中国)
# 2. 或者手动执行：chcp 65001 切换为UTF-8编码
# 3. 使用新版Windows终端(Windows Terminal)
```

### 1. 环境准备
- 确保系统已安装：
  - Python 3.8+
  - Git 2.30+
  - 推荐使用Windows 10/11或Linux/macOS

### 2. 获取代码
```bash
git clone https://github.com/85391242/AI-Core-Enhancement.git
cd AI-Core-Enhancement
```

### 3. 设置隔离环境
```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 4. 运行应用
```bash
# 启动主程序
python start_autopilot.py

# 或使用开发模式(带热重载)
python -m flask run --debug
```

### 5. 验证部署
- 访问 http://localhost:5000
- 检查控制台输出是否正常

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

## 腾讯云部署方案（推荐）

### 使用CloudBase云开发部署

1. **开通服务**
   - 登录[腾讯云控制台](https://console.cloud.tencent.com/)
   - 搜索并开通"云开发 CloudBase"服务

2. **创建环境**
   ```bash
   # 安装CloudBase CLI
   npm install -g @cloudbase/cli

   # 初始化项目
   tcb init

   # 选择环境类型（选择Web应用）
   # 关联已有环境或创建新环境
   ```

3. **部署应用**
   ```bash
   # 安装依赖（使用云函数部署）
   tcb functions:deploy

   # 部署静态资源
   tcb hosting:deploy -e 你的环境ID
   ```

4. **访问应用**
   - 控制台会提供默认访问域名
   - 可在CloudBase控制台查看日志和监控

### 传统服务器部署
如需使用腾讯云CVM或轻量服务器，步骤与本地部署相同：
1. 购买并登录服务器
2. 按照本地部署指南操作即可

## 常见问题
1. **Python未找到**：请确保已安装Python并添加到PATH
2. **依赖安装失败**：尝试升级pip `python -m pip install --upgrade pip`
3. **权限问题**：在Linux/macOS上可能需要使用`sudo`
4. **腾讯云部署问题**：
   - 确保账户有足够权限
   - 检查地域是否选择正确
   - 配额不足时可申请提升

如需更多帮助，请参考项目文档或提交Issue。