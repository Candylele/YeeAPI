# 数据库封装实现，该模块用于封装 MySQL 数据库的常用操作
import pymysql  # 导入 pymysql 库，用于连接和操作 MySQL 数据库
import json  # 导入 json 库，用于处理 JSON 数据
import logging  # 导入 logging 库，用于记录错误日志

# 配置日志，设置日志级别为 ERROR，日志格式包含时间、日志级别和具体信息
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

class OperateMysql(object):
    """
    该类用于封装 MySQL 数据库的常见操作，包括查询、插入、更新和删除等
    """
    def __init__(self):
        """
        初始化数据库连接配置。
        定义一个包含数据库连接所需参数的字典，后续用于连接数据库。
        """
        self.config = {
            'host': "localhost",  # 数据库服务器地址
            'user': "root",  # 数据库用户名
            'password': "!QAZ2wsx",  # 数据库密码
            'database': "students",  # 要连接的数据库名
            'charset': 'utf8mb4',  # 字符编码，支持更多字符
            'cursorclass': pymysql.cursors.DictCursor  # 游标类型，返回字典形式的查询结果
        }

    def execute_query(self, sql, data=None, is_select=False, fetch_all=False):
        """
        执行 SQL 查询或修改语句。
        :param sql: 要执行的 SQL 语句
        :param data: 执行 SQL 语句时需要传递的参数，默认为 None
        :param is_select: 是否为查询语句，默认为 False
        :param fetch_all: 是否获取所有查询结果，默认为 False
        :return: 如果是查询语句，返回 JSON 格式的查询结果；否则返回操作状态字典
        """
        try:
            # 使用 with 语句管理数据库连接，确保资源在使用后自动关闭
            with pymysql.connect(**self.config) as connection:
                # 使用 with 语句管理游标，确保游标在使用后自动关闭
                with connection.cursor() as cursor:
                    if data:
                        # 如果有参数，执行带参数的 SQL 语句
                        cursor.execute(sql, data)
                    else:
                        # 执行不带参数的 SQL 语句
                        cursor.execute(sql)
                    if is_select:
                        # 如果是查询语句
                        if fetch_all:
                            # 获取所有查询结果
                            result = cursor.fetchall()
                        else:
                            # 获取第一条查询结果
                            result = cursor.fetchone()
                        # 将查询结果转换为 JSON 字符串，禁用 ASCII 编码
                        return json.dumps(result, ensure_ascii=False)
                    else:
                        # 如果不是查询语句，提交事务
                        connection.commit()
                        return {'status': 'success', 'message': '操作成功'}
        except Exception as e:
            # 记录执行 SQL 语句时的错误信息
            logging.error(f"执行 SQL 语句时出错: {e}")
            if isinstance(connection, pymysql.connections.Connection):
                # 如果发生错误，回滚事务
                connection.rollback()
            return {'status': 'error', 'message': str(e)}

    def select_first_data(self, sql):
        """
        查询第一条数据。
        :param sql: 要执行的查询 SQL 语句
        :return: JSON 格式的第一条查询结果
        """
        return self.execute_query(sql, is_select=True)

    def select_all_data(self, sql):
        """
        查询所有数据。
        :param sql: 要执行的查询 SQL 语句
        :return: JSON 格式的所有查询结果
        """
        return self.execute_query(sql, is_select=True, fetch_all=True)

    def show_all_tables(self):
        """
        查询数据库下的所有表名。
        :return: JSON 格式的所有表名查询结果
        """
        sql = "SHOW TABLES"
        return self.execute_query(sql, is_select=True, fetch_all=True)

    def del_data(self, sql):
        """
        删除数据。
        :param sql: 要执行的删除 SQL 语句
        :return: 操作状态字典
        """
        return self.execute_query(sql)

    def update_data(self, sql):
        """
        修改数据。
        :param sql: 要执行的更新 SQL 语句
        :return: 操作状态字典
        """
        return self.execute_query(sql)

    def insert_data(self, sql, data):
        """
        新增数据。
        :param sql: 要执行的插入 SQL 语句
        :param data: 插入数据时需要传递的参数
        :return: 操作状态字典
        """
        return self.execute_query(sql, data)

if __name__ == "__main__":
    # 创建 OperateMysql 类的实例
    om = OperateMysql()
    # 新增数据
    data = [{'id': 1, 'name': '测试', 'age': 15}, {'id': 2, 'name': '老王', 'age': 10}, {'id': 3, 'name': '李四', 'age': 20}]
    for i in data:
        i_data = (i['id'], i['name'], i['age'])
        insert_res = om.insert_data(
            """INSERT INTO test_student (id,name,age) VALUES (%s,%s,%s)""", i_data
        )
        print(insert_res)
    # 查询数据
    one_data = om.select_first_data(
        """
        SELECT * FROM test_student;
        """
    )
    all_data = om.select_all_data(
        """
        SELECT * FROM test_student;
        """
    )
    print(one_data)
    print("查询总数据: %s, 分别是: %s" % (len(json.loads(all_data)), all_data))
    # 修改数据
    update_data = om.update_data(
        """
        UPDATE test_student SET name = '王五' WHERE id = 1;
        """
    )
    print(update_data)
    # 删除数据
    del_data = om.del_data(
        """
        DELETE FROM test_student WHERE id in (1,2,3);
        """
    )
    print(del_data)