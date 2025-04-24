import os
import json
import re
import jsonpath
import requests
import allure
from common.config import Config
from common.check_utils import CheckUtils
from common.log_utils import logger
from requests.exceptions import ProxyError, ConnectionError, RequestException

conf_file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'conf', 'config.ini')


class RequestsUtils:
    def __init__(self):
        self.session = requests.session()
        self.hosts = Config(conf_file_path).HOSTS
        self.header = Config(conf_file_path).HEADER
        self.tmp_variables = {}

    # def request_by_step(self, test_steps):
    #     for test_step in test_steps:
    #         step_description = '测试步骤[%s]开始执行' % test_step['用例步骤']
    #         with allure.step(step_description):
    #             logger.info(step_description)
    #             result = self.request(test_step)
    #         # 将日志记录放在with语句块外部
    #         logger.info('~~~测试步骤[%s]执行结束~~~' % test_step['用例步骤'])
    #         if result['code'] != 0:
    #             break
    #     return result
    #
    # def request(self, step_info):
    #     request_type = step_info['请求方式']
    #     if request_type == 'get':
    #         result = self.__get(step_info)
    #     elif request_type == 'post':
    #         result = self.__post(step_info)
    #     elif request_type == 'delete':
    #         result = self.__delete(step_info)
    #     elif request_type == 'put':
    #         result = self.__put(step_info)
    #     else:
    #         result = {'code': 1, 'message': '%s请求方式不支持' % request_type, 'check_result': False}
    #     return result

    # def request_by_step(self, test_steps):
    #     for test_step in test_steps:
    #         step_description = '测试步骤[%s]开始执行' % test_step['用例步骤']
    #         with allure.step(step_description):
    #             logger.info(step_description)
    #             result = self.handle_request(test_step)  # 调用新处理函数
    #         logger.info('~~~测试步骤[%s]执行结束~~~' % test_step['用例步骤'])
    #         if result['code'] != 0:
    #             break
    #     return result

    def request_by_step(self, test_steps):
        for test_step in test_steps:
            step_description = '测试步骤[%s]开始执行' % test_step['用例步骤']
            with allure.step(step_description):
                logger.info(step_description)
                result = self.handle_request(test_step)  # 调用新处理函数
            # 添加条件检查来确保 result 不是 None
            if result is not None:
                logger.info('~~~测试步骤[%s]执行结束~~~' % test_step['用例步骤'])
                if result['code'] != 0:
                    break
            else:
                # 处理 result 为 None 的情况
                logger.error('测试步骤[%s]执行失败，因为返回结果为 None' % test_step['用例步骤'])
                result = {'code': 3, 'message': '未知错误导致返回结果为 None', 'check_result': False}
                break  #或者根据需求决定是否中断循环
        return result  #为none时没有返回值

    def handle_request(self, step_info):  #新处理函数
        request_type = step_info['请求方式']
        result = None
        try:
            if request_type == 'get':
                result = self.__get(step_info)
            elif request_type == 'post':
                result = self.__post(step_info)
            elif request_type == 'delete':
                result = self.__delete(step_info)
            elif request_type == 'put':
                result = self.__put(step_info)
            # 可以继续添加其他请求方式的处理
            else:
                result = {'code': 1, 'message': '%s请求方式不支持' % request_type, 'check_result': False}
        except ProxyError as e:
            result = self.handle_exception('调用接口时发生代理异常', e, step_info)
        except ConnectionError as e:
            result = self.handle_exception('调用接口时发生连接异常', e, step_info)
        except RequestException as e:
            result = self.handle_exception('调用接口时发生请求异常', e, step_info)
        except Exception as e:
            result = self.handle_exception('调用接口时发生未知异常', e, step_info)
        return result

    def handle_exception(self, message_prefix, e, step_info):  # 异常处理函数
        error_message = f"{message_prefix}，异常原因：{e.__str__()}"
        logger.error(error_message)
        return {'code': 3, 'message': f'调用接口[{step_info["接口名称"]}]时{error_message}', 'check_result': False}

    def __get(self, request_info):
        logger.info('接口[%s]开始调用' % request_info['接口名称'])
        # 构造URL模板
        url_template = 'https://%s%s' % (self.hosts, request_info['请求地址'])
        print('这是URL模板：%s' % url_template)
        # 使用正则表达式查找URL模板中的变量，并进行替换
        variable_pattern = re.compile(r'\${\w+}')

        def replace_variable(match):
            variable_name = match.group()[2:-1]  # 提取变量名，去掉${}
            return self.tmp_variables.get(variable_name, match.group())  # 用tmp_variables中的值替换，如果没有则保留原变量

        url = variable_pattern.sub(replace_variable, url_template)
        print('这是替换后的URL：%s' % url)

        variable_list = re.findall('\\${\w+}', request_info['请求参数(get)'])
        for variable in variable_list:
            request_info['请求参数(get)'] = request_info['请求参数(get)'].replace(variable, self.tmp_variables[
                variable[2:-1]])

        params = json.loads(request_info['请求参数(get)']) if request_info['请求参数(get)'] else None
        # headers = json.loads(request_info['请求头部信息']) if request_info['请求头部信息'] else None
        headers = json.loads(self.header)
        response = self.session.get(url=url, params=params, headers=headers, timeout=(3, 5)) #设置连接超时时间为3秒，读取超时时间为5秒
        logger.info('接口响应结果：%s' % response.json())

        if request_info['取值方式'] == '正则取值':
            value = re.findall(request_info['取值代码'], response.text)[0]
            self.tmp_variables[request_info['取值变量']] = value
            print("这是正则表达式取到的值：%s" % value)

        elif request_info['取值方式'] == 'jsonpath取值':
            value = jsonpath.jsonpath(response.json(), request_info['取值代码'])[0]
            self.tmp_variables[request_info['取值变量']] = value
            print("这是jsonpath取到的值：%s" % value)
        print("这是tmp_variables结果: %s" % self.tmp_variables)

        result = CheckUtils(response).run_check(request_info['断言类型'], request_info['期望结果'])
        logger.info('接口[%s]调用完成' % request_info['接口名称'])
        print('断言结果：%s' % result['message'])
        print(result)
        return result

        # try:
        #     # 构造URL模板
        #     url_template = 'https://%s%s' % (self.hosts, request_info['请求地址'])
        #     print('这是URL模板：%s' % url_template)
        #     # 使用正则表达式查找URL模板中的变量，并进行替换
        #     variable_pattern = re.compile(r'\${\w+}')
        #     def replace_variable(match):
        #         variable_name = match.group()[2:-1]  # 提取变量名，去掉${}
        #         return self.tmp_variables.get(variable_name, match.group())  # 用tmp_variables中的值替换，如果没有则保留原变量
        #     url = variable_pattern.sub(replace_variable, url_template)
        #     print('这是替换后的URL：%s' % url)
        #
        #
        #     variable_list = re.findall('\\${\w+}', request_info['请求参数(get)'])
        #     for variable in variable_list:
        #         request_info['请求参数(get)'] = request_info['请求参数(get)'].replace(variable, self.tmp_variables[
        #             variable[2:-1]])
        #
        #     # 发送GET请求
        #     params = json.loads(request_info['请求参数(get)']) if request_info['请求参数(get)'] else None
        #     #headers = json.loads(request_info['请求头部信息']) if request_info['请求头部信息'] else None
        #     headers = json.loads(self.header)
        #     response = self.session.get(url=url, params=params, headers=headers)
        #     logger.info('接口响应结果：%s' % response.json())
        #
        #     # headers = {
        #     #     'apiKey': '176db230-d76c-474f-a288-da5a0e3a8d4a',  # 替换为你的实际API密钥
        #     #     'Content-Type': 'application/json'  # 根据需要设置其他头部信息，例如内容类型
        #     # }
        #     # url = 'https://uat.yeeflow.cn/openapi/v1/lists/30/1818904734567501824/fields'
        #     # response = self.session.get(url=url,
        #     #                             headers=headers)
        #     #print('接口响应结果：%s'%response.json())
        #
        #
        #     if request_info['取值方式'] == '正则取值':
        #         value = re.findall(request_info['取值代码'], response.text)[0]
        #         self.tmp_variables[request_info['取值变量']] = value
        #         print("这是正则表达式取到的值：%s" % value)
        #
        #     elif request_info['取值方式'] == 'jsonpath取值':
        #         value = jsonpath.jsonpath(response.json(), request_info['取值代码'])[0]
        #         self.tmp_variables[request_info['取值变量']] = value
        #         print("这是jsonpath取到的值：%s" % value)
        #     print("这是tmp_variables结果: %s" % self.tmp_variables)
        #
        #     result = CheckUtils(response).run_check(request_info['断言类型'], request_info['期望结果'])
        #     logger.info('接口[%s]调用完成' % request_info['接口名称'])
        #     print('断言结果：%s'%result['message'])
        #
        # except ProxyError as e:
        #     result = {'code': 3,
        #               'message': '调用接口[%s]时发生代理异常，异常原因：%s' % (request_info['接口名称'], e.__str__()),
        #               'check_result': False}
        #     logger.error(result['message'])
        # except ConnectionError as e:
        #     result = {'code': 3,
        #               'message': '调用接口[%s]时发生链接异常，异常原因：%s' % (request_info['接口名称'], e.__str__()),
        #               'check_result': False}
        #     logger.error(result['message'])
        # except RequestException as e:
        #     result = {'code': 3,
        #               'message': '调用接口[%s]时发生请求异常，异常原因：%s' % (request_info['接口名称'], e.__str__()),
        #               'check_result': False}
        #     logger.error(result['message'])
        # except Exception as e:
        #     result = {'code': 3,
        #               'message': '调用接口[%s]时发生请求异常，异常原因：%s' % (request_info['接口名称'], e.__str__()),
        #               'check_result': False}
        #     logger.error(result['message'])
        # return result

    def __post(self, request_info):
        logger.info('接口[%s]开始调用' % request_info['接口名称'])
        # 构造URL模板
        url_template = 'https://%s%s' % (self.hosts, request_info['请求地址'])
        # print('这是URL模板：%s' % url_template)
        # 使用正则表达式查找URL模板中的变量，并进行替换
        variable_pattern = re.compile(r'\${\w+}')

        def replace_variable(match):
            variable_name = match.group()[2:-1]  # 提取变量名，去掉${}
            return self.tmp_variables.get(variable_name, match.group())  # 用tmp_variables中的值替换，如果没有则保留原变量

        url = variable_pattern.sub(replace_variable, url_template)
        print('这是替换后的URL：%s' % url)

        get_veriable_list = re.findall('\\${\w+}', request_info['请求参数(get)'])
        for variable in get_veriable_list:
            request_info['请求参数(get)'] = request_info['请求参数(get)'].replace(variable, self.tmp_variables[
                variable[2:-1]])

        post_variable_list = re.findall('\\${\w+}', request_info['请求参数(post)'])
        for variable in post_variable_list:
            request_info['请求参数(post)'] = request_info['请求参数(post)'].replace(variable, self.tmp_variables[
                variable[2:-1]])

        params = json.loads(request_info['请求参数(get)']) if request_info['请求参数(get)'] else None
        # headers = json.loads(request_info['请求头部信息']) if request_info['请求头部信息'] else None
        headers = json.loads(self.header)
        body = json.loads(request_info['请求参数(post)']) if request_info['请求参数(post)'] else None
        response = self.session.post(url=url, params=params, headers=headers, json=body, timeout=(3, 5)) #连接超时3秒，读取超时5秒
        # print('接口响应结果：%s'%response.json())
        logger.info('接口响应结果：%s' % response.json())

        if request_info['取值方式'] == '正则取值':
            value = re.findall(request_info['取值代码'], response.text)[0]
            print("这是正则表达式取到的值：%s" % value)
            self.tmp_variables[request_info['取值变量']] = value

        elif request_info['取值方式'] == 'jsonpath取值':
            value = jsonpath.jsonpath(response.json(), request_info['取值代码'])[0]
            print("这是jsonpath取到的值：%s" % value)
            self.tmp_variables[request_info['取值变量']] = value
        print("这是tmp_variables结果: %s" % self.tmp_variables)

        result = CheckUtils(response).run_check(request_info['断言类型'], request_info['期望结果'])
        logger.info('接口[%s]调用完成' % request_info['接口名称'])
        print('断言结果：%s' % result['message'])
        print(result)
        return result


        # try:
        #     # 构造URL模板
        #     url_template = 'https://%s%s' % (self.hosts, request_info['请求地址'])
        #     #print('这是URL模板：%s' % url_template)
        #     # 使用正则表达式查找URL模板中的变量，并进行替换
        #     variable_pattern = re.compile(r'\${\w+}')
        #     def replace_variable(match):
        #         variable_name = match.group()[2:-1]  # 提取变量名，去掉${}
        #         return self.tmp_variables.get(variable_name, match.group())  # 用tmp_variables中的值替换，如果没有则保留原变量
        #     url = variable_pattern.sub(replace_variable, url_template)
        #     print('这是替换后的URL：%s' % url)
        #
        #     get_veriable_list = re.findall('\\${\w+}', request_info['请求参数(get)'])
        #     for variable in get_veriable_list:
        #         request_info['请求参数(get)'] = request_info['请求参数(get)'].replace(variable, self.tmp_variables[
        #             variable[2:-1]])
        #
        #     post_variable_list = re.findall('\\${\w+}', request_info['请求参数(post)'])
        #     for variable in post_variable_list:
        #         request_info['请求参数(post)'] = request_info['请求参数(post)'].replace(variable, self.tmp_variables[
        #             variable[2:-1]])
        #
        #     params = json.loads(request_info['请求参数(get)']) if request_info['请求参数(get)'] else None
        #     #headers = json.loads(request_info['请求头部信息']) if request_info['请求头部信息'] else None
        #     headers = json.loads(self.header)
        #     body = json.loads(request_info['请求参数(post)']) if request_info['请求参数(post)'] else None
        #     response = self.session.post(url=url,params=params,headers=headers,json=body)
        #     #print('接口响应结果：%s'%response.json())
        #     logger.info('接口响应结果：%s'%response.json())
        #
        #     if request_info['取值方式'] == '正则取值':
        #         value = re.findall(request_info['取值代码'], response.text)[0]
        #         print("这是正则表达式取到的值：%s" % value)
        #         self.tmp_variables[request_info['取值变量']] = value
        #
        #     elif request_info['取值方式'] == 'jsonpath取值':
        #         value = jsonpath.jsonpath(response.json(), request_info['取值代码'])[0]
        #         print("这是jsonpath取到的值：%s" % value)
        #         self.tmp_variables[request_info['取值变量']] = value
        #     print("这是tmp_variables结果: %s" % self.tmp_variables)
        #
        #
        #     result = CheckUtils(response).run_check(request_info['断言类型'], request_info['期望结果'])
        #     logger.info('接口[%s]调用完成' % request_info['接口名称'])
        #     print('断言结果：%s'%result['message'])
        #
        # except ProxyError as e:
        #     result = {'code': 3,
        #               'message': '调用接口[%s]时发生代理异常，异常原因：%s' % (request_info['接口名称'], str(e)),
        #               'check_result': False}
        #     logger.error(result['message'])
        # except ConnectionError as e:
        #     result = {'code': 3,
        #               'message': '调用接口[%s]时发生链接异常，异常原因：%s' % (request_info['接口名称'], str(e)),
        #               'check_result': False}
        #     logger.error(result['message'])
        # except RequestException as e:
        #     result = {'code': 3,
        #               'message': '调用接口[%s]时发生请求异常，异常原因：%s' % (request_info['接口名称'], str(e)),
        #               'check_result': False}
        #     logger.error(result['message'])
        # except Exception as e:
        #     result = {'code': 3,
        #               'message': '调用接口[%s]时发生系统异常，异常原因：%s' % (request_info['接口名称'], str(e)),
        #               'check_result': False}
        #     logger.error(result['message'])
        # return result

    def __delete(self, request_info):
        logger.info('接口[%s]开始调用' % request_info['接口名称'])
        # 构造URL模板
        url_template = 'https://%s%s' % (self.hosts, request_info['请求地址'])
        print('这是URL模板：%s' % url_template)
        # 使用正则表达式查找URL模板中的变量，并进行替换
        variable_pattern = re.compile(r'\${\w+}')

        def replace_variable(match):
            variable_name = match.group()[2:-1]  # 提取变量名，去掉${}
            return self.tmp_variables.get(variable_name, match.group())  # 用tmp_variables中的值替换，如果没有则保留原变量

        url = variable_pattern.sub(replace_variable, url_template)
        print('这是替换后的URL：%s' % url)

        variable_list = re.findall('\\${\w+}', request_info['请求参数(get)'])
        for variable in variable_list:
            request_info['请求参数(get)'] = request_info['请求参数(get)'].replace(variable, self.tmp_variables[
                variable[2:-1]])

        # 发送delete请求
        params = json.loads(request_info['请求参数(get)']) if request_info['请求参数(get)'] else None
        # headers = json.loads(request_info['请求头部信息']) if request_info['请求头部信息'] else None
        headers = json.loads(self.header)
        response = self.session.delete(url=url, params=params, headers=headers, timeout=(3, 5)) #连接超时3秒，读取超时5秒
        logger.info('接口响应结果：%s' % response.json())

        if request_info['取值方式'] == '正则取值':
            value = re.findall(request_info['取值代码'], response.text)[0]
            self.tmp_variables[request_info['取值变量']] = value
            print("这是正则表达式取到的值：%s" % value)

        elif request_info['取值方式'] == 'jsonpath取值':
            value = jsonpath.jsonpath(response.json(), request_info['取值代码'])[0]
            self.tmp_variables[request_info['取值变量']] = value
            print("这是jsonpath取到的值：%s" % value)
        print("这是tmp_variables结果: %s" % self.tmp_variables)

        result = CheckUtils(response).run_check(request_info['断言类型'], request_info['期望结果'])
        logger.info('接口[%s]调用完成' % request_info['接口名称'])
        print('断言结果：%s' % result['message'])
        print(result)
        return result


        # try:
        #     # 构造URL模板
        #     url_template = 'https://%s%s' % (self.hosts, request_info['请求地址'])
        #     print('这是URL模板：%s' % url_template)
        #     # 使用正则表达式查找URL模板中的变量，并进行替换
        #     variable_pattern = re.compile(r'\${\w+}')
        #     def replace_variable(match):
        #         variable_name = match.group()[2:-1]  # 提取变量名，去掉${}
        #         return self.tmp_variables.get(variable_name, match.group())  # 用tmp_variables中的值替换，如果没有则保留原变量
        #     url = variable_pattern.sub(replace_variable, url_template)
        #     print('这是替换后的URL：%s' % url)
        #
        #
        #     variable_list = re.findall('\\${\w+}', request_info['请求参数(get)'])
        #     for variable in variable_list:
        #         request_info['请求参数(get)'] = request_info['请求参数(get)'].replace(variable, self.tmp_variables[
        #             variable[2:-1]])
        #
        #     # 发送GET请求
        #     params = json.loads(request_info['请求参数(get)']) if request_info['请求参数(get)'] else None
        #     #headers = json.loads(request_info['请求头部信息']) if request_info['请求头部信息'] else None
        #     headers = json.loads(self.header)
        #     response = self.session.delete(url=url, params=params, headers=headers)
        #     logger.info('接口响应结果：%s' % response.json())
        #
        #     if request_info['取值方式'] == '正则取值':
        #         value = re.findall(request_info['取值代码'], response.text)[0]
        #         self.tmp_variables[request_info['取值变量']] = value
        #         print("这是正则表达式取到的值：%s" % value)
        #
        #     elif request_info['取值方式'] == 'jsonpath取值':
        #         value = jsonpath.jsonpath(response.json(), request_info['取值代码'])[0]
        #         self.tmp_variables[request_info['取值变量']] = value
        #         print("这是jsonpath取到的值：%s" % value)
        #     print("这是tmp_variables结果: %s" % self.tmp_variables)
        #
        #     result = CheckUtils(response).run_check(request_info['断言类型'], request_info['期望结果'])
        #     logger.info('接口[%s]调用完成' % request_info['接口名称'])
        #     print('断言结果：%s'%result['message'])
        #
        # except ProxyError as e:
        #     result = {'code': 3,
        #               'message': '调用接口[%s]时发生代理异常，异常原因：%s' % (request_info['接口名称'], e.__str__()),
        #               'check_result': False}
        #     logger.error(result['message'])
        # except ConnectionError as e:
        #     result = {'code': 3,
        #               'message': '调用接口[%s]时发生链接异常，异常原因：%s' % (request_info['接口名称'], e.__str__()),
        #               'check_result': False}
        #     logger.error(result['message'])
        # except RequestException as e:
        #     result = {'code': 3,
        #               'message': '调用接口[%s]时发生请求异常，异常原因：%s' % (request_info['接口名称'], e.__str__()),
        #               'check_result': False}
        #     logger.error(result['message'])
        # except Exception as e:
        #     result = {'code': 3,
        #               'message': '调用接口[%s]时发生请求异常，异常原因：%s' % (request_info['接口名称'], e.__str__()),
        #               'check_result': False}
        #     logger.error(result['message'])
        # return result

    def __put(self, request_info):
        logger.info('接口[%s]开始调用' % request_info['接口名称'])
        # 构造URL模板
        url_template = 'https://%s%s' % (self.hosts, request_info['请求地址'])
        # print('这是URL模板：%s' % url_template)
        # 使用正则表达式查找URL模板中的变量，并进行替换
        variable_pattern = re.compile(r'\${\w+}')

        def replace_variable(match):
            variable_name = match.group()[2:-1]  # 提取变量名，去掉${}
            return self.tmp_variables.get(variable_name, match.group())  # 用tmp_variables中的值替换，如果没有则保留原变量

        url = variable_pattern.sub(replace_variable, url_template)
        print('这是替换后的URL：%s' % url)

        get_veriable_list = re.findall('\\${\w+}', request_info['请求参数(get)'])
        for variable in get_veriable_list:
            request_info['请求参数(get)'] = request_info['请求参数(get)'].replace(variable, self.tmp_variables[
                variable[2:-1]])

        post_variable_list = re.findall('\\${\w+}', request_info['请求参数(post)'])
        for variable in post_variable_list:
            request_info['请求参数(post)'] = request_info['请求参数(post)'].replace(variable, self.tmp_variables[
                variable[2:-1]])

        params = json.loads(request_info['请求参数(get)']) if request_info['请求参数(get)'] else None
        # headers = json.loads(request_info['请求头部信息']) if request_info['请求头部信息'] else None
        headers = json.loads(self.header)
        body = json.loads(request_info['请求参数(post)']) if request_info['请求参数(post)'] else None
        response = self.session.put(url=url, params=params, headers=headers, json=body, timeout=(3, 5)) #连接超时3秒，读取超时5秒
        # print('接口响应结果：%s'%response.json())
        logger.info('接口响应结果：%s' % response.json())

        if request_info['取值方式'] == '正则取值':
            value = re.findall(request_info['取值代码'], response.text)[0]
            print("这是正则表达式取到的值：%s" % value)
            self.tmp_variables[request_info['取值变量']] = value

        elif request_info['取值方式'] == 'jsonpath取值':
            value = jsonpath.jsonpath(response.json(), request_info['取值代码'])[0]
            print("这是jsonpath取到的值：%s" % value)
            self.tmp_variables[request_info['取值变量']] = value
        print("这是tmp_variables结果: %s" % self.tmp_variables)

        result = CheckUtils(response).run_check(request_info['断言类型'], request_info['期望结果'])
        logger.info('接口[%s]调用完成' % request_info['接口名称'])
        print('断言结果：%s' % result['message'])
        print(result)
        return result


        # try:
        #     # 构造URL模板
        #     url_template = 'https://%s%s' % (self.hosts, request_info['请求地址'])
        #     #print('这是URL模板：%s' % url_template)
        #     # 使用正则表达式查找URL模板中的变量，并进行替换
        #     variable_pattern = re.compile(r'\${\w+}')
        #     def replace_variable(match):
        #         variable_name = match.group()[2:-1]  # 提取变量名，去掉${}
        #         return self.tmp_variables.get(variable_name, match.group())  # 用tmp_variables中的值替换，如果没有则保留原变量
        #     url = variable_pattern.sub(replace_variable, url_template)
        #     print('这是替换后的URL：%s' % url)
        #
        #     get_veriable_list = re.findall('\\${\w+}', request_info['请求参数(get)'])
        #     for variable in get_veriable_list:
        #         request_info['请求参数(get)'] = request_info['请求参数(get)'].replace(variable, self.tmp_variables[
        #             variable[2:-1]])
        #
        #     post_variable_list = re.findall('\\${\w+}', request_info['请求参数(post)'])
        #     for variable in post_variable_list:
        #         request_info['请求参数(post)'] = request_info['请求参数(post)'].replace(variable, self.tmp_variables[
        #             variable[2:-1]])
        #
        #     params = json.loads(request_info['请求参数(get)']) if request_info['请求参数(get)'] else None
        #     #headers = json.loads(request_info['请求头部信息']) if request_info['请求头部信息'] else None
        #     headers = json.loads(self.header)
        #     body = json.loads(request_info['请求参数(post)']) if request_info['请求参数(post)'] else None
        #     response = self.session.put(url=url,params=params,headers=headers,json=body)
        #     #print('接口响应结果：%s'%response.json())
        #     logger.info('接口响应结果：%s'%response.json())
        #
        #     if request_info['取值方式'] == '正则取值':
        #         value = re.findall(request_info['取值代码'], response.text)[0]
        #         print("这是正则表达式取到的值：%s" % value)
        #         self.tmp_variables[request_info['取值变量']] = value
        #
        #     elif request_info['取值方式'] == 'jsonpath取值':
        #         value = jsonpath.jsonpath(response.json(), request_info['取值代码'])[0]
        #         print("这是jsonpath取到的值：%s" % value)
        #         self.tmp_variables[request_info['取值变量']] = value
        #     print("这是tmp_variables结果: %s" % self.tmp_variables)
        #
        #
        #     result = CheckUtils(response).run_check(request_info['断言类型'], request_info['期望结果'])
        #     logger.info('接口[%s]调用完成' % request_info['接口名称'])
        #     print('断言结果：%s'%result['message'])
        #
        # except ProxyError as e:
        #     result = {'code': 3,
        #               'message': '调用接口[%s]时发生代理异常，异常原因：%s' % (request_info['接口名称'], str(e)),
        #               'check_result': False}
        #     logger.error(result['message'])
        # except ConnectionError as e:
        #     result = {'code': 3,
        #               'message': '调用接口[%s]时发生链接异常，异常原因：%s' % (request_info['接口名称'], str(e)),
        #               'check_result': False}
        #     logger.error(result['message'])
        # except RequestException as e:
        #     result = {'code': 3,
        #               'message': '调用接口[%s]时发生请求异常，异常原因：%s' % (request_info['接口名称'], str(e)),
        #               'check_result': False}
        #     logger.error(result['message'])
        # except Exception as e:
        #     result = {'code': 3,
        #               'message': '调用接口[%s]时发生系统异常，异常原因：%s' % (request_info['接口名称'], str(e)),
        #               'check_result': False}
        #     logger.error(result['message'])
        # return result

