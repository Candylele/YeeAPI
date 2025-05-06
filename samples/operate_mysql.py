#数据库封装实现
import pymysql
import json
import logging

# 配置日志
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

class OperateMysql(object):
    def __init__(self):
        self.config = {
            'host': "localhost",
            'user': "root",
            'password': "123456",
            'database': "test",
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor
        }

    def execute_query(self, sql, data=None, is_select=False, fetch_all=False):
        try:
            with pymysql.connect(**self.config) as connection:  #管理数据库连接和游标，确保资源在使用后自动关闭
                with connection.cursor() as cursor:
                    if data:
                        cursor.execute(sql, data)
                    else:
                        cursor.execute(sql)
                    if is_select:
                        if fetch_all:
                            result = cursor.fetchall()
                        else:
                            result = cursor.fetchone()
                        return json.dumps(result, ensure_ascii=False)
                    else:
                        connection.commit()
                        return {'status': 'success', 'message': '操作成功'}
        except Exception as e:
            logging.error(f"执行 SQL 语句时出错: {e}")
            if isinstance(connection, pymysql.connections.Connection):
                connection.rollback()
            return {'status': 'error', 'message': str(e)}

    def select_first_data(self, sql):
        return self.execute_query(sql, is_select=True)

    def select_all_data(self, sql):
        return self.execute_query(sql, is_select=True, fetch_all=True)

    def del_data(self, sql):
        return self.execute_query(sql)

    def update_data(self, sql):
        return self.execute_query(sql)

    def insert_data(self, sql, data):
        return self.execute_query(sql, data)

if __name__ == "__main__":
    om = OperateMysql()
    # 新增
    data = [{'id': 1, 'name': '测试', 'age': 15}, {'id': 2, 'name': '老王', 'age': 10}, {'id': 3, 'name': '李四', 'age': 20}]
    for i in data:
        i_data = (i['id'], i['name'], i['age'])
        insert_res = om.insert_data(
            """
            INSERT INTO test_student (id,name,age) VALUES (%s,%s,%s)
            """, i_data
        )
        print(insert_res)
    # 查询
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
    # 修改
    update_data = om.update_data(
        """
        UPDATE test_student SET name = '王五' WHERE id = 1;
        """
    )
    print(update_data)
    # 删除
    del_data = om.del_data(
        """
        DELETE FROM test_student WHERE id in (1,2,3);
        """
    )
    print(del_data)
