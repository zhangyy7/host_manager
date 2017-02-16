"""主机管理核心逻辑模块."""
# ! /usr/bin/env python
# -*- coding: utf-8 -*-
import paramiko
import json
from conf import settings


class HostManager(object):
    """主机管理类，实现了增、删、查、命令分发、文件传输几个功能."""

    _private_key = paramiko.RSAKey(filename=settings.private_key_filepath)
    _hosts_filepath = settings.hosts_filepath

    def __init__(self):
        """初始化所需参数."""
        self.ssh_client = paramiko.SSHClient()

    def show_hosts(self, parameter_list):
        """加载主机配置文件，并展示主机列表."""
        pass

    def add_host(self, hostname, port, group, version):
        """添加主机."""
        self._json_load_from_file()

    def remove_host(self):
        """删除主机."""
        pass

    def exec_command(self, command):
        """在指定主机上执行命令."""
        pass

    def transfer_files(self):
        """与指定主机传输文件."""
        pass

    def _json_load_from_file(self):
        """从文件load数据到内存."""
        with open(self._hosts_filepath) as hosts_fp:
            self.hosts = json.load(hosts_fp)

    def _json_dump_to_file(self):
        """将内存的数据序列号到文件."""
        with open(self._hosts_filepath, 'w') as hosts_fp:
            json.dump(self.hosts, hosts_fp, sort_keys=True, ensure_ascii=False)
