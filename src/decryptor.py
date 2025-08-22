"""
核心解密模块
处理AES解密和gzip解压缩
"""

import gzip
import io
import codecs
import struct
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class LogDecryptor:
    """日志解密器"""
    
    def __init__(self, key: bytes, iv: bytes):
        """
        初始化解密器
        
        Args:
            key: AES密钥
            iv: AES初始化向量
        """
        self.key = key
        self.iv = iv
    
    def decrypt_file(self, infile: str, dst: str) -> bool:
        """
        解密日志文件
        
        Args:
            infile: 输入文件路径
            dst: 输出文件路径
            
        Returns:
            bool: 解密是否成功
        """
        try:
            with open(dst, 'wb') as dst_file:
                with codecs.open(infile, mode='rb') as file:
                    # 读取1个字节
                    while file.read(1) == b'\x01':
                        # 读取四个字节, 转成int(大端)
                        bts = file.read(4)
                        size = struct.unpack('>I', bts)[0]

                        if size == 0:
                            break

                        # 读取加密内容
                        encrypted_content = file.read(size)
                        if not encrypted_content:
                            break
                            
                        # AES 解密
                        decrypted = self._decrypt_aes(encrypted_content)

                        # 读取压缩内容
                        compressed_content = decrypted

                        # 获取最后一个字节
                        last_byte = compressed_content[-1]
                        byte_val = struct.pack('>B', last_byte)
                        padding_length = struct.unpack('>B', byte_val)[0]

                        # 截取padding之前字节
                        compressed_content = compressed_content[0:-padding_length]

                        # 解压
                        try:
                            decompressed = self._decompress_gzip(compressed_content)
                            dst_file.write(decompressed)
                        except Exception as e:
                            print(f"解压失败，错误信息：{e}")
                            continue

                        # 只有存在填充时，才读一个尾巴
                        if padding_length != 0:
                            tail = file.read(1)
            
            return True
            
        except Exception as e:
            print(f"解密文件时出错: {e}")
            return False
    
    def _decrypt_aes(self, encrypted_content: bytes) -> bytes:
        """
        AES解密
        
        Args:
            encrypted_content: 加密内容
            
        Returns:
            bytes: 解密后的内容
        """
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(self.iv), backend=default_backend())
        decryptor = cipher.decryptor()
        return decryptor.update(encrypted_content) + decryptor.finalize()
    
    def _decompress_gzip(self, compressed_content: bytes) -> bytes:
        """
        Gzip解压缩
        
        Args:
            compressed_content: 压缩内容
            
        Returns:
            bytes: 解压缩后的内容
        """
        temp_io = io.BytesIO(compressed_content)
        with gzip.GzipFile(mode='rb', fileobj=temp_io) as un_gzip_io:
            return un_gzip_io.read()


# 保持向后兼容的函数
def logan_parse(infile: str, dst: str, key: bytes, iv: bytes) -> bool:
    """
    Args:
        infile: 输入文件
        dst: 输出文件地址
        key: AES密钥
        iv: AES初始化向量
        
    Returns:
        bool: 解析是否成功
    """
    decryptor = LogDecryptor(key, iv)
    return decryptor.decrypt_file(infile, dst) 