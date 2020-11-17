import pymssql
import pandas as pd


class OrderModel(object):
    conn_ss = pymssql.connect(host='192.168.40.229:1433', port=3306, user='serverapp', password='wetown2020',
                              database='GiftDB')

    # 获取所有订单
    @classmethod
    def get_orders(cls, staff_no, year):
        cursor = cls.conn_ss.cursor()

        sql = "SELECT * FROM [order] o WHERE o.status != 2 AND o.staff_no = '%s' AND o.[year] = '%s'" % (staff_no, year)
        cursor.execute(sql)
        result_list = cursor.fetchall()
        print(result_list)
        print(type(result_list))

        cls.conn_ss.commit()
        cursor.close()

        return result_list

    # 创建订单
    @classmethod
    def create_order(cls, info):
        print('create_order')
        print(info)
        try:
            cursor = cls.conn_ss.cursor()
            # order表中创建记录
            data = {
                'staff_no': info['staffNo'],
                'gift_id': info['id'],
                'gift_name': info['name'],
                'gift_goods_limit_num': info['limitGoodsNum'],
                'year': info['year'],
                'create_by': info['creator']
            }
            base_sql_order = 'insert into [order] ({}) values ({})'
            sql_item_order = []
            sql_values_order = []

            for key in data:
                sql_item_order.append(key)
                if isinstance(data[key], str):  # 如果是字符串 加上引号
                    sql_values_order.append("\'" + data[key] + "\'")
                else:
                    sql_values_order.append(data[key])

            sql_insert_order = base_sql_order.format(','.join(sql_item_order), ','.join(list(map(str, sql_values_order))))

            print(sql_insert_order)
            cursor.execute(sql_insert_order)

            # 获取order.id
            order_id = cursor.lastrowid
            print(order_id)

            # order_goods表中创建记录
            goods_list = info['goods']
            for goods in goods_list:
                relation_info = {
                    'order_id': order_id,
                    'goods_id': goods['id'],
                    'goods_name': goods['name'],
                    'goods_image_url': goods['imageUrl'],
                    'goods_unit': goods['unit'],
                    'goods_price': goods['price']
                }

                stock_info = {
                    'goods_id': goods['id'],
                    'change_type': 2,
                    'num': 1,
                    'change_des': '通过福利管理系统领取生日礼包',
                    'create_by': info['creator']
                }

                base_sql_relation = 'insert into dbo.order_goods ({}) values ({})'
                base_sql_stock = 'insert into dbo.goods_stock_change_detail ({}) values ({})'
                sql_item_relation = []
                sql_values_relation = []
                sql_item_stock = []
                sql_values_stock = []

                for key in relation_info:
                    sql_item_relation.append(key)
                    if isinstance(relation_info[key], str):  # 如果是字符串 加上引号
                        sql_values_relation.append("\'" + relation_info[key] + "\'")
                    else:
                        sql_values_relation.append(relation_info[key])

                sql_relation = base_sql_relation.format(','.join(sql_item_relation),
                                                        ','.join(list(map(str, sql_values_relation))))
                cursor.execute(sql_relation)
                # goods_stock_change_detial表中创建记录
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

    # 获取订单列表
    @classmethod
    def get_all(cls, page, page_size, staff_no, year, order_status):
        staff_no_sql = ''
        year_sql = ''
        status_sql = ''
        if order_status:
            status_sql = '=' + order_status
        else:
            status_sql = '!=2'

        if staff_no:
            staff_no_sql = f'AND staff_no = \'{staff_no}\''

        if year:
            year_sql = f'AND year = \'{year}\''

        # 获取订单总数量
        total_count_sql = f'select COUNT(id) as totalNum from [order] where status{status_sql} {staff_no_sql} {year_sql}'
        print(total_count_sql)
        df_total_count = pd.read_sql(total_count_sql, con=cls.conn_ss)
        total_num = df_total_count['totalNum'][0]

        # 获取订单记录明细
        if page and page_size:
            min_top = (int(page) - 1) * int(page_size)
            max_top = int(page) * int(page_size)
            records_sql = f'select top {max_top} * from [order] where id not in (select top {min_top} id from [order] WHERE status {status_sql} {staff_no_sql} {year_sql} order by create_time desc) AND status {status_sql} {staff_no_sql} {year_sql} order by create_time desc'
            print(records_sql)
        else:
            records_sql = f'select * from [order] WHERE status {status_sql} {staff_no_sql} {year_sql}'
        df_records = pd.read_sql(records_sql, con=cls.conn_ss)

        # 遍历结果，根据order_id查询商品列表
        order_list = []
        for index, row in df_records.iterrows():
            order_item = {}
            order_item['id'] = row[0]
            order_item['staffNo'] = row[1]
            order_item['giftId'] = row[2]
            order_item['giftName'] = row[3]
            order_item['giftGoodsLimit'] = row[4]
            order_item['status'] = row[5]
            order_item['year'] = row[6]
            order_item['goods'] = []

            sql_goods = "SELECT * FROM order_goods og WHERE og.status = 1 AND og.order_id = '%s'" % (row[0])

            df_goods = pd.read_sql(sql_goods, con=cls.conn_ss)
            goods_list = []

            for i, goods in df_goods.iterrows():
                goods_item = {}
                goods_item['id'] = goods[2]
                goods_item['name'] = goods[3]
                goods_item['imageUrl'] = goods[4]
                goods_item['unit'] = goods[5]
                goods_item['price'] = goods[6]
                goods_list.append(goods_item)
            order_item['goods'] = goods_list
            order_list.append(order_item)
        df = pd.DataFrame(order_list)
        df = df.to_json(orient='records')

        return total_num, df

    # 修改订单状态
    @classmethod
    def edit_order_status(cls, order_id, status, staff_no):
        try:
            cursor = cls.conn_ss.cursor()
            update_sql = ''
            if status == 3:
                update_sql = "update [order] set status = '%d', confirm_by = '%s' where id = '%s'" % (status, staff_no, order_id)
            if status == 4:
                update_sql = "update [order] set status = '%d', finished_by = '%s' where id = '%s'" % (status, staff_no, order_id)
            cursor.execute(update_sql)
            cls.conn_ss.commit()
            return True
        except Exception as e:
            print(e)
            cls.conn_ss.rollback()
            return False
