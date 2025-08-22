# Logger Unzip Tool

[LJJLogger](https://github.com/blantian/LJJLogger) 配套日志解密工具，支持跨平台运行。

## 📦 安装

### 方法1: 从源码运行

```bash
# 克隆项目
git clone <repository-url>
cd LoggerUnzip

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 运行程序
python app.py
```

### 方法2: 使用预编译版本

下载对应平台的预编译版本，解压后直接运行。

## 🛠️ 构建

### 构建可执行文件（推荐）

```bash
# 安装构建依赖
pip install -r requirements.txt

# 跨平台构建（根据当前系统生成对应可执行文件）
python build_cross_platform.py
```

构建完成后，可执行文件将位于 `dist/` 目录下（例如 `dist/macos/LoggerUnzipTool`）。

### 手动构建（可选）

```bash
# 使用PyInstaller与通用配置
pyinstaller build_config_universal.spec
```

## 📁 项目结构

```
LoggerUnzip/
├── src/                    # 源代码模块
│   ├── __init__.py
│   ├── decryptor.py       # 核心解密模块
│   ├── file_processor.py  # 文件处理模块
│   ├── system_utils.py    # 系统工具模块
│   ├── ui_components.py   # UI组件模块
│   ├── worker_thread.py   # 工作线程模块
│   └── main_window.py     # 主窗口模块
├── app.py                 # 主程序入口
├── requirements.txt       # 项目依赖
├── setup.py              # 打包配置
├── build_config_universal.spec  # PyInstaller通用配置
├── build_cross_platform.py      # 跨平台构建脚本
└── README.md             # 项目说明
```

## 🎯 功能

- **文件选择**: 支持拖拽和浏览选择文件
- **智能解密**: AES解密 + Gzip解压缩
- **自动格式化**: JSON日志自动格式化
- **时间戳转换**: 自动转换时间戳为可读格式
- **实时日志**: 处理过程实时显示
- **自动打开**: 解密完成后自动打开文件
- **跨平台**: 支持Windows、macOS、Linux

## 🔧 技术栈

- **PySide6**: 现代化Qt界面框架
- **cryptography**: 安全加密解密库
- **PyInstaller**: 跨平台打包工具
- **Python 3.8+**: 现代Python特性支持

## 📋 系统要求

- Python 3.8 或更高版本
- Windows 10+, macOS 10.14+, 或 Linux
- 至少 100MB 可用磁盘空间
