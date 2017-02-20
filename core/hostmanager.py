"""主机管理核心逻辑模块."""
# ! /usr/bin/env python
# -*- coding: utf-8 -*-
import paramiko
import json
import queue
import collections
import threading
from conf import settings


class HostManager(object):
    """主机管理类，实现了增、删、查、命令分发、文件传输几个功能."""

    _private_key = paramiko.RSAKey(filename=settings.private_key_filepath)
    _hosts_filepath = settings.hosts_filepath

    def __init__(self):
        """初始化所需参数."""
        # self.ssh_client = paramiko.SSHClient()
        # self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.result_queue = collections.defaultdict(queue.Queue)

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

    def show_hosts_by_group(self, group):
        """加载主机配置文件，按组查询."""
        pass

    def add_host(self, hostname, port, username, group, version):
        """添加主机.

        :param hostname: ip地址
        :param port: 端口号
        :param username: 用户
        :param group: 组，本程序是按Linux发行版本分组，如Ubuntu、centos等
        :param version: 系统版本
        """
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
        self._json_dump_to_file(hosts)

    def exec_command(self, hostname, port, username, command):
        """在指定主机上执行命令.

        :param hostname: ip地址
        :param port: 端口
        :param username: 用户名
        :param command: 命令
        """
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(
            hostname, port, username, pkey=self._private_key)
        stdin, stdout, stderr = ssh_client.exec_command(command)
        res, err = stdout.read(), stderr.read()
        result = res if res else err
        ssh_client.close()
        self.result_queue[hostname].put(result)

    def multi_exec_command(self, host_list, command):
        """多线程并发在多台主机上执行命令.

        :param host_list: must be like [('hostname1',port), ('hostname1',port)]
        :param command: 系统命令，like"ls" "df"...
        """
        threads_list = []
        for host in host_list:
            hostname, port, username = host
            t = threading.Thread(target=self.exec_command,
                                 args=(hostname, port, username, command))
            threads_list.append(t)
            t.start()
        for t in threads_list:
            t.join()

    def show_all_result(self):
        """输出全部命令执行结果."""
        result_list = []
        for hostname in self.result_queue:
            temp = "hostname:{}\n result:\n{}"
            result_info = temp.format(hostname, self.result_queue[
                hostname].get().decode())
            result_list.append(result_info)
        result_info_all = '\n\n'.join(result_list)
        return result_info_all

    def show_result(self, hostlist):
        """输出指定主机的命令执行结果."""
        result_list = []
        for required_hostname in hostlist:
            for hostname in self.result_queue:
                if required_hostname == hostname:
                    temp = "hostname:{}\n result:\n{}"
                    result_info = temp.format(hostname, self.result_queue[
                        hostname].get().decode())
                    result_list.append(result_info)
        result_info_all = '\n\n'.join(result_list)
        return result_info_all

    def transfer_files(self, host_list, trans_type,
                       local_path, remote_path):
        """与指定主机传输文件.

        :param host_list: must be like [('hostname1',port), ('hostname1',port)]
        :param trans_type: 指明上传还是下载，1上传，2下载
        :param local_path: 本地文件路径
        :param remote_path: 远程文件路径
        """
        threads_list = []
        for host in host_list:
            hostname, port, username = host
            if trans_type == "1":
                t = threading.Thread(target=self._put, args=(
                    (hostname, port), username, local_path, remote_path))
                threads_list.append(t)
                t.start()
            elif trans_type == "2":
                t = threading.Thread(target=self._get, args=(
                    (hostname, port), username, local_path, remote_path))
                threads_list.append(t)
                t.start()
        for t in threads_list:
            t.join()

    def _put(self, host, username, local_path, remote_path):
        """在类内部由transfer_files方法调用.

        :param host: 主机地址和端口的列表
        :param local_path: 本地文件路径
        :param remote_path: 远程文件路径
        """
        transfer = paramiko.Transport(host)
        transfer.connect(username=username, pkey=self._private_key)
        sftp = transfer.open_sftp_client()
        sftp.put(localpath=local_path, remotepath=remote_path)
        print("上传成功！")
        sftp.close()

    def _get(self, host, username, local_path, remote_path):
        """在类内部由transfer_files方法调用.

        :param host: 主机地址和端口的列表
        :param local_path: 本地文件路径
        :param remote_path: 远程文件路径
        """
        transfer = paramiko.Transport(host)
        transfer.connect(username=username, pkey=self._private_key)
        sftp = transfer.open_sftp_client()
        sftp.get(remote_path, local_path)
        sftp.close()

    def _json_load_from_file(self):
        """从文件load数据到内存."""
        with open(self._hosts_filepath) as hosts_fp:
            hosts = json.load(hosts_fp)
        return hosts

    def _json_dump_to_file(self, hosts):
        """将内存的数据序列号到文件."""
        with open(self._hosts_filepath, 'w') as hosts_fp:
            json.dump(hosts, hosts_fp, sort_keys=True, ensure_ascii=False)

    def get_host_list(self, hostid_list):
        """返回hostname,port,username的列表.

        param hostid_list: 包含hostid的列表
        """
        hosts = self._json_load_from_file()
        hosts_list = []
        for hostid in hostid_list:
            if hostid in hosts:
                hostname = hosts[hostid]["hostname"]
                port = hosts[hostid]["port"]
                username = hosts[hostid]["username"]
                host_tuple = (hostname, port, username)
                hosts_list.append(host_tuple)
        return hosts_list


