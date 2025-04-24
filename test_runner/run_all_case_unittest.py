import os
import unittest
from common import HTMLTestReportCN
from common.config import Config
from common.log_utils import logger

current_path=os.path.dirname(os.path.abspath(__file__))
case_path=os.path.join(current_path,'..','testcases')

config_file_path=os.path.join(current_path,'..','conf','config.ini')
local_config=Config(config_file_path)
report_dir=os.path.join(current_path,'..',local_config.REPORT_PATH)

logger.info('~~~接口自动化开始~~~')

def loading_testcase():
    logger.info('加载接口接口测试用例')
    discover_obj=unittest.defaultTestLoader.discover(start_dir=case_path,pattern='暂不执行test_api_case.py')
    all_case_suite=unittest.TestSuite()
    all_case_suite.addTest(discover_obj)
    return all_case_suite

result_path_obj=HTMLTestReportCN.ReportDirectory(report_dir)
result_path_obj.create_dir('接口测试报告')
result_html_path=HTMLTestReportCN.GlobalMsg.get_value('report_path')
result_html_obj=open(result_html_path,'wb')
html_runner=HTMLTestReportCN.HTMLTestRunner(stream=result_html_obj,
                                            title='测试报告',
                                            description='关键字驱动框架',
                                            tester='candy')
html_runner.run(loading_testcase())
logger.info('接口自动化测试结束！')