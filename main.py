"""GUI utility for decrypting log files."""

from binascii import unhexlify
import os
import json
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
import threading

# The decryption helper module depends on ``pycryptodome``.  When the
# dependency is missing, importing it at module load time will raise an
# exception and prevent the GUI from being displayed.  To keep the interface
# usable, defer the import and capture the error for later reporting.
try:  # pragma: no cover - import error handling
    import ex  # type: ignore
    _ex_import_error = None
except Exception as e:  # pragma: no cover - executed only when import fails
    ex = None  # type: ignore
    _ex_import_error = e


class LoggerUnzipGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Logger Unzip Tool")
        self.root.geometry("800x600")
        
        # 默认参数
        self.key = b'1234567890abcdef'
        self.iv = b'abcdef1234567890'
        self.infile_dir = ''
        self.out_dir = ''

        self.setup_ui()

        # 如果解密模块加载失败，在日志区域给出提示，界面仍可正常使用。
        if _ex_import_error is not None:
            self.log_message(f"解密模块加载失败: {_ex_import_error}")
    
    def setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 文件路径输入区域
        file_frame = ttk.Frame(main_frame)
        file_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(file_frame, text="文件路径:").pack(side=tk.LEFT)
        self.file_path_var = tk.StringVar()
        self.file_path_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=50)
        self.file_path_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(file_frame, text="选择文件", command=self.select_file).pack(side=tk.RIGHT)
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        self.decrypt_btn = ttk.Button(button_frame, text="开始解密", command=self.start_decrypt)
        self.decrypt_btn.pack(side=tk.LEFT, padx=5)
        
        self.view_dir_btn = ttk.Button(button_frame, text="查看生成目录", command=self.view_generated_dir, state='disabled')
        self.view_dir_btn.pack(side=tk.LEFT, padx=5)
        
        # 进度条
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=5)
        
        # 日志显示区域
        ttk.Label(main_frame, text="处理日志:").pack(anchor=tk.W, pady=(10, 5))
        self.log_text = ScrolledText(main_frame, height=20, width=80)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 添加初始日志
        self.log_message("界面已加载完成")
    
    def select_file(self):
        """选择文件"""
        file_path = filedialog.askopenfilename(title="选择要解密的文件")
        if file_path:
            self.file_path_var.set(file_path)
            self.log_message(f"已选择文件: {file_path}")
    
    def view_generated_dir(self):
        """查看生成的目录"""
        if not hasattr(self, 'output_dir') or not self.output_dir:
            messagebox.showwarning("警告", "还没有生成输出目录")
            return
        
        if not os.path.exists(self.output_dir):
            self.log_message("输出目录不存在")
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
                file_size = os.path.getsize(file_path)
                self.log_message(f"  {i}. {file} ({file_size} bytes)")
                
        except Exception as e:
            self.log_message(f"查看生成目录时出错: {e}")
    
    def log_message(self, message):
        """在日志区域显示消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def start_decrypt(self):
        """开始解密文件"""
        if _ex_import_error is not None:
            messagebox.showerror("错误", f"解密模块加载失败: {_ex_import_error}")
            return

        file_path = self.file_path_var.get().strip()
        if not file_path:
            messagebox.showerror("错误", "请先选择或输入文件路径")
            return
        
        if not os.path.exists(file_path):
            messagebox.showerror("错误", "文件不存在")
            return
        
        # 在新线程中处理，避免界面冻结
        self.decrypt_btn.config(state='disabled')
        self.progress.start()
        
        thread = threading.Thread(target=self.decrypt_file, args=(file_path,))
        thread.daemon = True
        thread.start()
    
    def decrypt_file(self, file_path):
        """解密单个文件"""
        try:
            # 创建输出目录（在文件所在目录下创建logs2文件夹）
            file_dir = os.path.dirname(file_path)
            self.output_dir = os.path.join(file_dir, 'logs2')
            os.makedirs(self.output_dir, exist_ok=True)
            
            self.log_message("开始解密文件...")
            
            # 获取文件名（不包含路径）
            file_name = os.path.basename(file_path)
            
            # 检查文件名是否为数字（时间戳）
            if not file_name.isdigit():
                self.log_message(f"文件名 {file_name} 不是数字格式，尝试直接处理...")
                # 如果不是数字，直接使用原文件名
                out_name = file_name + '.txt'
            else:
                # 如果是数字，转换为时间格式
                ts = int(file_name)
                dt = datetime.fromtimestamp(ts/1000)
                out_name = dt.strftime('%Y%m%d_%H_%M_%S.txt')
            
            outfile = os.path.join(self.output_dir, out_name)
            
            # 如果已存在同名输出文件，则跳过
            if os.path.exists(outfile):
                self.log_message(f'跳过 {file_path}, 已存在输出文件 {out_name}')
                return
            
            self.log_message(f'处理文件: {file_name} -> {out_name}')
            
            # 解密文件
            ex.logan_parse(file_path, outfile, self.key, self.iv)
            
            # 格式化输出
            formatted_lines = []
            with open(outfile, 'rb') as f:
                for line in f:
                    try:
                        line = line.decode('utf-8').strip()
                    except UnicodeDecodeError:
                        continue  # 跳过无法解码的行
                    if not line:
                        continue
                    try:
                        log = json.loads(line)
                        ts2 = log.get('l')
                        if ts2:
                            ts_fmt = datetime.fromtimestamp(ts2/1000).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                        else:
                            ts_fmt = ''
                        thread_id = log.get('i', '')
                        tag = log.get('n', '')
                        content = log.get('c', '').strip()
                        formatted_lines.append(f'{ts_fmt} {thread_id} {tag} {content}')
                    except Exception as e:
                        formatted_lines.append(f'Parse error: {e} {line}')
            
            with open(outfile, 'w', encoding='utf-8') as f:
                for line in formatted_lines:
                    f.write(line + '\n')
            
            self.log_message(f'解密完成: {out_name}')
            self.log_message(f'输出目录: {self.output_dir}')
            
        except Exception as e:
            self.log_message(f"解密过程中出错: {e}")
        finally:
            # 恢复界面状态
            self.root.after(0, self.decrypt_finished)
    
    def decrypt_finished(self):
        """解密完成后的界面恢复"""
        self.progress.stop()
        self.decrypt_btn.config(state='normal')
        self.view_dir_btn.config(state='normal')
        messagebox.showinfo("完成", "文件解密完成!")


def main():
    root = tk.Tk()
    app = LoggerUnzipGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main() 