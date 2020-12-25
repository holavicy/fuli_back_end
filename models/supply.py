import pymssql
import pandas as pd


class SupplyModel(object):
    conn_ss = pymssql.connect(host='192.168.40.229:1433', port=3306, user='serverapp', password='wetown2020',
                              database='GiftDB')

    # 创建代领
    @classmethod
    def create_supply(cls, info):
        print(info)
        try:
            cursor = cls.conn_ss.cursor()
            # others_supply表中创建记录
            data = {
                'staff_no': info['staffNo'],
                'can_supply_staff_no': info['othersStaffNo'],
                'year': info['year'],
                'create_by': info['creator'],
                'can_supply_name': info['othersName'],
                'staff_name': info['staffName'],
            }
            base_sql = 'insert into [others_supply] ({}) values ({})'
            sql_item = []
            sql_values = []

            for key in data:
                sql_item.append(key)
                if isinstance(data[key], str):  # 如果是字符串 加上引号
                    sql_values.append("\'" + data[key] + "\'")
                else:
                    sql_values.append(data[key])

            sql_insert = base_sql.format(','.join(sql_item), ','.join(list(map(str, sql_values))))

            print(sql_insert)
            cursor.execute(sql_insert)
            cls.conn_ss.commit()
            cursor.close()
            return True
        except Exception as e:
            print(e)
            cls.conn_ss.rollback()
            return False

    # 获取代领列表
    @classmethod
    def get_all(cls, page, page_size, staff_no, year, supply_staff_no):
        staff_no_sql = ''
        year_sql = ''
        supply_staff_no_sql = ''

        if staff_no:
            staff_no_sql = f'AND staff_no = \'{staff_no}\''

        if year:
            year_sql = f'AND year = \'{year}\''

        if supply_staff_no:
            supply_staff_no_sql = f'AND can_supply_staff_no = \'{supply_staff_no}\''

        # 获取代领总数量
        total_count_sql = f'select COUNT(id) as totalNum from [others_supply] where status = 1 {staff_no_sql} {year_sql} {supply_staff_no_sql}'
        print(total_count_sql)
        df_total_count = pd.read_sql(total_count_sql, con=cls.conn_ss)
        total_num = df_total_count['totalNum'][0]

        # 获取代领记录明细
        if page and page_size:
            min_top = (int(page) - 1) * int(page_size)
            max_top = int(page_size)
            records_sql = f'select top {max_top} * from [others_supply] where id not in (select top {min_top} id from [others_supply] WHERE  status = 1 {staff_no_sql} {year_sql} {supply_staff_no_sql} order by create_time desc) AND status  = 1 {staff_no_sql} {year_sql} {supply_staff_no_sql} order by create_time desc'
            print(records_sql)
        else:
            records_sql = f'select * from [others_supply] WHERE status  = 1 {staff_no_sql} {year_sql} {supply_staff_no_sql} '

        df_records = pd.read_sql(records_sql, con=cls.conn_ss)
        record_list = []
        for index, row in df_records.iterrows():
            row_id = row[0]
            staff_no = row[1]
            staff_name = row[8]
            can_supply_staff_no = row[2]
            can_supply_name = row[7]
            year = row[3]
            record_item = {
                "id": row_id,
                "staff_no": staff_no,
                "staff_name": staff_name,
                "can_supply_staff_no": can_supply_staff_no,
                "can_supply_name": can_supply_name,
                "year": year,
            }
            print(staff_no, can_supply_staff_no, year)
            sql_order = "SELECT * FROM [order] o WHERE o.status != 2 AND o.create_by = '%s' AND o.staff_no = '%s' AND o.[year] = '%s'" % (can_supply_staff_no, staff_no, year)
            df_orders = pd.read_sql(sql_order, con=cls.conn_ss)
            order_list = []
            for order_index, order in df_orders.iterrows():
                order_item = {
                    "id": order[0],
                    "status": order[5]
                }
                order_list.append(order_item)
            record_item["supply_order_list"] = order_list
            record_list.append(record_item)
        df = pd.DataFrame(record_list)
        df = df.to_json(orient='records')

        return total_num, df

    # 取消代领
    @classmethod
    def update_supply_status(cls, data):
        staff_no = data['staffNo']
        year = data['year']
        try:
            cursor = cls.conn_ss.cursor()

            update_sql = f'update [others_supply] set status = 2 where staff_no = {staff_no} and year = {year}'

            cursor.execute(update_sql)
            cls.conn_ss.commit()
            cursor.close()
            return True
        except Exception as e:
            print(e)
            cls.conn_ss.rollback()
            return False