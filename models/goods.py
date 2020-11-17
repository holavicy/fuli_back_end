import pymssql
import pandas as pd


class GoodsModel(object):

    conn_ss = pymssql.connect(host='192.168.40.229:1433', port=3306, user='serverapp', password='wetown2020',
                              database='GiftDB')

    # 获取商品列表
    @classmethod
    def get_all(cls, page, page_size, name, status):
        name_sql = ''
        status_sql = ''
        if status:
            status_sql = '=' + status
        else:
            status_sql = '!=2'

        if name:
            name_sql = f'AND name LIKE \'%{name}%\''

        # 获取商品总数量
        total_count_sql = f'select COUNT(id) as totalNum from goods as g where g.status{status_sql} {name_sql}'
        df_total_count = pd.read_sql(total_count_sql, con=cls.conn_ss)
        total_num = df_total_count['totalNum'][0]

        # 获取商品记录明细
        if page and page_size:
            min_top = (int(page) - 1) * int(page_size)
            max_top = int(page) * int(page_size)
            records_sql = f'select top {max_top} * from goods LEFT JOIN (SELECT a.goods_id, SUM(a.num) num FROM (SELECT gscd.goods_id, gscd.change_type, CASE WHEN gscd.change_type = 1 THEN gscd.num WHEN gscd.change_type = 2 THEN 0-gscd.num ELSE 0 END as num FROM goods_stock_change_detail gscd WHERE gscd.status = 1) a GROUP BY a.goods_id) s ON id = s.goods_id where id not in (select top {min_top} id from goods WHERE status {status_sql} {name_sql} order by create_time desc) AND status {status_sql} {name_sql} order by create_time desc'
        else:
            records_sql = f'select * from goods LEFT JOIN (SELECT a.goods_id, SUM(a.num) num FROM (SELECT gscd.goods_id, gscd.change_type, CASE WHEN gscd.change_type = 1 THEN gscd.num WHEN gscd.change_type = 2 THEN 0-gscd.num ELSE 0 END as num FROM goods_stock_change_detail gscd WHERE gscd.status = 1) a GROUP BY a.goods_id) s ON id = s.goods_id WHERE status {status_sql}'
        df_records = pd.read_sql(records_sql, con=cls.conn_ss)
        df_records = df_records.to_json(orient='records')
        return total_num, df_records

    # 新增商品
    @classmethod
    def create_goods(cls, goods_info, num, staff_no):
        try:
            cursor = cls.conn_ss.cursor()
            # 新增商品
            base_sql_goods = "insert into dbo.goods ({}) values ({})"
            sql_item_goods = ['create_by']
            sql_values_goods = [staff_no]

            for key in goods_info:
                sql_item_goods.append(key)
                if isinstance(goods_info[key], str):  # 如果是字符串 加上引号
                    sql_values_goods.append("\'" + goods_info[key] + "\'")
                else:
                    sql_values_goods.append(goods_info[key])
            sql_goods = base_sql_goods.format(','.join(sql_item_goods), ','.join(list(map(str, sql_values_goods))))

            cursor.execute(sql_goods)

            # 新增商品之后获取该商品id
            goods_id = cursor.lastrowid

            # 新增库存变化明细记录
            base_sql_stock = "insert into dbo.goods_stock_change_detail ({}) values ({})"
            sql_item_stock = []
            sql_values_stock = []

            stock_info = {
                'goods_id': goods_id,
                'num': num,
                'change_des': '手动新增商品时初始化',
                'create_by': staff_no
            }

            for key in stock_info:
                sql_item_stock.append(key)
                if isinstance(stock_info[key], str):  # 如果是字符串 加上引号
                    sql_values_stock.append("\'" + stock_info[key] + "\'")
                else:
                    sql_values_stock.append(stock_info[key])

            sql_stock = base_sql_stock.format(','.join(sql_item_stock), ','.join(list(map(str, sql_values_stock))))

            cursor.execute(sql_stock)

            cls.conn_ss.commit()
            cursor.close()
            return True
        except Exception as e:
            cls.conn_ss.rollback()
            return False

    # 修改商品状态
    @classmethod
    def edit_goods_status(cls, goods_id, status, staff_no):
        try:
            cursor = cls.conn_ss.cursor()

            update_sql = f'update goods set status = {status}, update_by = {staff_no} where id = {goods_id}'

            cursor.execute(update_sql)
            cls.conn_ss.commit()
            cursor.close()
            return True
        except Exception as e:
            cls.conn_ss.rollback()
            return False

    # 修改商品基础信息
    @classmethod
    def edit_goods_info(cls, goods_id, name, unit, price, image_url, update_by):
        try:
            cursor = cls.conn_ss.cursor()
            update_sql = "update goods set name = '%s', unit = '%s', price = '%s', image_url = '%s', update_by = '%s' where id = '%d'" % (name, unit, price, image_url, update_by, goods_id)
            cursor.execute(update_sql)
            cls.conn_ss.commit()
            cursor.close()
            return True
        except Exception as e:
            cls.conn_ss.rollback()
            return False

    # 获取商品库存明细
    @classmethod
    def get_goods_stock(cls, page, page_size, goods_id):

        min_top = (int(page) - 1) * int(page_size)
        max_top = int(page) * int(page_size)

        # 获取商品库存明细总条数
        total_count_sql = "select COUNT(id) as totalNum from goods_stock_change_detail as gscd where gscd.status = 1 and gscd.goods_id = '%s'"%(goods_id)
        df_total_count = pd.read_sql(total_count_sql, con=cls.conn_ss)
        total_num = df_total_count['totalNum'][0]

        # 获取商品库存明细
        records_sql = "select top %d * from goods_stock_change_detail where id not in (select top %d id from goods_stock_change_detail WHERE status = 1 and goods_id = '%s' order by create_time desc) AND status = 1 and goods_id = '%s' order by create_time desc" % (max_top, min_top, goods_id, goods_id)
        df_records = pd.read_sql(records_sql, con=cls.conn_ss)
        df_records = df_records.to_json(orient='records', date_format='iso', date_unit = 's')
        return total_num, df_records

    # 修改商品库存
    @classmethod
    def add_stock_detail(cls, info):
        try:
            cursor = cls.conn_ss.cursor()

            base_sql = "insert into dbo.goods_stock_change_detail ({}) values ({})"
            sql_item = []
            sql_values = []

            for key in info:
                sql_item.append(key)
                if isinstance(info[key], str):  # 如果是字符串 加上引号
                    sql_values.append("\'" + info[key] + "\'")
                else:
                    sql_values.append(info[key])
            sql = base_sql.format(','.join(sql_item), ','.join(list(map(str, sql_values))))

            cursor.execute(sql)
            cls.conn_ss.commit()
            cursor.close()
            return Ture
        except Exception as e:
            cls.conn_ss.rollback()
            return False
