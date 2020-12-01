import pymssql
import pandas as pd
import cx_Oracle
import re
import json
import numpy as np


class UserModel(object):
    ncDbInfo = {
        "user": "nc633_rebulid",
        "password": "nc633_123",
        "db": "wtdb",
        "host": "192.168.40.230",
        "port": "1521",
    }
    conn_ss = pymssql.connect(host='192.168.40.229:1433', port=3306, user='serverapp', password='wetown2020',
                              database='GiftDB')
    db_nc = cx_Oracle.connect(
        f'{ncDbInfo["user"]}/{ncDbInfo["password"]}@{ncDbInfo["host"]}:{ncDbInfo["port"]}/{ncDbInfo["db"]}',
        encoding="UTF-8", nencoding="UTF-8")

    # 获取NC中bd_psndoc员工基本信息
    @classmethod
    def get_user_info(cls, code):
        sql = "select ss.code, ss.name, ss.birthdate,c.hiredate from bd_psndoc ss left join (select a.clerkcode, min(a.begindate) as hiredate from hi_psnjob a left join bd_psncl b on a.pk_psncl = b.pk_psncl where b.name = '全职' group by a.clerkcode) c on c.clerkcode = ss.code where ss.code = '%s'" % (code)
        df_records = pd.read_sql(sql, con=cls.db_nc)
        df_records = df_records.to_json(orient='records')
        print(df_records)
        return df_records

    # 获取所有可领取生日礼包的人员
    @classmethod
    def get_user_list(cls, page, page_size, staff_no, name, get_status, get_year):
        staff_no_sql = ''
        name_sql = ''
        get_year_sql = ''
        if staff_no:
            staff_no_sql = f'AND ss.code = \'{staff_no}\''
        if name:
            name_sql = f'AND ss.name like \'%{name}%\''
        if get_year:
            get_year_sql = f'and b.zzdate <= \'{get_year}\''

        got_user_list = []
        un_got_user_list = []
        template = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
        re.sub(template, r"\1-01-01", get_year)
        begin_date = re.sub(template, r"\1-01-01", get_year)
        end_date = re.sub(template, r"\1-12-31", get_year)
        year = re.sub(template, r"\1", get_year)


        records_sql = "select ss.pk_psndoc, ss.code, ss.name, ss.birthdate, b.zzdate from (select ss.pk_psndoc from bd_psndoc ss inner join hi_psnjob job on job.pk_psndoc = ss.pk_psndoc inner join bd_psncl jt on jt.pk_psncl = job.pk_psncl where ss.enablestate = 2 and job.endflag = 'N' and job.poststat = 'Y' and jt.name in ('正式员工','全职','车间在职', '试用期员工', '退休返聘') group by ss.pk_psndoc, ss.name having ss.name not like '%测试%') a join ( \
            select job.pk_psndoc, min(job.begindate) as zzdate from hi_psnjob job join bd_psncl jt on job.pk_psncl = jt.pk_psncl where jt.name in ('正式员工','全职','车间在职', '退休返聘') group by job.pk_psndoc) b on a.pk_psndoc = b.pk_psndoc \
            join bd_psndoc ss on ss.pk_psndoc = a.pk_psndoc where ss.pk_psndoc not in ( select ss.pk_psndoc from bd_psndoc ss \
            left join hi_psnjob job on ss.pk_psndoc = job.pk_psndoc left join org_dept dp on dp.pk_dept = job.pk_dept left join org_dept fdp on fdp.pk_dept = dp.pk_fatherorg \
            where job.endflag = 'N' and job.ismainjob = 'Y'and (dp.name in ('电商运营部')or fdp.name in ('广州研发中心')or ss.name in ('王署斌', '龚培春'))) " + staff_no_sql + name_sql + get_year_sql + " order by ss.code"

        df_records = pd.read_sql(records_sql, con=cls.db_nc)

        for index, row in df_records.iterrows():
            user_item = {}
            user_item['CODE'] = row[1]
            user_item['NAME'] = row[2]
            user_item['BIRTHDATE'] = row[3]
            user_item['ZZDATE'] = row[4]

            order_sql = '''SELECT *  from [order] o where o.status != 2 and o.create_time >= '%s' and o.create_time <= '%s' and o.staff_no = '%s' ''' % (begin_date, end_date, row[1])
            df_order = pd.read_sql(order_sql, con=cls.conn_ss)
            got_num = len(df_order)
            user_item['GOTNUM'] = got_num
            user_item['isOthers'] = '否'

            # 到other_supply中查询记录  若存在则设置了代领，若不存在则没有设置代领
            supply_sql = "SELECT * from others_supply osp WHERE osp.status = 1 AND osp.staff_no = '%s 'AND osp.year = '%s'" %(row[1], year)
            df_supply = pd.read_sql(supply_sql, con=cls.conn_ss)
            supply_num = len(df_supply)
            df_supply = df_supply.to_json(orient='records')
            df_supply = json.loads(df_supply)

            if supply_num > 0:
                user_item['isOthers'] = '是'
                user_item['othersName'] = df_supply[0]['can_supply_name']
                user_item['othersStaffNo'] = df_supply[0]['can_supply_staff_no']

            if got_num > 0:
                got_user_list.append(user_item)
            else:
                un_got_user_list.append(user_item)

        if get_status == '1':
            user_list = got_user_list
        elif get_status == '2':
            user_list = un_got_user_list
        else:
            user_list = got_user_list + un_got_user_list
        total_num = len(user_list)

        if page and page_size:
            min_top = (int(page) - 1) * int(page_size)
            max_top = int(page) * int(page_size)
            user_list = user_list[min_top:max_top]

        df = pd.DataFrame(user_list)
        df = df.to_json(orient='records')

        return total_num, df
