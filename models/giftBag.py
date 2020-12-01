import pymssql
import pandas as pd
from common.tool import get_now


class GiftBagModel(object):
    conn_ss = pymssql.connect(host='192.168.40.229:1433', port=3306, user='serverapp', password='wetown2020',
                              database='GiftDB')

    # 新增礼包
    @classmethod
    def create_gift_bag(cls, info):
        try:
            cursor = cls.conn_ss.cursor()

            # 向礼包表中新增数据
            data = {
                'name': info['name'],
                'limit_goods_num': info['limitGoodsNum'],
                'create_by': info['staffNo']
            }
            base_sql_gifts = 'insert into dbo.gifts ({}) values ({})'
            sql_item_gifts = []
            sql_values_gifts = []

            for key in data:
                sql_item_gifts.append(key)
                if isinstance(data[key], str):  # 如果是字符串 加上引号
                    sql_values_gifts.append("\'" + data[key] + "\'")
                else:
                    sql_values_gifts.append(data[key])

            sql_gifts = base_sql_gifts.format(','.join(sql_item_gifts), ','.join(list(map(str, sql_values_gifts))))

            cursor.execute(sql_gifts)

            # 成功后获取礼包ID
            gift_id = cursor.lastrowid

            # 向礼包商品关系表中插入数据

            goods_list = info['goods']
            for goods in goods_list:
                relation_info = {
                    'gift_id': gift_id,
                    'goods_id': goods['id'],
                    'create_by': info['staffNo']
                }

                base_sql_relation = 'insert into dbo.gift_goods_relation ({}) values ({})'
                sql_item_relation = []
                sql_values_relation = []

                for key in relation_info:
                    sql_item_relation.append(key)
                    if isinstance(relation_info[key], str):  # 如果是字符串 加上引号
                        sql_values_relation.append("\'" + relation_info[key] + "\'")
                    else:
                        sql_values_relation.append(relation_info[key])

                sql_relation = base_sql_relation.format(','.join(sql_item_relation), ','.join(list(map(str, sql_values_relation))))
                cursor.execute(sql_relation)
            cls.conn_ss.commit()
            cursor.close()
            return True
        except Exception as e:
            print(e)
            cls.conn_ss.rollback()
            return False

    # 获取礼包列表
    @classmethod
    def get_all(cls, page, page_size, gift_name, goods_name, gift_status):
        gift_ids_str = ''
        if goods_name:
            print(goods_name)
            gift_ids_str = cls.get_ids_by_goods_name(goods_name)

        name_sql = ''
        status_sql = ''
        ids_sql = ''
        if gift_status:
            status_sql = '=' + gift_status
        else:
            status_sql = '!=2'

        if gift_name:
            name_sql = f'AND name LIKE \'%{gift_name}%\''

        if gift_ids_str:
            ids_sql = f'and id in ({gift_ids_str})'

        if goods_name and gift_ids_str == '':
            total_num = 0
            df = '[]'
            return total_num, df
        else:
            # 获取总数
            total_count_sql = f'select COUNT(id) as totalNum FROM gifts WHERE status {status_sql} {name_sql} {ids_sql}'
            df_total_count = pd.read_sql(total_count_sql, con=cls.conn_ss)
            total_num = df_total_count['totalNum'][0]

            # 获取gift记录
            if page and page_size:
                min_top = (int(page) - 1) * int(page_size)
                max_top = int(page) * int(page_size)
                records_sql = f'select top {max_top} * from gifts where id not in (select top {min_top} id from gifts WHERE status {status_sql} {name_sql} {ids_sql}  order by create_time desc) AND status {status_sql} {name_sql} {ids_sql} order by create_time desc'
            else:
                records_sql = f'select * from gifts WHERE status {status_sql} {name_sql} {ids_sql}  order by create_time desc'
            df_records = pd.read_sql(records_sql, con=cls.conn_ss)
            gift_list = []
            for index, row in df_records.iterrows():
                gift_item = {}
                gift_item['id'] = row[0]
                gift_item['name'] = row[1]
                gift_item['status'] = row[2]
                gift_item['limitGoodsNum'] = row[3]
                gift_item['goods'] = []
                gift_id = row[0]
                sql_relation = '''SELECT gi.*
                                    FROM gift_goods_relation ggr
                                    INNER JOIN (
                                    select g.id goodsId, g.name goodsName, g.image_url,g.unit, g.price, s.num
                                    from goods g
                                    LEFT JOIN (
                                    SELECT a.goods_id, SUM(a.num) num 
                                    FROM (
                                    SELECT gscd.goods_id, gscd.change_type, CASE WHEN gscd.change_type = 1 THEN gscd.num WHEN gscd.change_type = 2 THEN 0-gscd.num ELSE 0 END as num 
                                    FROM goods_stock_change_detail gscd 
                                    WHERE gscd.status = 1) a 
                                    GROUP BY a.goods_id) s ON g.id = s.goods_id
                                    WHERE g.status = 1) gi ON gi.goodsId = ggr.goods_id
                                    WHERE ggr.gift_id = %d
                                    AND ggr.status = 1 '''%(gift_id)
                df_goods = pd.read_sql(sql_relation, con=cls.conn_ss)
                goods_list = []
                for goodsIndex, goods in df_goods.iterrows():
                    goods_item = {}
                    goods_item['id'] = goods[0]
                    goods_item['name'] = goods[1]
                    goods_item['imageUrl'] = goods[2]
                    goods_item['unit'] = goods[3]
                    goods_item['price'] = goods[4]
                    goods_item['num'] = goods[5]
                    goods_list.append(goods_item)
                gift_item['goods'] = goods_list
                gift_list.append(gift_item)

            df = pd.DataFrame(gift_list)
            df = df.to_json(orient='records')
            return total_num, df

    # 根据商品名称获取相关的gifts_id
    @classmethod
    def get_ids_by_goods_name(cls, name):
        sql = f'SELECT ggr.gift_id FROM gift_goods_relation ggr INNER JOIN goods g ON ggr.goods_id = g.id WHERE ggr.status = 1 AND g.status = 1 AND g.name LIKE \'%{name}%\''
        df_records = pd.read_sql(sql, con=cls.conn_ss)
        gift_ids_list = []
        for item in df_records['gift_id']:
            gift_ids_list.append(item)
        gift_ids_str = ','.join([str(i) for i in gift_ids_list])
        return gift_ids_str

    # 修改礼包状态
    @classmethod
    def edit_gift_bag_status(cls, gift_bag_id, status, staff_no):
        now = get_now()
        now= f'\'{now}\''
        try:
            cursor = cls.conn_ss.cursor()

            update_sql = f'update gifts set status = {status}, update_by = {staff_no}, update_time = {now} where id = {gift_bag_id}'

            cursor.execute(update_sql)
            cls.conn_ss.commit()
            cursor.close()
            return True
        except Exception as e:
            cls.conn_ss.rollback()
            return False

    # 修改礼包信息
    @classmethod
    def edit_gift_bag_info(cls, data):
        now = get_now()
        # try:
        cursor = cls.conn_ss.cursor()

        # 更新gifts表中的数据
        update_sql = "update gifts set name = '%s', limit_goods_num = '%d', update_by = '%s', update_time = '%s' where id = '%s'" % (data['name'], data['limitGoodsNum'], data['staffNo'], now, data['id'])
        cursor.execute(update_sql)

        # 根据gifts.id删除gifts_goods_relation表中的关系
        update_relation_sql = "update gift_goods_relation set status = 2, update_by = '%s', update_time = '%s' where gift_id = '%s' and status = 1" % (data['staffNo'], now, data['id'])
        cursor.execute(update_relation_sql)

        # 根据goods插入新的数据
        goods_list = data['goods']
        for goods in goods_list:
            relation_info = {
                'gift_id': data['id'],
                'goods_id': goods['id'],
                'create_by': data['staffNo']
            }

            base_sql_relation = 'insert into dbo.gift_goods_relation ({}) values ({})'
            sql_item_relation = []
            sql_values_relation = []

            for key in relation_info:
                sql_item_relation.append(key)
                if isinstance(relation_info[key], str):  # 如果是字符串 加上引号
                    sql_values_relation.append("\'" + relation_info[key] + "\'")
                else:
                    sql_values_relation.append(relation_info[key])

            sql_relation = base_sql_relation.format(','.join(sql_item_relation),
                                                    ','.join(list(map(str, sql_values_relation))))
            print(sql_relation)
            cursor.execute(sql_relation)
            print('end_gift')
            print(goods)

        cls.conn_ss.commit()
        cursor.close()
        return True
        # except Exception as e:
        #     cls.conn_ss.rollback()
        #     return False
