import pymssql
import pandas as pd
from common.tool import format_sql_values


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
                'create_by': info['staffNo'],
                'create_by_name': info['creatorName']
            }
            base_sql = 'insert into dbo.[like] ({}) values ({})'
            sql_item, sql_values = format_sql_values(data)
            sql = base_sql.format(','.join(sql_item), ','.join(list(map(str, sql_values))))

            cursor.execute(sql)
            cls.conn_ss.commit()
            cursor.close()
            return True
        except Exception as e:
            print(e)
            cls.conn_ss.rollback()
            return False

    # 获取喜欢列表
    @classmethod
    def get_all(cls, staff_no, goods_id):

        # 获取喜欢记录总数量
        total_count_sql = "SELECT count(*) as totalNum FROM [like] l WHERE l.status = 1 AND l.goods_id = '%s' AND l.create_by = '%s'" % (goods_id, staff_no)
        df_total_count = pd.read_sql(total_count_sql, con=cls.conn_ss)
        total_num = df_total_count['totalNum'][0]

        records_sql = "SELECT * FROM [like] l WHERE l.status = 1 AND l.goods_id = '%s' AND l.create_by = '%s'" % (goods_id, staff_no)

        df_records = pd.read_sql(records_sql, con=cls.conn_ss)

        df_records = df_records.to_json(orient='records')
        return total_num, df_records

    # 取消想要某商品
    @classmethod
    def cancel_like(cls, data):
        # 根据goods_id和staff_no，将like表中的记录都置为2
        try:
            cursor = cls.conn_ss.cursor()

            staff_no = data['staffNo']
            goods_id = data['goodsId']

            # 更新gifts表中的数据
            update_sql = "UPDATE [like] SET status = 2 WHERE create_by = '%s' AND goods_id = '%s'" % (staff_no, goods_id)
            cursor.execute(update_sql)
            cls.conn_ss.commit()
            cursor.close()
            return True
        except Exception as e:
            print(e)
            cls.conn_ss.rollback()
            return False
