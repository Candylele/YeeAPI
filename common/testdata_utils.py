# 根据读取的Excel数据，判断用例是否执行，并将列表数据转为字典[{},{}] == {"":[],}

import os
from common.excel_utils import ExcelUtils

#excel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","test_data","testcase_infos.xlsx")
excel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","test_data","yeeflow_testcase_infos.xlsx")

class TestdataUtils():
    def __init__(self):
        self.excel_utils = ExcelUtils(excel_path,"Sheet1")

    def convert_testdata_to_dict(self):
        testdata_dict = {}
        for row_data in self.excel_utils.get_excel_data_by_list():
            if row_data["用例执行"] == "是":
                testdata_dict.setdefault(row_data["测试用例编号"],[]).append(row_data)
        return testdata_dict

    def convert_testdata_to_list(self):
        testcase_data = []
        for key,value in self.convert_testdata_to_dict().items():
            temp_dict = {}
            temp_dict['case_id'] = key
            temp_dict['case_step'] = value
            testcase_data.append(temp_dict)
        return testcase_data

if __name__ == '__main__':
    #print(TestdataUtils().convert_testdata_to_dict())
    print(TestdataUtils().convert_testdata_to_list())