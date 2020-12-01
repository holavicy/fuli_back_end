import pymssql
import pandas as pd


class LikeModel(object):
    conn_ss = pymssql.connect(host='192.168.40.229:1433', port=3306, user='serverapp', password='wetown2020',
                              database='GiftDB')

    # 新增商品喜欢
    @classmethod
    def create_like(cls, info):
        try:
            cursor = cls.conn_ss.cursor()

            data = {
                'goods_id': info['goodsId'],
                'create_by': info['staffNo']
            }
            base_sql = 'insert into dbo.[like] ({}) values ({})'
            sql_item = []
            sql_values = []

            for key in data:
                sql_item.append(key)
                if isinstance(data[key], str):  # 如果是字符串 加上引号
                    sql_values.append("\'" + data[key] + "\'")
                else:
                    sql_values.append(data[key])

            sql = base_sql.format(','.join(sql_item), ','.join(list(map(str, sql_values))))
            print(sql)

            cursor.execute(sql)
            cls.conn_ss.commit()
            cursor.close()
            return True
        except Exception as e:
            print(e)
            cls.conn_ss.rollback()
            return False
