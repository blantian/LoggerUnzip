"""
主窗口模块
应用程序的主界面
"""

import os
from datetime import datetime
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QFileDialog, QMessageBox)
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtCore import QTimer

from .ui_components import UIStyles, UIComponents
from .worker_thread import DecryptWorkerThread
from .system_utils import SystemUtils
from .file_processor import FileProcessor


class LoggerUnzipMainWindow(QMainWindow):
    """日志解密工具主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Logger Unzip Tool")
        self.setGeometry(100, 100, 900, 700)
        
        # 默认参数
        self.key = b'1234567890abcdef'
        self.iv = b'abcdef1234567890'
        self.output_dir = None
        self.output_file_path = None
        self.decrypt_thread = None
        
        # 初始化UI
        self.setup_ui()
        self.setup_style()
        
        # 延迟显示初始日志，避免启动时的卡顿
        QTimer.singleShot(100, lambda: self.log_message("界面已加载完成"))
    
    def setup_ui(self):
        """设置用户界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # 文件路径输入区域
        self.setup_file_input_section(main_layout)
        
        # 按钮区域
        self.setup_button_section(main_layout)
        
        # 进度条
        self.progress_bar = UIComponents.create_progress_bar()
        main_layout.addWidget(self.progress_bar)
        
        # 日志显示区域
        self.setup_log_section(main_layout)
    
    def setup_file_input_section(self, main_layout):
        """设置文件输入区域"""
        file_frame = UIComponents.create_styled_frame()
        file_layout = QHBoxLayout(file_frame)
        
        file_label = QLabel("文件路径:")
        file_label.setMinimumWidth(80)
        file_layout.addWidget(file_label)
        
        self.file_path_edit = UIComponents.create_file_input()
        file_layout.addWidget(self.file_path_edit)
        
        self.select_file_btn = UIComponents.create_primary_button("选择文件")
        self.select_file_btn.clicked.connect(self.select_file)
        file_layout.addWidget(self.select_file_btn)
        
        main_layout.addWidget(file_frame)
    
    def setup_button_section(self, main_layout):
        """设置按钮区域"""
        button_frame = UIComponents.create_styled_frame()
        button_layout = QHBoxLayout(button_frame)
        
        self.decrypt_btn = UIComponents.create_primary_button("开始解密")
        self.decrypt_btn.clicked.connect(self.start_decrypt)
        button_layout.addWidget(self.decrypt_btn)
        
        self.view_dir_btn = UIComponents.create_primary_button("查看生成目录")
        self.view_dir_btn.clicked.connect(self.view_generated_dir)
        self.view_dir_btn.setEnabled(False)
        button_layout.addWidget(self.view_dir_btn)
        
        self.open_file_btn = UIComponents.create_primary_button("打开文件")
        self.open_file_btn.clicked.connect(self.open_decrypted_file)
        self.open_file_btn.setEnabled(False)
        button_layout.addWidget(self.open_file_btn)
        
        button_layout.addStretch()
        main_layout.addWidget(button_frame)
    
    def setup_log_section(self, main_layout):
        """设置日志显示区域"""
        log_label = QLabel("处理日志:")
        log_label.setFont(QFont("Arial", 10, QFont.Bold))
        main_layout.addWidget(log_label)
        
        self.log_text = UIComponents.create_log_display()
        main_layout.addWidget(self.log_text)
    
    def setup_style(self):
        """设置样式"""
        self.setStyleSheet(UIStyles.get_main_style())
    
    def select_file(self):
        """选择文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择要解密的文件", "", "All Files (*.*)"
        )
        if file_path:
            self.file_path_edit.setText(file_path)
            self.log_message(f"已选择文件: {file_path}")
    
    def view_generated_dir(self):
        """查看生成的目录"""
        if not self.output_dir or not os.path.exists(self.output_dir):
            QMessageBox.warning(self, "警告", "还没有生成输出目录")
            return
        
        try:
            files = os.listdir(self.output_dir)
            if not files:
                self.log_message("输出目录为空")
                return
            
            # 显示所有文件
            self.log_message(f"生成目录内容 (共{len(files)}个文件):")
            for i, file in enumerate(files, 1):
                file_path = os.path.join(self.output_dir, file)
                file_name, file_size = FileProcessor.get_file_info(file_path)
                self.log_message(f"  {i}. {file_name} ({file_size} bytes)")
                
        except Exception as e:
            self.log_message(f"查看生成目录时出错: {e}")
    
    def open_decrypted_file(self):
        """打开解密后的文件"""
        if not self.output_file_path:
            QMessageBox.warning(self, "警告", "还没有生成输出文件")
            return
        
        if not os.path.exists(self.output_file_path):
            QMessageBox.warning(self, "警告", "输出文件不存在")
            return
        
        if SystemUtils.open_file(self.output_file_path):
            self.log_message(f"已打开文件: {self.output_file_path}")
        else:
            QMessageBox.critical(self, "错误", "无法打开文件")
            self.log_message("打开文件失败")
    
    def log_message(self, message: str):
        """在日志区域显示消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
        # 滚动到底部
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_text.setTextCursor(cursor)
    
    def start_decrypt(self):
        """开始解密文件"""
        file_path = self.file_path_edit.text().strip()
        if not file_path:
            QMessageBox.critical(self, "错误", "请先选择或输入文件路径")
            return
        
        if not os.path.exists(file_path):
            QMessageBox.critical(self, "错误", "文件不存在")
            return
        
        # 禁用按钮，显示进度条
        self.decrypt_btn.setEnabled(False)
        self.view_dir_btn.setEnabled(False)
        self.open_file_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 设置为不确定模式
        
        # 创建并启动解密线程
        self.decrypt_thread = DecryptWorkerThread(file_path, self.key, self.iv)
        self.decrypt_thread.log_signal.connect(self.log_message)
        self.decrypt_thread.finished_signal.connect(self.decrypt_finished)
        self.decrypt_thread.error_signal.connect(self.decrypt_error)
        self.decrypt_thread.start()
    
    def decrypt_finished(self):
        """解密完成后的界面恢复"""
        self.progress_bar.setVisible(False)
        self.decrypt_btn.setEnabled(True)
        self.view_dir_btn.setEnabled(True)
        
        # 保存输出目录路径和文件路径
        if self.decrypt_thread:
            if hasattr(self.decrypt_thread, 'output_dir'):
                self.output_dir = self.decrypt_thread.output_dir
            if hasattr(self.decrypt_thread, 'output_file_path'):
                self.output_file_path = self.decrypt_thread.output_file_path
                self.open_file_btn.setEnabled(True)
        
        QMessageBox.information(self, "完成", "文件解密完成!")
        
        # 自动打开文件
        if self.output_file_path:
            self.open_decrypted_file()
    
    def decrypt_error(self, error_message: str):
        """解密错误处理"""
        self.progress_bar.setVisible(False)
        self.decrypt_btn.setEnabled(True)
        self.view_dir_btn.setEnabled(True)
        self.open_file_btn.setEnabled(False)
        QMessageBox.critical(self, "错误", error_message) 