if __name__ == '__main__':
    # request_info = {'测试用例编号': 'api_case_01', '测试用例名称': '获取列表字段明细测试', '用例执行': '是',
    #                 '用例步骤': 'step_01',
    #                 '接口名称': '获取列表字段明细', '请求方式': 'get',
    #                 '请求头部信息': '{"apiKey":"176db230-d76c-474f-a288-da5a0e3a8d4a","Content-Type": "application/json"}',
    #                 '请求地址': '/lists/30/1818904734567501824/fields',
    #                 '请求参数(get)': '',
    #                 '请求参数(post)': '',
    #                 '取值方式': 'jsonpath取值', '取值代码': '$.Data[*].FieldName', '取值变量': 'id', '断言类型': 'body_regexp',
    #                 '期望结果': '"Status":0'}
    # r = RequestsUtils()
    # result = r.request(request_info)
    # print("用例执行结果：%s"%result)

    case_info = [{
        '测试用例编号': 'api_case_03',
        '测试用例名称': '列表新增数据后查看详情再删除',
        '用例执行': '是',
        '用例步骤': 'step_01',
        '接口名称': '新增数据',
        '请求方式': 'post',
        '请求头部信息': '{"apiKey":"176db230-d76c-474f-a288-da5a0e3a8d4a"}',
        '请求地址': '/lists/30/1818904734567501824/items',
        '请求参数(get)': '{"columnType":"0"}',
        '请求参数(post)': '{"Data": {"Title": "接口新增测试1","Text1": "动空只观论。","Text2": "你要门。","Decimal1": "1"}}',
        '取值方式': 'jsonpath取值',
        '取值代码': '$.Data',
        '取值变量': 'id',
        '断言类型': 'body_regexp',
        '期望结果': '"Status":0'
    }, {
        '测试用例编号': 'api_case_03',
        '测试用例名称': '列表新增数据后查看详情再删除',
        '用例执行': '是',
        '用例步骤': 'step_02',
        '接口名称': '查看数据',
        '请求方式': 'get',
        '请求头部信息': '{"apiKey":"176db230-d76c-474f-a288-da5a0e3a8d4a"}',
        '请求地址': '/lists/30/1818904734567501824/items/${id}',
        '请求参数(get)': '{"fields":"Title,Decimal1,Text1,Text2"}',
        '请求参数(post)': '',
        '取值方式': '无',
        '取值代码': '',
        '取值变量': '',
        '断言类型': 'body_regexp',
        '期望结果': '"Status":0'
    }]
    r = RequestsUtils()
    result = r.request_by_step(case_info)
    print(result)
    print(result['check_result'])

    # 俩个步骤的接口用例，先获取access_token再创建标签
    # case_info = [
    #     {'测试用例编号': 'api_case_02', '测试用例名称': '创建标签接口测试', '用例执行': '是', '用例步骤': 'step_01',
    #      '接口名称': '获取access_token接口', '请求方式': 'get', '请求头部信息': '', '请求地址': '/cgi-bin/token',
    #      '请求参数(get)': '{"grant_type":"client_credential","appid":"wx55614004f367f8ca","secret":"65515b46dd758dfdb09420bb7db2c67f"}',
    #      '请求参数(post)': '',
    #      '取值方式': '正则取值', '取值代码': '"access_token":"(.+?)"', '取值变量': 'token',
    #      '断言类型': 'json_key_value', '期望结果': '{"expires_in":7200}'},
    #     {'测试用例编号': 'api_case_02', '测试用例名称': '创建标签接口测试', '用例执行': '否', '用例步骤': 'step_02',
    #      '接口名称': '创建标签接口', '请求方式': 'post', '请求头部信息': '', '请求地址': '/cgi-bin/tags/create',
    #      '请求参数(get)': '{"access_token":"${token}"}',
    #      '请求参数(post)': '{   "tag" : {     "name" : "P5P6new01" } } ',
    #      '取值方式': '无', '取值代码': '', '取值变量': '',
    #      '断言类型': 'json_key', '期望结果': 'tag'}
    # ]
    # r = RequestsUtils()
    # result = r.request_by_step(case_info)  # request_by_step-->request-->__get或__post

    # case_info= [
    #     {'测试用例编号': 'api_case_01', '测试用例名称': '获取列表字段明细测试', '用例执行': '是', '用例步骤': 'step_01',
    #      '接口名称': '获取列表字段明细', '请求方式': 'get',
    #      '请求头部信息': '{"apiKey":"176db230-d76c-474f-a288-da5a0e3a8d4a","Content-Type": "application/json"}',
    #      '请求地址': '/openapi/v1/lists/30/1818904734567501824/fields', '请求参数(get)': '', '请求参数(post)': '',
    #      '取值方式': '无', '取值代码': '', '取值变量': '', '断言类型': 'body_regexp', '期望结果': '"Status":0'}]
    # r = RequestsUtils()
    # result = r.request_by_step(case_info)

    # request_info = {'测试用例编号': 'api_case_02', '测试用例名称': '创建标签接口测试', '用例执行': '是', '用例步骤': 'step_01',
    #          '接口名称': '获取access_token接口', '请求方式': 'get', '请求头部信息': '', '请求地址': '/cgi-bin/token',
    #          '请求参数(get)': '{"grant_type":"client_credential","appid":"wx55614004f367f8ca","secret":"65515b46dd758dfdb09420bb7db2c67f"}',
    #          '请求参数(post)': '',
    #          '取值方式': '正则取值', '取值代码': '"access_token":"(.+?)"', '取值变量': 'token',
    #          '断言类型': 'none', '期望结果': ''}
    # r = RequestsUtils()
    # result = r.request(request_info)
    # print(result)
    # #print(type(result))
    # print(result['response_body'])
    # print(result.get('message'))

    # request_info = {'测试用例编号': 'api_case_02', '测试用例名称': '创建标签接口测试', '用例执行': '否', '用例步骤': 'step_02',
    #               '接口名称': '创建标签接口', '请求方式': 'post', '请求头部信息': '', '请求地址': '/cgi-bin/tags/create',
    #               '请求参数(get)': '{"access_token":"${token}"}',
    #               '请求参数(post)': '{   "tag" : {     "name" : "P5P6new01" } } ',
    #               '取值方式': '无', '取值代码': '', '取值变量': '',
    #               '断言类型': 'json_key', '期望结果': 'tag'}
    # print(request_info['请求参数(get)'])
    # get_variable_list = re.findall('\\${\w+}', request_info['请求参数(get)'])
    # print("@@@这是variable_list: %s" % get_variable_list)
    # print(request_info['请求参数(post)'])
    # post_variable_list = re.findall('\\${\w+}', request_info['请求参数(post)'])
    # print("~~~这是variable_list: %s" % post_variable_list)

    # request_info = {'测试用例编号': 'api_case_01', '测试用例名称': '获取access_token接口测试', '用例执行': '是','用例步骤': 'step_01',
    #                 '接口名称': '获取access_token接口',
    #                 '请求方式': 'get',
    #                 '请求头部信息': '','请求地址': '/cgi-bin/token',
    #                 '请求参数(get)': '{"grant_type":"client_credential","appid":"wx55614004f367f8ca","secret":"65515b46dd758dfdb09420bb7db2c67f"}',
    #                 '请求参数(post)': '', '取值方式': 'jsonpath取值', '取值代码': '$.access_token','取值变量': 'token_value',
    #                 '断言类型': 'none', '期望结果': '"access_token":"(.+?)"'}


