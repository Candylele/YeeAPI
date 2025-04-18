import pytest
import allure
from common.requests_utils import RequestsUtils
from common.testdata_utils import TestdataUtils
from common.log_utils import logger

test_case_list = TestdataUtils().convert_testdata_to_list()
case_name_str = ','.join(test_case_list[0].keys())  # 'case_id,case_step'

case_step_infos = []
for case_case in test_case_list:
    case_step_infos.append(tuple(case_case.values()))

@allure.epic('应用列表接口测试')
@allure.feature('这是应用里面列表的增删改查的接口测试')
@allure.title('{case_id}')
@allure.description('用例的预期结果基本为"Status":0')
@pytest.mark.parametrize('case_id,case_step', case_step_infos)
def test_api_case(case_id, case_step):
    logger.info('~~~~~~~~~~~~~~~~~~~~~测试用例[%s---%s]开始执行' % (case_step[0]['测试用例编号'], case_step[0]['测试用例名称']))
    actual_result = RequestsUtils().request_by_step(case_step)
    logger.info(actual_result)
    logger.info('测试用例 [%s--%s] 执行结束~~~~~~~~~~~~~~~~~~~~~~~~' % (case_step[0]['测试用例编号'], case_step[0]['测试用例名称']))
    assert actual_result['check_result']


if __name__ == '__main__':
    pytest.main()
    print('模块test_api_case_by_pytest运行结束')
