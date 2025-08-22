"""
工作线程模块
处理后台解密任务
"""

import os
from PySide6.QtCore import QThread, Signal
from .decryptor import LogDecryptor
from .file_processor import FileProcessor


class DecryptWorkerThread(QThread):
    """解密工作线程"""
    
    # 信号定义
    log_signal = Signal(str)
    finished_signal = Signal()
    error_signal = Signal(str)
    
    def __init__(self, file_path: str, key: bytes, iv: bytes):
        """
        初始化解密工作线程
        
        Args:
            file_path: 输入文件路径
            key: AES密钥
            iv: AES初始化向量
        """
        super().__init__()
        self.file_path = file_path
        self.key = key
        self.iv = iv
        self.output_dir = None
        self.output_file_path = None
    
    def run(self):
        """执行解密任务"""
        try:
            # 创建输出目录
            self.output_dir = FileProcessor.get_output_directory(self.file_path)
            
            self.log_signal.emit("开始解密文件...")
            
            # 获取文件名并处理
            file_name = os.path.basename(self.file_path)
            out_name = FileProcessor.process_filename(file_name)
            
            # 检查是否需要调整文件名
            if out_name.endswith('.zip.txt'):
                original_name = out_name
                out_name = out_name.replace('.zip.txt', '.txt')
                self.log_signal.emit(f"文件名已调整: {original_name} -> {out_name}")
            
            # 构建输出文件路径
            outfile = os.path.join(self.output_dir, out_name)
            
            # 检查是否已存在同名文件
            if os.path.exists(outfile):
                self.log_signal.emit(f'跳过 {self.file_path}, 已存在输出文件 {out_name}')
                self.output_file_path = outfile
                return
            
            self.log_signal.emit(f'处理文件: {file_name} -> {out_name}')
            
            # 执行解密
            decryptor = LogDecryptor(self.key, self.iv)
            if not decryptor.decrypt_file(self.file_path, outfile):
                self.error_signal.emit("解密失败")
                return
            
            # 格式化输出
            self.log_signal.emit("格式化日志内容...")
            formatted_lines = FileProcessor.format_log_content(outfile)
            
            if not FileProcessor.save_formatted_content(outfile, formatted_lines):
                self.error_signal.emit("保存格式化内容失败")
                return
            
            # 保存输出文件路径
            self.output_file_path = outfile
            
            self.log_signal.emit(f'解密完成: {out_name}')
            self.log_signal.emit(f'输出目录: {self.output_dir}')
            
        except Exception as e:
            self.error_signal.emit(f"解密过程中出错: {e}")
        finally:
            self.finished_signal.emit() 