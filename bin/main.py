"""程序启动的脚本."""
# ! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from core import hostmanager


def main():
    """程序主函数."""
    manager = hostmanager.manager
    func_dict = {"1": manager.show_host,
                 "2": manager.exec_command,
                 "3": manager.transfer_files,
                 "4": manager.add_host,
                 "5": manager.remove_host,
                 "6": sys.exit}
    while True:
        func = input(
            "【1.查主机信息 2.执行命令 3.文件传输 4.添加主机 5.删除主机 6.退出】\n").strip()
        active = func_dict.get(func, 0)
        if active:
            active()
        else:
            print("没有这个选项，请重新选择。")
