"""主机管理核心逻辑模块."""
# ! /usr/bin/env python
# -*- coding: utf-8 -*-
import paramiko
import json
import queue
import collections
from conf import settings


class HostManager(object):
    """主机管理类，实现了增、删、查、命令分发、文件传输几个功能."""

    _private_key = paramiko.RSAKey(filename=settings.private_key_filepath)
    _hosts_filepath = settings.hosts_filepath

    def __init__(self):
        """初始化所需参数."""
        self.ssh_client = paramiko.SSHClient()

    def show_all_hosts(self):
        """加载主机配置文件，并展示所有主机信息."""
        hosts = self._json_load_from_file()
        host_info_list = []
        for hostid in hosts:
            temp = "hostid:{}, hostname:{}, port:{}, group:{}, version:{}"
            host_info = temp.format(
                hostid,
                hosts[hostid]["hostname"],
                hosts[hostid]["port"],
                hosts[hostid]["group"],
                hosts[hostid]["version"])
            host_info_list.append(host_info)
        host_info_str = '\n'.join(host_info_list)
        print(host_info_str)

    def show_hosts_by_group(self):
        """加载主机配置文件，并展示所有主机信息."""
        pass

    def add_host(self, hostname, port, username, group, version):
        """添加主机."""
        hosts = self._json_load_from_file()
        host_id = str(max([int(i) for i in hosts]) + 1)
        hosts[host_id] = {
            "hostname": hostname,
            "port": port,
            "username": username,
            "group": group,
            "version": version}
        self._json_dump_to_file(hosts)

    def remove_host(self, host_id):
        """删除主机."""
        hosts = self._json_load_from_file()
        if host_id in hosts:
            del hosts[host_id]

    def exec_command(self, host_list, command):
        """在指定主机上执行命令."""
        res_queue = collections.defaultdict(queue.Queue())
        for host in host_list:
            hostname, port, username = host
            self.ssh_client.connect(
                hostname, port, username, pkey=self._private_key)
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            res, err = stdout.read(), stderr.read()
            result = res if res else err
            res_queue[hostname].put(result)
        return res_queue

    def transfer_files(self):
        """与指定主机传输文件."""
        pass

    def _json_load_from_file(self):
        """从文件load数据到内存."""
        with open(self._hosts_filepath) as hosts_fp:
            hosts = json.load(hosts_fp)
        return hosts

    def _json_dump_to_file(self, hosts):
        """将内存的数据序列号到文件."""
        with open(self._hosts_filepath, 'w') as hosts_fp:
            json.dump(hosts, hosts_fp, sort_keys=True, ensure_ascii=False)
