import pymssql
import cx_Oracle
import pandas as pd
from common.tool import get_now


class ChartModel(object):
    conn_ss = pymssql.connect(host='192.168.40.229:1433', port=3306, user='serverapp', password='wetown2020',
                              database='GiftDB')

    ncDbInfo = {
        "user": "nc633_rebulid",
        "password": "nc633_123",
        "db": "wtdb",
        "host": "192.168.40.230",
        "port": "1521",
    }

    db_nc = cx_Oracle.connect(
        f'{ncDbInfo["user"]}/{ncDbInfo["password"]}@{ncDbInfo["host"]}:{ncDbInfo["port"]}/{ncDbInfo["db"]}',
        encoding="UTF-8", nencoding="UTF-8")

    # 商品库存报表
    @classmethod
    def goods_stock_report(cls):
        sql = "SELECT g.id, g.name, ISNULL(a.allIn, 0) allIn, ISNULL(b.allOut, 0) allOut, ISNULL(a.allIn, 0) - ISNULL(b.allOut, 0) stock, g.price, ISNULL(a.allIn, 0) * g.price totalInAmount\
                FROM goods g\
                LEFT JOIN (\
                    SELECT gscd.goods_id, SUM(gscd.num) allIn\
                    FROM goods_stock_change_detail gscd\
                    WHERE gscd.status != 2\
                    AND gscd.change_type = 1\
                    GROUP BY gscd.goods_id\
                ) a ON a.goods_id = g.id\
                LEFT JOIN (\
                    SELECT gscd.goods_id, SUM(gscd.num) allOut\
                    FROM goods_stock_change_detail gscd\
                    WHERE gscd.status != 2\
                    AND gscd.change_type = 2\
                    GROUP BY gscd.goods_id\
                ) b ON b.goods_id = g.id\
                WHERE g.status != 2;"
        result_list = pd.read_sql(sql, con=cls.conn_ss)
        result_list = result_list.to_json(orient='records')
        return result_list

    @classmethod
    def goods_stock_in_detail_report(cls, goods_name, begin_date, end_date, page, page_size):
        try:
            name_sql = ''
            begin_sql = ''
            end_sql = ''
            if goods_name:
                name_sql = f'AND name LIKE \'%{goods_name}%\''
            if begin_date:
                begin_time = str(begin_date) + ' 00:00:00'
                begin_sql = f'AND gscd.create_time >= \'{begin_time}\''
            if end_date:
                end_time = str(end_date) + ' 23:59:59'
                end_sql = f'AND gscd.create_time <= \'{end_time}\''
            num_sql = f'SELECT count(*) as totalNum\
                    FROM goods_stock_change_detail gscd\
                    INNER JOIN goods g ON g.id = gscd.goods_id\
                    WHERE gscd.status != 2\
                    AND gscd.change_type = 1 ' \
                    f'{name_sql} {begin_sql} {end_sql}'
            df_total_count = pd.read_sql(num_sql, con=cls.conn_ss)
            total_num = df_total_count['totalNum'][0]

            sql = f'SELECT g.id, g.name, gscd.create_time, gscd.num, gscd.price, gscd.num * gscd.price as amount, gscd.change_des\
                      FROM goods_stock_change_detail gscd\
                      INNER JOIN goods g ON g.id = gscd.goods_id\
                      WHERE gscd.status != 2\
                      AND gscd.change_type = 1 ' \
                f'{name_sql} {begin_sql} {end_sql} order by gscd.create_time desc'

            if page and page_size:
                min_top = (int(page) - 1) * int(page_size)
                max_top = int(page_size)
                sql = f'SELECT top {max_top} * \
                        from (SELECT gscd.id gid, g.id, g.name, gscd.create_time, gscd.num, gscd.price, gscd.num * gscd.price as amount, gscd.change_des\
                                FROM goods_stock_change_detail gscd\
                                INNER JOIN goods g ON g.id = gscd.goods_id\
                                WHERE gscd.status != 2\
                                AND gscd.change_type = 1\
                                {name_sql}\
                                {begin_sql}\
                                {end_sql}) a\
                        WHERE a.gid not in (\
                            SELECT top {min_top} b.gid from ( SELECT gscd.id gid, g.id, g.name, gscd.create_time, gscd.num, gscd.price, gscd.num * gscd.price as amount, gscd.change_des\
                            FROM goods_stock_change_detail gscd\
                            INNER JOIN goods g ON g.id = gscd.goods_id\
                            WHERE gscd.status != 2\
                            AND gscd.change_type = 1\
                            {name_sql}\
                            {begin_sql}\
                            {end_sql}) b order by b.create_time desc) order by a.create_time desc'
            df_records = pd.read_sql(sql, con=cls.conn_ss)
            df_records = df_records.to_json(orient='records')
            return total_num, df_records
        except Exception as e:
            print(e)

    @classmethod
    def goods_stock_out_detail_report(cls, goods_name, begin_date, end_date, page, page_size):
        try:
            name_sql = ''
            begin_sql = ''
            end_sql = ''
            if goods_name:
                name_sql = f'AND name LIKE \'%{goods_name}%\''
            if begin_date:
                begin_time = str(begin_date) + ' 00:00:00'
                begin_sql = f'AND gscd.create_time >= \'{begin_time}\''
            if end_date:
                end_time = str(end_date) + ' 23:59:59'
                end_sql = f'AND gscd.create_time <= \'{end_time}\''
            num_sql = f'SELECT count(*) as totalNum\
                    FROM goods_stock_change_detail gscd\
                    INNER JOIN goods g ON g.id = gscd.goods_id\
                    WHERE gscd.status != 2\
                    AND gscd.change_type = 2 ' \
                    f'{name_sql} {begin_sql} {end_sql}'
            df_total_count = pd.read_sql(num_sql, con=cls.conn_ss)
            total_num = df_total_count['totalNum'][0]

            sql = f'SELECT g.id, g.name, gscd.create_time, gscd.num, gscd.price, gscd.num * gscd.price as amount, gscd.change_des\
                      FROM goods_stock_change_detail gscd\
                      INNER JOIN goods g ON g.id = gscd.goods_id\
                      WHERE gscd.status != 2\
                      AND gscd.change_type = 2 ' \
                f'{name_sql} {begin_sql} {end_sql} order by gscd.create_time desc'

            if page and page_size:
                min_top = (int(page) - 1) * int(page_size)
                max_top = int(page_size)
                sql = f'SELECT top {max_top} * \
                        from (SELECT gscd.id gid, g.id, g.name, gscd.create_time, gscd.num, gscd.price, gscd.num * gscd.price as amount, gscd.change_des\
                                FROM goods_stock_change_detail gscd\
                                INNER JOIN goods g ON g.id = gscd.goods_id\
                                WHERE gscd.status != 2\
                                AND gscd.change_type = 2\
                                {name_sql}\
                                {begin_sql}\
                                {end_sql}) a\
                        WHERE a.gid not in (\
                            SELECT top {min_top} b.gid from ( SELECT gscd.id gid, g.id, g.name, gscd.create_time, gscd.num, gscd.price, gscd.num * gscd.price as amount, gscd.change_des\
                            FROM goods_stock_change_detail gscd\
                            INNER JOIN goods g ON g.id = gscd.goods_id\
                            WHERE gscd.status != 2\
                            AND gscd.change_type = 2\
                            {name_sql}\
                            {begin_sql}\
                            {end_sql} ) b order by b.create_time desc) order by a.create_time desc'
            df_records = pd.read_sql(sql, con=cls.conn_ss)
            df_records = df_records.to_json(orient='records')
            return total_num, df_records
        except Exception as e:
            print(e)

    @classmethod
    def gift_record(cls, gift_name, year, page, page_size):
        try:
            name_sql = ''
            year_sql = ''
            if gift_name:
                name_sql = f'and g.name like \'%{gift_name}%\''
            if year:
                year_sql = f'and o.[year] = \'{year}\' '

            num_sql = f'SELECT count(*) as totalNum\
                        FROM [order] o\
                        INNER JOIN gifts g ON g.id = o.gift_id\
                        WHERE o.status = 4 {name_sql} {year_sql}'
            df_total_count = pd.read_sql(num_sql, con=cls.conn_ss)
            total_num = df_total_count['totalNum'][0]

            sql = f'SELECT o.id as oid, o.[year], g.name, o.staff_no, o.staff_name, o.finish_time\
                        FROM [order] o\
                        INNER JOIN gifts g ON g.id = o.gift_id\
                        WHERE o.status = 4 {name_sql} {year_sql}'\
                    f'ORDER BY o.finish_time DESC'

            if page and page_size:
                min_top = (int(page) - 1) * int(page_size)
                max_top = int(page_size)
                sql = f'SELECT top {max_top} * \
                        from (SELECT o.id as oid, o.[year], g.name, o.staff_no, o.staff_name, o.finish_time\
                        FROM [order] o\
                        INNER JOIN gifts g ON g.id = o.gift_id\
                        WHERE o.status = 4' \
                            f'{name_sql} {year_sql} ) a\
                                    WHERE a.oid not in (\
                                        SELECT top {min_top} b.oid from ( SELECT o.id as oid, o.[year], g.name, o.staff_no, o.staff_name, o.finish_time\
                        FROM [order] o\
                        INNER JOIN gifts g ON g.id = o.gift_id\
                        WHERE o.status = 4 {name_sql} {year_sql}) b order by b.finish_time desc) order by a.finish_time desc'

            df_records = pd.read_sql(sql, con=cls.conn_ss)
            gift_list = []
            for index, row in df_records.iterrows():
                order_id = row[0]
                staff_no = row[3]
                goods_list = cls.get_order_goods_by_id(order_id)
                staff_info = cls.get_user_info_nc(staff_no)
                print(staff_info)
                birth_date = staff_info['BIRTHDATE'][0]
                dept_id = staff_info['PK_DEPT'][0]
                org_name = staff_info['ORGNAME'][0]

                dept_list = cls.get_dept_list(dept_id, [])

                gift_item = {
                    "order_id": order_id,
                    "gift_name": row[2],
                    "staff_no": staff_no,
                    "staff_name": row[4],
                    "finish_time": row[5],
                    "goods_list": goods_list,
                    "birth_date": birth_date,
                    "dept_list": dept_list,
                    "org_name": org_name
                }
                gift_list.append(gift_item)
            df = pd.DataFrame(gift_list)
            df = df.to_json(orient='records')
            return total_num, df
        except Exception as e:
            print(e)

    @classmethod
    def get_order_goods_by_id(cls, order_id):
        sql = "SELECT og.order_id, og.goods_id, og.goods_name, gscd.price\
                FROM order_goods og \
                INNER JOIN goods_stock_change_detail gscd ON gscd.order_id = og.order_id AND gscd.goods_id = og.goods_id\
                WHERE og.status = 1\
                AND og.order_id = '%s'" % (order_id)
        df_records = pd.read_sql(sql, con=cls.conn_ss)
        goods_list = []
        for index, row in df_records.iterrows():
            goods_item = {
                "goods_name": row[2],
                "goods_num": 1,
                "goods_price": row[3],
                "total_amount": row[3]
            }
            goods_list.append(goods_item)
        return goods_list

    @classmethod
    def get_user_info_nc(cls, staff_no):
        sql = "select ss.code, org.name as orgName, ss.birthdate,job.pk_dept from bd_psndoc ss inner join hi_psnjob job on ss.pk_psndoc = job.pk_psndoc left join org_orgs org on job.pk_org = org.pk_org where job.endflag = 'N' and job.ismainjob = 'Y' and job.lastflag = 'Y' and ss.code = '%s'" % (staff_no.strip())
        df_records = pd.read_sql(sql, con=cls.db_nc)
        return df_records

    @classmethod
    def get_dept_info(cls, dept_id):
        sql = "select name,pk_fatherorg from org_dept where pk_dept='%s'" % (dept_id.strip())
        df_records = pd.read_sql(sql, con=cls.db_nc)
        return df_records

    @classmethod
    def get_dept_list(cls, dept_id, dept_list):
        dept_info = cls.get_dept_info(dept_id)
        dept_name = dept_info['NAME'][0]
        dept_father_id = dept_info['PK_FATHERORG'][0]
        dept_list.insert(0, dept_name)
        if dept_father_id == '~':
            return dept_list

        return cls.get_dept_list(dept_father_id, dept_list)

    @classmethod
    def gift_sum_report(cls):
        sql = "SELECT a.gift_id, g.name, a.num\
                FROM (\
                    SELECT o.gift_id, COUNT(o.id) as num\
                    FROM [order] o\
                    WHERE o.status = 4\
                    GROUP BY o.gift_id\
                )a INNER JOIN gifts g ON a.gift_id = g.id;"
        df_records = pd.read_sql(sql, con=cls.conn_ss)
        gift_list = []
        for index, row in df_records.iterrows():
            gift_id = row[0]

            goods_sql = "SELECT g.name, a.goodsNum, a.allAmount, CAST(a.allAmount/ a.goodsNum as DECIMAL(5,2)) avgPrice\
                            from (\
                            SELECT og.goods_id, COUNT(og.id) as goodsNum, SUM(gscd.price) as allAmount\
                            FROM [order] o\
                            INNER JOIN order_goods og ON og.order_id = o.id\
                            INNER JOIN goods_stock_change_detail gscd ON og.order_id = gscd.order_id AND og.goods_id = gscd.goods_id\
                            WHERE o.status = 4\
                            AND o.gift_id = '%s'\
                            GROUP BY og.goods_id ) a\
                            INNER JOIN goods g ON a.goods_id = g.id" % (gift_id)
            goods_list = []
            gift_all_amount = 0
            df_goods_records = pd.read_sql(goods_sql, con=cls.conn_ss)
            for goodsIndex, goods in df_goods_records.iterrows():
                goods_item = {
                    "goods_name": goods[0],
                    "goods_num": goods[1],
                    "goods_avg_price": goods[3],
                    "goods_total_amount": goods[2]
                }
                goods_list.append(goods_item)
                gift_all_amount = int(goods[2]) + int(gift_all_amount)
            gift_item = {
                "gift_id": gift_id,
                "gift_name": row[1],
                "gift_num": row[2],
                "all_amount": gift_all_amount,
                "goods_list": goods_list
            }
            gift_list.append(gift_item)

        df = pd.DataFrame(gift_list)
        df = df.to_json(orient='records')
        return df



