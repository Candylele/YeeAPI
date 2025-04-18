# 不能取名为test_api_unittest_case.py


import unittest
import warnings
import paramunittest
from common.requests_utils import RequestsUtils
from common.testdata_utils import TestdataUtils
from common.log_utils import logger

test_case_lists = TestdataUtils().convert_testdata_to_list()


@paramunittest.parametrized(*test_case_lists)
class TestApiCase(paramunittest.ParametrizedTestCase):
    def setUp(self) -> None:
        warnings.simplefilter('ignore', ResourceWarning)

    def setParameters(self, case_id, case_step):
        self.case_id = case_id
        self.case_step = case_step

    def test_api_case(self):
        logger.info('测试用例[%s--%s]开始执行' % (self.case_step[0]['测试用例编号'], self.case_step[0]['测试用例名称']))
        self._testMethodName = self.case_step[0]['测试用例编号']
        self._testMethodDoc = self.case_step[0]['测试用例名称']
        test_result = RequestsUtils().request_by_step(self.case_step)
        logger.info('测试用例[%s--%s]执行结束' % (self.case_step[0]['测试用例编号'], self.case_step[0]['测试用例名称']))
        self.assertTrue(test_result['check_result'], test_result['message'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
