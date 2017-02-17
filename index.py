"""程序从这里运行."""
from core import hostmanager

hm = hostmanager.HostManager()
hm.show_all_hosts()
host_list = [('192.168.146.132', 22, "zhangyy"),
             ('192.168.146.136', 22, "zhangyy"),
             ('192.168.146.134', 22, "zhangyy"),
             ('192.168.146.133', 22, "zhangyy"),
             ('192.168.146.135', 22, "zhangyy")]
# start = time.time()
# hm.multi_exec_command(host_list, "df")
# print(time.time() - start)
result = hm.show_all_result()
print(result)

hm.transfer_files(host_list, "1", r'e:\python\learning.py',
                  r'from_win.py')
