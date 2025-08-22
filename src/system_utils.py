"""
系统工具模块
处理跨平台功能
"""

import os
import platform
import subprocess
from typing import Optional


class SystemUtils:
    """系统工具类"""
    
    @staticmethod
    def get_system() -> str:
        """
        获取当前操作系统
        
        Returns:
            str: 操作系统名称
        """
        return platform.system()
    
    @staticmethod
    def open_file(file_path: str) -> bool:
        """
        用默认程序打开文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否成功打开
        """
        if not os.path.exists(file_path):
            return False
        
        try:
            system = SystemUtils.get_system()
            
            if system == "Darwin":  # macOS
                subprocess.run(["open", file_path], check=True)
            elif system == "Windows":
                subprocess.run(["notepad", file_path], check=True)
            elif system == "Linux":
                subprocess.run(["xdg-open", file_path], check=True)
            else:
                # 通用方法
                subprocess.run(["open", file_path], check=True)
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"打开文件失败: {e}")
            return False
        except Exception as e:
            print(f"打开文件时出错: {e}")
            return False
    
    @staticmethod
    def open_directory(directory_path: str) -> bool:
        """
        打开目录
        
        Args:
            directory_path: 目录路径
            
        Returns:
            bool: 是否成功打开
        """
        if not os.path.exists(directory_path):
            return False
        
        try:
            system = SystemUtils.get_system()
            
            if system == "Darwin":  # macOS
                subprocess.run(["open", directory_path], check=True)
            elif system == "Windows":
                subprocess.run(["explorer", directory_path], check=True)
            elif system == "Linux":
                subprocess.run(["xdg-open", directory_path], check=True)
            else:
                subprocess.run(["open", directory_path], check=True)
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"打开目录失败: {e}")
            return False
        except Exception as e:
            print(f"打开目录时出错: {e}")
            return False
    
    @staticmethod
    def get_default_editor() -> Optional[str]:
        """
        获取默认文本编辑器
        
        Returns:
            Optional[str]: 编辑器路径或None
        """
        system = SystemUtils.get_system()
        
        if system == "Darwin":  # macOS
            return "TextEdit"
        elif system == "Windows":
            return "notepad"
        elif system == "Linux":
            # 尝试常见的Linux编辑器
            editors = ["gedit", "nano", "vim", "vi"]
            for editor in editors:
                try:
                    subprocess.run(["which", editor], check=True, capture_output=True)
                    return editor
                except subprocess.CalledProcessError:
                    continue
            return None
        else:
            return None
    
    @staticmethod
    def is_macos() -> bool:
        """是否为macOS系统"""
        return SystemUtils.get_system() == "Darwin"
    
    @staticmethod
    def is_windows() -> bool:
        """是否为Windows系统"""
        return SystemUtils.get_system() == "Windows"
    
    @staticmethod
    def is_linux() -> bool:
        """是否为Linux系统"""
        return SystemUtils.get_system() == "Linux" 