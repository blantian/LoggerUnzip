#!/usr/bin/env python3
"""
Logger Unzip Tool - 主程序入口
"""

import sys
from PySide6.QtWidgets import QApplication
from src.main_window import LoggerUnzipMainWindow


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setApplicationName("Logger Unzip Tool")
    app.setApplicationVersion("2.0.0")
    
    # 创建并显示主窗口
    window = LoggerUnzipMainWindow()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec())


if __name__ == '__main__':
    main() 