"""
文件处理模块
处理文件名转换、格式化等
"""

import os
import json
from datetime import datetime
from typing import List, Tuple


class FileProcessor:
    """文件处理器"""
    
    @staticmethod
    def process_filename(file_name: str) -> str:
        """
        处理文件名
        
        Args:
            file_name: 原始文件名
            
        Returns:
            str: 处理后的文件名
        """
        # 检查文件名是否为数字（时间戳）
        if not file_name.isdigit():
            # 如果不是数字，直接使用原文件名
            out_name = file_name + '.txt'
        else:
            # 如果是数字，转换为时间格式
            ts = int(file_name)
            dt = datetime.fromtimestamp(ts/1000)
            out_name = dt.strftime('%Y%m%d_%H_%M_%S.txt')
        
        # 处理文件名，移除.zip后缀
        if out_name.endswith('.zip.txt'):
            out_name = out_name.replace('.zip.txt', '.txt')
        
        return out_name
    
    @staticmethod
    def format_log_content(file_path: str) -> List[str]:
        """
        格式化日志内容
        
        Args:
            file_path: 日志文件路径
            
        Returns:
            List[str]: 格式化后的日志行列表
        """
        formatted_lines = []
        
        try:
            with open(file_path, 'rb') as f:
                for line in f:
                    try:
                        line = line.decode('utf-8').strip()
                    except UnicodeDecodeError:
                        continue  # 跳过无法解码的行
                    
                    if not line:
                        continue
                    
                    try:
                        log = json.loads(line)
                        formatted_line = FileProcessor._format_log_line(log)
                        formatted_lines.append(formatted_line)
                    except Exception as e:
                        formatted_lines.append(f'Parse error: {e} {line}')
        
        except Exception as e:
            print(f"格式化日志内容时出错: {e}")
        
        return formatted_lines
    
    @staticmethod
    def _format_log_line(log: dict) -> str:
        """
        格式化单行日志
        
        Args:
            log: 日志字典
            
        Returns:
            str: 格式化后的日志行
        """
        ts2 = log.get('l')
        if ts2:
            ts_fmt = datetime.fromtimestamp(ts2/1000).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        else:
            ts_fmt = ''
        
        thread_id = log.get('i', '')
        tag = log.get('n', '')
        content = log.get('c', '').strip()
        
        return f'{ts_fmt} {thread_id} {tag} {content}'
    
    @staticmethod
    def save_formatted_content(file_path: str, formatted_lines: List[str]) -> bool:
        """
        保存格式化后的内容
        
        Args:
            file_path: 文件路径
            formatted_lines: 格式化后的行列表
            
        Returns:
            bool: 保存是否成功
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for line in formatted_lines:
                    f.write(line + '\n')
            return True
        except Exception as e:
            print(f"保存格式化内容时出错: {e}")
            return False
    
    @staticmethod
    def get_output_directory(input_file_path: str) -> str:
        """
        获取输出目录
        
        Args:
            input_file_path: 输入文件路径
            
        Returns:
            str: 输出目录路径
        """
        file_dir = os.path.dirname(input_file_path)
        output_dir = os.path.join(file_dir, 'decompressionLogs')
        os.makedirs(output_dir, exist_ok=True)
        return output_dir
    
    @staticmethod
    def get_file_info(file_path: str) -> Tuple[str, int]:
        """
        获取文件信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            Tuple[str, int]: (文件名, 文件大小)
        """
        if not os.path.exists(file_path):
            return "", 0
        
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        return file_name, file_size 