class InterActive(object):
    """用户交互类."""

    def __init__(self):
        """实例化一个HostManager."""
        self.manager = HostManager()

    def show_host(self):
        """根据用户输入调用相应的方法."""
        group = None
        query_mode = input('请选择查询方式【1.查询所有主机 2.根据分组查询】').strip()
        if query_mode == "2":
            group = input("请选择要查询的分组")
        self._show_host(query_mode, group)

    def _show_host(self, query_mode, group=None):
        """在类的内部由show_host调用."""
        if query_mode == "1":
            self.manager.show_all_hosts()
        elif query_mode == "2":
            self.manager.show_hosts_by_group(group)

    def _get_host_list(self):
        """在类内部调用，获取主机列表."""
        hostids = input("请输入目标主机的hostid，多个主机用“,”逗号隔开：\n").strip()
        hostid_list = hostids.split(',')
        hosts_list = self.manager.get_host_list(hostid_list)
        return hosts_list

    def exec_command(self):
        """根据用户输入执行命令."""
        hosts_list = self._get_host_list()
        command = input("请输入命令：\n").strip()
        self.manager.multi_exec_command(hosts_list, command)
        is_show_result = input("是否立即查看执行结果：【1.是 2.否】")
        if is_show_result == "1":
            result = self.manager.show_all_result()
            print(result)

    def transfer_files(self):
        """根据用户输入，与指定主机传输文件."""
        hosts_list = self._get_host_list()
        trans_type = input("请选择传输类型【1.上传 2.下载】：\n")
        localpath = input("请输入本地路径：\n").strip()
        remotepath = input("请输入远程路径：\n").strip()
        self.manager.transfer_files(
            hosts_list, trans_type, localpath, remotepath)

    def add_host(self):
        """根据用户输入，添加主机信息.

        hostname, port, username, group, version
        """
        hostname = input("请输入主机IP地址：\n").strip()
        port = input("请输入主机端口：\n").strip()
        username = input("请输入主机用户名：\n").strip()
        group = input("请输入主机组名称（组名为Linux发行版本Ubuntu、centos等）：\n").strip()
        version = input("请输入系统版本：\n").strip()
        self.manager.add_host(hostname, port, username, group, version)

    def remove_host(self):
        """删除主机."""
        hostid = input("请输入要删除的hostid：\n").strip()
        self.manager.remove_host(hostid)

manager = InterActive()
