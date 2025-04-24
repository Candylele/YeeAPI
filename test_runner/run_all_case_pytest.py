import os
import shutil
import pytest

current_path=os.path.dirname(os.path.abspath(__file__))
case_path=os.path.join(current_path,'..','testcases')
json_report_path=os.path.join(current_path,'..','pytest_report','json_report')
html_report_path=os.path.join(current_path,'..','pytest_report','html_report')

if os.path.isdir(json_report_path):
    shutil.rmtree(json_report_path)
os.mkdir(json_report_path)

pytest.main([case_path,'--alluredir=%s'%json_report_path])
os.system('allure generate %s -o %s --clean'%(json_report_path,html_report_path))
print('模块run_all_case_pytest运行结束')