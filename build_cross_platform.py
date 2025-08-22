#!/usr/bin/env python3
"""
跨平台构建脚本
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def run_command(command, description):
    """运行命令并处理错误"""
    print(f"正在{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description}成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description}失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False


def get_system_info():
    """获取系统信息"""
    system = platform.system()
    machine = platform.machine()
    architecture = platform.architecture()[0]
    
    print(f"当前系统: {system}")
    print(f"机器类型: {machine}")
    print(f"架构: {architecture}")
    
    return system, machine, architecture


def build_for_current_platform():
    """为当前平台构建"""
    system, machine, architecture = get_system_info()
    
    # 设置环境变量
    os.environ['PYTHONOPTIMIZE'] = '2'
    
    if system == "Darwin":  # macOS
        os.environ['QT_QPA_PLATFORM'] = 'cocoa'
        dist_path = "dist/macos"
    elif system == "Windows":
        dist_path = "dist/windows"
    elif system == "Linux":
        os.environ['QT_QPA_PLATFORM'] = 'xcb'
        dist_path = "dist/linux"
    else:
        dist_path = "dist/unknown"
    
    # 清理之前的构建
    clean_build()
    
    # 构建命令
    command = (
        f"pyinstaller build_config_universal.spec "
        f"--distpath {dist_path} "
        f"--workpath build/{system.lower()} "
        f"--clean "
        f"--noconfirm "
        f"--log-level WARN"
    )
    
    if not run_command(command, f"构建{system}版本"):
        return False
    
    # 设置权限和优化
    optimize_executable(dist_path, system)
    
    return True


def optimize_executable(dist_path, system):
    """优化可执行文件"""
    if system == "Darwin":
        exe_path = os.path.join(dist_path, "LoggerUnzipTool")
    elif system == "Windows":
        exe_path = os.path.join(dist_path, "LoggerUnzipTool.exe")
    else:
        exe_path = os.path.join(dist_path, "LoggerUnzipTool")
    
    if not os.path.exists(exe_path):
        print("可执行文件不存在，跳过优化")
        return
    
    print("优化可执行文件...")
    
    # 设置可执行权限
    if system != "Windows":
        os.chmod(exe_path, 0o755)
        print("✓ 设置可执行权限")
    
    # macOS特定优化
    if system == "Darwin":
        try:
            # 代码签名（可选）
            subprocess.run(["codesign", "--force", "--deep", "--sign", "-", exe_path], 
                          check=True, capture_output=True)
            print("✓ 代码签名完成")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠ 代码签名跳过（codesign不可用）")
        
        # 创建通用二进制文件（如果支持）
        if platform.machine() == "arm64":
            print("检测到Apple Silicon，确保兼容性...")
    
    # 获取文件大小
    file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
    print(f"✓ 可执行文件大小: {file_size:.1f} MB")
    print(f"✓ 可执行文件位置: {exe_path}")


def clean_build():
    """清理构建文件"""
    print("清理构建文件...")
    
    dirs_to_clean = ["build", "__pycache__", "src/__pycache__"]
    files_to_clean = ["*.spec"]
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            import shutil
            shutil.rmtree(dir_name)
            print(f"✓ 删除目录: {dir_name}")
    
    for pattern in files_to_clean:
        for file_path in Path(".").glob(pattern):
            if file_path.name != "build_config_universal.spec":
                file_path.unlink()
                print(f"✓ 删除文件: {file_path}")


def create_installer_script():
    """创建安装脚本"""
    system, machine, architecture = get_system_info()
    
    if system == "Darwin":
        create_macos_installer()
    elif system == "Windows":
        create_windows_installer()
    elif system == "Linux":
        create_linux_installer()


def create_macos_installer():
    """创建macOS安装脚本"""
    installer_script = """#!/bin/bash
# LoggerUnzipTool 安装脚本 (macOS)

echo "正在安装 LoggerUnzipTool..."

