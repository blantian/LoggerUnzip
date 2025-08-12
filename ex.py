import gzip
import io
import codecs
import struct
from Crypto.Cipher import AES


def logan_parse(infile, dst, key, iv):
    """
    logan 文件解密
    :param iv: aes key
    :param key: aes iv
    :param infile: 输入文件
    :param dst: 输出文件地址
    :return: NULL
    """
    with open(dst, 'wb') as dst:
        with codecs.open(infile, mode='rb') as file:
            # 读取1个字节
            while file.read(1) == b'\x01':
                # 读取四个字节, 转成int(大端)
                bts = file.read(4)
                print("four bytes: ", [bts])
                size = struct.unpack('>I', bts)[0]
                print("size: ", size)

                if size == 0:
                    print("size is 0, break loop.")
                    break

                # 读取加密内容
                encrypted_content = file.read(size)
                print("encrypted_content: ", [encrypted_content])
                if not encrypted_content:
                    print("encrypted_content is empty, break loop.")
                    break
                # aes 解密
                aes_decrypt = AES.new(key, AES.MODE_CBC, iv)
                decrypted = aes_decrypt.decrypt(encrypted_content)
                print("decrypted_content: ", [decrypted])

                # 读取压缩内容
                compressed_content = decrypted

                # 获取最后一个字节
                # '>b' 只能表示 -127-128 的有符号证书，'>B' 可以表示 0-255
                # 这里可能会得到 255 的整数值
                last_byte = compressed_content[-1]
                byte_val = struct.pack('>B', last_byte)
                padding_length = struct.unpack('>B', byte_val)[0]
                print("padding_len: ", padding_length)

                # 截取padding之前字节
                compressed_content = compressed_content[0:-padding_length]
                # print ("compressed_content: ", [compressed_content])

                # 解压
                # 会出现解压失败的情况，直接跳过这段数据
                try:
                    temp_io = io.BytesIO(compressed_content)
                    un_gzip_io = gzip.GzipFile(mode='rb', fileobj=temp_io)
                    decompressed = un_gzip_io.read()
                    # 写入文件
                    # print("decompressed_content: ", decompressed)
                    dst.write(decompressed)
                except Exception as e:
                    print("解压失败，错误信息：", e)
                    continue

                # 只有存在填充时，才读一个尾巴
                if padding_length != 0:
                    tail = file.read(1)
                    print("tail:", tail)