# 调用ConfigUtils中的方法，直接读取某个数据

import os
from common.config_utils import ConfigUtils


class Config:
    def __init__(self, config_file_path):
        self.cfg_obj = ConfigUtils(config_file_path)

    @property
    def HOSTS(self):
        host_value = self.cfg_obj.read_value('default', 'HOSTS')
        return host_value

    @property
    def TOKEN_VALUE(self):
        token_value = self.cfg_obj.read_value('default', 'TOKEN_VALUE')
        return token_value

    @property
    def REPORT_PATH(self):
        report_path_value = self.cfg_obj.read_value('default', 'report_path')
        return report_path_value

    @property
    def YEEFLOW_HOSTS(self):
        yeeflow_hosts = self.cfg_obj.read_value('default','yeeflow_hosts')
        return yeeflow_hosts

    @property
    def HEADER(self):
        header = self.cfg_obj.read_value('default','header')
        return header

if __name__ == '__main__':
    print(os.path.abspath(__file__))
    print(os.path.dirname(os.path.abspath(__file__)))
    current_path = os.path.dirname(os.path.abspath(__file__))
    config_file_dir = os.path.join(current_path, '..', 'conf', 'config.ini')
    print(config_file_dir)

    local_config = Config(config_file_dir)
    print(local_config.HOSTS)
    print(local_config.TOKEN_VALUE)
    print(local_config.REPORT_PATH)
    print(local_config.YEEFLOW_HOSTS)