# 检查是否已安装
if [ -f "/usr/local/bin/LoggerUnzipTool" ]; then
    echo "检测到已安装的版本，正在更新..."
    sudo rm -f /usr/local/bin/LoggerUnzipTool
fi

# 复制到系统目录
sudo cp -R LoggerUnzipTool /usr/local/bin/
sudo chmod +x /usr/local/bin/LoggerUnzipTool

echo "安装完成！"
echo "使用方法: LoggerUnzipTool"
"""
    
    with open("install_macos.sh", "w") as f:
        f.write(installer_script)
    
    os.chmod("install_macos.sh", 0o755)
    print("✓ 创建macOS安装脚本: install_macos.sh")


def create_windows_installer():
    """创建Windows安装脚本"""
    installer_script = """@echo off
REM LoggerUnzipTool 安装脚本 (Windows)

echo 正在安装 LoggerUnzipTool...

REM 检查是否已安装
if exist "C:\\Program Files\\LoggerUnzipTool\\LoggerUnzipTool.exe" (
    echo 检测到已安装的版本，正在更新...
    rmdir /s /q "C:\\Program Files\\LoggerUnzipTool"
)

REM 创建安装目录
mkdir "C:\\Program Files\\LoggerUnzipTool"

REM 复制文件
xcopy /s /y LoggerUnzipTool.exe "C:\\Program Files\\LoggerUnzipTool\\"

REM 创建桌面快捷方式
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%USERPROFILE%\\Desktop\\LoggerUnzipTool.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "C:\\Program Files\\LoggerUnzipTool\\LoggerUnzipTool.exe" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs
cscript CreateShortcut.vbs
del CreateShortcut.vbs

echo 安装完成！
echo 使用方法: 双击桌面快捷方式或在开始菜单中搜索
"""
    
    with open("install_windows.bat", "w") as f:
        f.write(installer_script)
    
    print("✓ 创建Windows安装脚本: install_windows.bat")


def create_linux_installer():
    """创建Linux安装脚本"""
    installer_script = """#!/bin/bash
# LoggerUnzipTool 安装脚本 (Linux)

echo "正在安装 LoggerUnzipTool..."

# 检查是否已安装
if [ -f "/usr/local/bin/LoggerUnzipTool" ]; then
    echo "检测到已安装的版本，正在更新..."
    sudo rm -f /usr/local/bin/LoggerUnzipTool
fi

# 复制到系统目录
sudo cp LoggerUnzipTool /usr/local/bin/
sudo chmod +x /usr/local/bin/LoggerUnzipTool

# 创建桌面文件
cat > LoggerUnzipTool.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=LoggerUnzipTool
Comment=Log file decryption tool
Exec=/usr/local/bin/LoggerUnzipTool
Icon=text-x-generic
Terminal=false
Categories=Utility;
EOF

# 安装桌面文件
sudo cp LoggerUnzipTool.desktop /usr/share/applications/
rm LoggerUnzipTool.desktop

echo "安装完成！"
echo "使用方法: LoggerUnzipTool 或在应用程序菜单中搜索"
"""
    
    with open("install_linux.sh", "w") as f:
        f.write(installer_script)
    
    os.chmod("install_linux.sh", 0o755)
    print("✓ 创建Linux安装脚本: install_linux.sh")


def main():
    """主函数"""
    print("Logger Unzip Tool - 跨平台构建脚本")
    print("=" * 40)
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("错误: 需要Python 3.8或更高版本")
        return 1
    
    # 获取系统信息
    system, machine, architecture = get_system_info()
    print()
    
    # 构建当前平台版本
    if not build_for_current_platform():
        return 1
    
    # 创建安装脚本
    create_installer_script()
    
    print("\n🎉 跨平台构建完成!")
    print(f"可执行文件已生成，支持在相同架构的{system}系统上运行")
    print("请将整个dist目录分发给目标用户")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 