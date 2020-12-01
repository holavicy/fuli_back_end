import pymssql
import pandas as pd
from common.tool import get_now


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
            records_sql = f'select top {max_top} * from goods LEFT JOIN (SELECT a.goods_id, SUM(a.num) num FROM (SELECT gscd.goods_id, gscd.change_type, CASE WHEN gscd.change_type = 1 THEN gscd.num WHEN gscd.change_type = 2 THEN 0-gscd.num ELSE 0 END as num FROM goods_stock_change_detail gscd WHERE gscd.status = 1) a GROUP BY a.goods_id) s ON id = s.goods_id LEFT JOIN(\
	                        SELECT b.goods_id as c_goods_id, count(*) likeStaffNum, SUM(b.num) likeNum FROM(SELECT l.goods_id, l.create_by,count(*) as num FROM [like] l GROUP BY l.goods_id,l.create_by) b GROUP BY b.goods_id) c on id = c.c_goods_id  \
                where id not in (select top {min_top} id from goods WHERE status {status_sql} {name_sql} order by create_time desc) AND status {status_sql} {name_sql} order by create_time desc'
        else:
            records_sql = f'select * from goods LEFT JOIN (SELECT a.goods_id, SUM(a.num) num FROM (SELECT gscd.goods_id, gscd.change_type, CASE WHEN gscd.change_type = 1 THEN gscd.num WHEN gscd.change_type = 2 THEN 0-gscd.num ELSE 0 END as num FROM goods_stock_change_detail gscd WHERE gscd.status = 1) a GROUP BY a.goods_id) s ON id = s.goods_id LEFT JOIN(\
	                        SELECT b.goods_id as c_goods_id, count(*) likeStaffNum, SUM(b.num) likeNum FROM(SELECT l.goods_id, l.create_by,count(*) as num FROM [like] l GROUP BY l.goods_id,l.create_by) b GROUP BY b.goods_id) c on id = c.c_goods_id  \
                WHERE status {status_sql}'

        print(records_sql)

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
            print(e)
            cls.conn_ss.rollback()
            return False

    # 修改商品状态
    @classmethod
    def edit_goods_status(cls, goods_id, status, staff_no):
        now = get_now()
        now = f'\'{now}\''
        try:
            cursor = cls.conn_ss.cursor()

            # 商品下架之前先判断一下该商品是否属于某个礼包，若属于，不允许下架，提示用户先取消和礼包的关联关系，而后，再进行下架
            if status != 1:

                belong_gift = cls.belong_gift(goods_id)

                if belong_gift:
                    return 1
                else:
                    update_sql = f'update goods set status = {status}, update_by = {staff_no}, update_time = {now} where id = {goods_id}'
                    print(update_sql)
                    cursor.execute(update_sql)
                    cls.conn_ss.commit()
                    cursor.close()
                    return 2

            else:
                update_sql = f'update goods set status = {status}, update_by = {staff_no}, update_time = {now} where id = {goods_id}'
                cursor.execute(update_sql)
                cls.conn_ss.commit()
                cursor.close()
                return 2

        except Exception as e:
            print(e)
            cls.conn_ss.rollback()
            return 3

    # 修改商品基础信息
    @classmethod
    def edit_goods_info(cls, goods_id, name, unit, price, image_url, update_by):
        now = get_now()
        try:
            cursor = cls.conn_ss.cursor()
            update_sql = "update goods set name = '%s', unit = '%s', price = '%s', image_url = '%s', update_by = '%s', update_time = '%s' where id = '%d'" % (name, unit, price, image_url, update_by, now, goods_id)
            cursor.execute(update_sql)
            cls.conn_ss.commit()
            cursor.close()
            return True
        except Exception as e:
            print(e)
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
            print('新增')
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
            return True
        except Exception as e:
            print(e)
            cls.conn_ss.rollback()
            return False

    # 根据id判断商品是否存在
    @classmethod
    def is_exist_goods(cls, goods_id):
        sql = f'select * from goods as g where g.id = {goods_id} and g.status != 2'
        df_records = pd.read_sql(sql, con=cls.conn_ss)
        print(len(df_records))

        if len(df_records) > 0:
            return True
        else:
            return False

    # 批量新增或更新商品 一个失败全部回滚
    @classmethod
    def batch_import_goods(cls, file_data_frame, staff_no):
        now = get_now()
        try:
            cursor = cls.conn_ss.cursor()
            for index, line in file_data_frame.iterrows():
                goods_id = line[0]
                goods_name = line[1]
                unit = line[2]
                num = line[3]
                price = line[4]
                # 根据id判断是否存在，若存在，更新
                flag = cls.is_exist_goods(goods_id)
                if flag:
                    update_sql = "update goods set name = '%s', unit = '%s', price = '%s', image_url = '%s', update_by = '%s', update_time where id = '%d'" % (
                    goods_name, unit, price, '', staff_no, now, goods_id)
                    cursor.execute(update_sql)

                    info = {
                        'goods_id': goods_id,
                        'change_type': 1,
                        'num': num,
                        'change_des': '导入',
                        'create_by': staff_no,
                    }
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
                else:
                    # 若不存在， 新增
                    print('add')
                    goods_info = {
                        'name': goods_name,
                        'unit': unit,
                        'image_url': '',
                        'price': price
                    }
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
                    sql_goods = base_sql_goods.format(','.join(sql_item_goods),
                                                      ','.join(list(map(str, sql_values_goods))))

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
                        'change_des': '导入',
                        'create_by': staff_no
                    }

                    for key in stock_info:
                        sql_item_stock.append(key)
                        if isinstance(stock_info[key], str):  # 如果是字符串 加上引号
                            sql_values_stock.append("\'" + stock_info[key] + "\'")
                        else:
                            sql_values_stock.append(stock_info[key])

                    sql_stock = base_sql_stock.format(','.join(sql_item_stock),
                                                      ','.join(list(map(str, sql_values_stock))))

                    cursor.execute(sql_stock)

            cls.conn_ss.commit()
            cursor.close()
            return True
        except Exception as e:
            print(e)
            cls.conn_ss.rollback()
            return False

    # 判断某个商品是否属于某个礼包（上架和下架）
    @classmethod
    def belong_gift(cls, goods_id):
        sql = f'SELECT * FROM gift_goods_relation ggr INNER JOIN gifts g on g.id = ggr.gift_id WHERE ggr.status = 1 AND g.status != 2 AND ggr.goods_id = {goods_id}'
        df_records = pd.read_sql(sql, con=cls.conn_ss)
        print(len(df_records))

        if len(df_records) > 0:
            return True
        else:
            return False

    # 删除库存记录
    @classmethod
    def delete_stock_detail(cls, stock_id, create_by):
        now = get_now()
        now = f'\'{now}\''
        try:
            cursor = cls.conn_ss.cursor()

            update_sql = f'update goods_stock_change_detail set status = 2, update_by = {create_by}, update_time = {now} where id = {stock_id}'
            cursor.execute(update_sql)
            cls.conn_ss.commit()
            cursor.close()
            return True
        except Exception as e:
            print(e)
            cls.conn_ss.rollback()
            return False

    # 修改库存明细记录
    @classmethod
    def update_stock_detail(cls, change_type, num, desc, stock_id, create_by):
        now = get_now()
        try:
            cursor = cls.conn_ss.cursor()

            update_sql = "update goods_stock_change_detail set change_type = '%s', num = '%s', change_des = '%s', update_by = '%s', update_time = '%s' where id = '%s'" % \
                         (change_type, num, desc, create_by, now, stock_id)
            print(update_sql)
            cursor.execute(update_sql)
            cls.conn_ss.commit()
            cursor.close()
            return True
        except Exception as e:
            print(e)
            cls.conn_ss.rollback()
            return False
