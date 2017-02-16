"""通用参数."""
import os

# 程序根目录
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 秘钥文件路径，在不同机器上使用本程序需配置此参数
private_key_filepath = r'c:\Users\Administrator\.ssh\id_rsa'

# 主机信息文件目录
hosts_filepath = os.path.join(BASE_PATH, 'conf', 'hostlist.json')
