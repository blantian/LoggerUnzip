"""
UI组件模块
包含样式定义和UI组件
"""

from PySide6.QtWidgets import QFrame, QPushButton, QLineEdit, QTextEdit, QProgressBar
from PySide6.QtGui import QFont


class UIStyles:
    """UI样式类"""
    
    @staticmethod
    def get_main_style() -> str:
        """获取主样式表"""
        return """
            QMainWindow {
                background-color: #f5f5f5;
            }
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:disabled {
                background-color: #ccc;
                color: #666;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 12px;
            }
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: #fafafa;
            }
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 3px;
            }
        """
    
    @staticmethod
    def get_dark_style() -> str:
        """获取深色主题样式表"""
        return """
            QMainWindow {
                background-color: #2d2d30;
                color: #ffffff;
            }
            QFrame {
                background-color: #3e3e42;
                border: 1px solid #555555;
                border-radius: 5px;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #555555;
                border-radius: 4px;
                font-size: 12px;
                background-color: #3e3e42;
                color: #ffffff;
            }
            QTextEdit {
                border: 1px solid #555555;
                border-radius: 4px;
                background-color: #2d2d30;
                color: #ffffff;
            }
            QProgressBar {
                border: 1px solid #555555;
                border-radius: 4px;
                text-align: center;
                background-color: #3e3e42;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 3px;
            }
            QLabel {
                color: #ffffff;
            }
        """


class UIComponents:
    """UI组件工厂类"""
    
    @staticmethod
    def create_styled_frame() -> QFrame:
        """创建样式化的框架"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        return frame
    
    @staticmethod
    def create_primary_button(text: str) -> QPushButton:
        """创建主要按钮"""
        button = QPushButton(text)
        button.setMinimumHeight(35)
        return button
    
    @staticmethod
    def create_file_input() -> QLineEdit:
        """创建文件输入框"""
        input_field = QLineEdit()
        input_field.setPlaceholderText("请选择要解密的文件...")
        return input_field
    
    @staticmethod
    def create_log_display() -> QTextEdit:
        """创建日志显示区域"""
        log_text = QTextEdit()
        log_text.setReadOnly(True)
        
        # 使用系统默认等宽字体，避免Consolas字体加载问题
        system_fonts = ["Monaco", "Menlo", "Courier New", "DejaVu Sans Mono", "Consolas"]
        font_found = False
        
        for font_name in system_fonts:
            font = QFont(font_name, 9)
            if font.exactMatch():
                log_text.setFont(font)
                font_found = True
                break
        
        # 如果没有找到等宽字体，使用系统默认字体
        if not font_found:
            log_text.setFont(QFont("Monaco", 9))
        
        return log_text
    
    @staticmethod
    def create_progress_bar() -> QProgressBar:
        """创建进度条"""
        progress_bar = QProgressBar()
        progress_bar.setVisible(False)
        return progress_bar 