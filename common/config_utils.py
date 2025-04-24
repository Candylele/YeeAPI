# 配置文件ini中数据的读写方法

import configparser


class ConfigUtils:
    def __init__(self, config_file_path):
        self.cfg_path = config_file_path
        self.cfg = configparser.ConfigParser()
        self.cfg.read(self.cfg_path)

    def read_value(self, section, key):
        value = self.cfg.get(section, key)
        return value

    def write_value(self, section, key, value):
        self.cfg.set(section, key, value)
        config_file_obj = open(self.cfg_path, 'w')
        self.cfg.write(config_file_obj)
        config_file_obj.flush()
        config_file_obj.close()


if __name__ == '__main__':
    config_utils = ConfigUtils('../conf/config.ini')
    print(config_utils.read_value('default', 'HOSTS'))
    config_utils.write_value('default', 'token_value', '888')
    print(config_utils.read_value('default', 'token_value'))
