import pymssql
import pandas as pd
import cx_Oracle
import re
import json
import numpy as np
import datetime

class TaskModel(object):
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

    # 获取一周后过生日的人
    @classmethod
    def get_next_week_birth_user_list(cls):

        try:
            today = datetime.date.today()
            next_week = today + datetime.timedelta(days=7)

            year = datetime.datetime.now().year

            begin_date = str(year)+'-01-01'
            end_date = str(year) + '-12-31'

            print(year)
            flag = datetime.datetime.strptime(str(today), '%Y-%m-%d') == datetime.datetime.strptime(begin_date,
                                                                                                    "%Y-%m-%d")
            sql = ''
            if flag:
                sql = "<=" + "\'" + str(next_week) + "\'"
            else:
                sql = '=' + "\'" + str(next_week) + "\'"

            records_sql = f'select org.name as orgName, ss.name, ss.code, ss.birthdate,REGEXP_REPLACE (ss.birthdate,\'(\\d{{{4}}})-(\\d{{{2}}})-(\\d{{{2}}})\',\'{year}-\\2-\\3\') AS thisYearBitth, b.zzdate, dp.name, dp2.name as dp2name,{year} - (REGEXP_SUBSTR(ss.birthdate,\'(\d){{{4}}}\')) + 1 as age ' \
                    f'from bd_psndoc ss ' \
                    f'inner join hi_psnjob job on ss.pk_psndoc = job.pk_psndoc ' \
                    f'inner join bd_psncl jt on jt.pk_psncl = job.pk_psncl ' \
                    f'inner join (select job.pk_psndoc, min(job.begindate) as zzdate from hi_psnjob job join bd_psncl jt on job.pk_psncl = jt.pk_psncl where jt.name in (\'正式员工\',\'全职\',\'车间在职\', \'退休返聘\') group by job.pk_psndoc) b on ss.pk_psndoc = b.pk_psndoc ' \
                    f'left join org_dept dp on dp.pk_dept = job.pk_dept ' \
                    f'left join org_dept dp2 on dp.pk_fatherorg = dp2.pk_dept ' \
                    f'left join org_group og on dp.pk_group = og.pk_group ' \
                    f'left join org_orgs org on dp.pk_org = org.pk_org ' \
                    f'where job.endflag = \'N\' and job.ismainjob = \'Y\' ' \
                    f'and job.lastflag = \'Y\' ' \
                    f'and org.pk_org in (\'0001A31000000002DQ1F\', \'0001A31000000002ETZ6\', \'0001A31000000002FDIG\', \'0001V1100000002GOO1A\', \'0001V1100000002A7G5J\', \'0001A31000000002DQ2O\', \'0001A310000000074BK7\') ' \
                    f'and (dp2.name not in (\'广州研发中心\') or dp2.name is null ) ' \
                    f'and (dp.name not in (\'电商运营部\') or dp.name is null) ' \
                    f'and ss.name not in (\'王署斌\', \'龚培春\', \'施国斌\') ' \
                    f'and ss.name not like \'%测试%\' ' \
                    f'and jt.name in (\'正式员工\',\'全职\',\'车间在职\', \'试用期员工\', \'退休返聘\') ' \
                    f'and b.zzdate <= REGEXP_REPLACE (ss.birthdate,\'(\\d{{{4}}})-(\\d{{{2}}})-(\\d{{{2}}})\',\'{year}-\\2-\\3\') ' \
                    f'and REGEXP_REPLACE (ss.birthdate,\'(\\d{{{4}}})-(\\d{{{2}}})-(\\d{{{2}}})\',\'{year}-\\2-\\3\')  <= \'{end_date}\' '\
                    f'and REGEXP_REPLACE (ss.birthdate,\'(\\d{{{4}}})-(\\d{{{2}}})-(\\d{{{2}}})\',\'{year}-\\2-\\3\')  {sql} '

            print(records_sql)

            df_records = pd.read_sql(records_sql, con=cls.db_nc)
            user_list = []

            for index, row in df_records.iterrows():
                staff_no = row[2]
                user_item = {}
                user_item['CODE'] = staff_no
                user_item['NAME'] = row[1]
                user_item['BIRTHDATE'] = row[3]
                user_item['THISYEARBIRTH'] = row[4]
                user_item['ZZDATE'] = row[5]

                user_item['isOthers'] = '否' # 是否已设置他人代领

                # 到other_supply中查询记录  若存在则设置了代领，若不存在则没有设置代领
                supply_sql = "SELECT * from others_supply osp WHERE osp.status = 1 AND osp.staff_no = '%s 'AND osp.year = '%s'" %(staff_no, year)
                df_supply = pd.read_sql(supply_sql, con=cls.conn_ss)
                supply_num = len(df_supply)
                df_supply = df_supply.to_json(orient='records')
                df_supply = json.loads(df_supply)

                if supply_num > 0:
                    user_item['isOthers'] = '是'
                    user_item['othersName'] = df_supply[0]['can_supply_name']
                    user_item['othersStaffNo'] = df_supply[0]['can_supply_staff_no']

                # 查询某人某年礼包领取状态
                order_sql = '''SELECT *  from [order] o where o.status != 2 and o.create_time >= '%s' and o.create_time <= '%s' and o.staff_no = '%s' ''' % (
                begin_date, end_date, staff_no)
                df_order = pd.read_sql(order_sql, con=cls.conn_ss)
                got_num = len(df_order)
                user_item['GOTNUM'] = got_num

                if got_num > 0:
                    order_status = df_order['status'][0]
                    user_item['ORDERSTATUS'] = order_status
                user_list.append(user_item)

            df = pd.DataFrame(user_list)
            df = df.to_json(orient='records')

            return df

        except Exception as e:
            print(e)

    # 获取今天之前应该申请、领取还未申请、领取的人(除去整生日)
    @classmethod
    def get_un_finish_user_list(cls):

        try:
            today = datetime.date.today()
            year = datetime.datetime.now().year
            begin_date = str(year)+'-01-01'
            end_date = str(year) + '-12-31'

            print(year)

            records_sql = f'select org.name as orgName, ss.name, ss.code, ss.birthdate,REGEXP_REPLACE (ss.birthdate,\'(\\d{{{4}}})-(\\d{{{2}}})-(\\d{{{2}}})\',\'{year}-\\2-\\3\') AS thisYearBitth, b.zzdate, dp.name, dp2.name as dp2name,{year} - (REGEXP_SUBSTR(ss.birthdate,\'(\d){{{4}}}\')) + 1 as age ' \
                    f'from bd_psndoc ss ' \
                    f'inner join hi_psnjob job on ss.pk_psndoc = job.pk_psndoc ' \
                    f'inner join bd_psncl jt on jt.pk_psncl = job.pk_psncl ' \
                    f'inner join (select job.pk_psndoc, min(job.begindate) as zzdate from hi_psnjob job join bd_psncl jt on job.pk_psncl = jt.pk_psncl where jt.name in (\'正式员工\',\'全职\',\'车间在职\', \'退休返聘\') group by job.pk_psndoc) b on ss.pk_psndoc = b.pk_psndoc ' \
                    f'left join org_dept dp on dp.pk_dept = job.pk_dept ' \
                    f'left join org_dept dp2 on dp.pk_fatherorg = dp2.pk_dept ' \
                    f'left join org_group og on dp.pk_group = og.pk_group ' \
                    f'left join org_orgs org on dp.pk_org = org.pk_org ' \
                    f'where job.endflag = \'N\' and job.ismainjob = \'Y\' ' \
                    f'and job.lastflag = \'Y\' ' \
                    f'and org.pk_org in (\'0001A31000000002DQ1F\', \'0001A31000000002ETZ6\', \'0001A31000000002FDIG\', \'0001V1100000002GOO1A\', \'0001V1100000002A7G5J\', \'0001A31000000002DQ2O\', \'0001A310000000074BK7\') ' \
                    f'and (dp2.name not in (\'广州研发中心\') or dp2.name is null ) ' \
                    f'and (dp.name not in (\'电商运营部\') or dp.name is null) ' \
                    f'and ss.name not in (\'王署斌\', \'龚培春\', \'施国斌\') ' \
                    f'and ss.name not like \'%测试%\' ' \
                    f'and jt.name in (\'正式员工\',\'全职\',\'车间在职\', \'试用期员工\', \'退休返聘\') ' \
                    f'and b.zzdate <= REGEXP_REPLACE (ss.birthdate,\'(\\d{{{4}}})-(\\d{{{2}}})-(\\d{{{2}}})\',\'{year}-\\2-\\3\') ' \
                    f'and mod({year}- (REGEXP_SUBSTR(ss.birthdate,\'(\\d){{{4}}}\')) + 1 , 10) != 0 ' \
                    f'and REGEXP_REPLACE (ss.birthdate,\'(\\d{{{4}}})-(\\d{{{2}}})-(\\d{{{2}}})\',\'{year}-\\2-\\3\')  < \'{today}\' '

            print(records_sql)

            df_records = pd.read_sql(records_sql, con=cls.db_nc)
            user_list = []

            for index, row in df_records.iterrows():
                staff_no = row[2]
                user_item = {}
                user_item['CODE'] = staff_no
                user_item['NAME'] = row[1]
                user_item['BIRTHDATE'] = row[3]
                user_item['THISYEARBIRTH'] = row[4]
                user_item['ZZDATE'] = row[5]

                user_item['isOthers'] = '否' # 是否已设置他人代领

                # 到other_supply中查询记录  若存在则设置了代领，若不存在则没有设置代领
                supply_sql = "SELECT * from others_supply osp WHERE osp.status = 1 AND osp.staff_no = '%s 'AND osp.year = '%s'" %(staff_no, year)
                df_supply = pd.read_sql(supply_sql, con=cls.conn_ss)
                supply_num = len(df_supply)
                df_supply = df_supply.to_json(orient='records')
                df_supply = json.loads(df_supply)

                if supply_num > 0:
                    user_item['isOthers'] = '是'
                    user_item['othersName'] = df_supply[0]['can_supply_name']
                    user_item['othersStaffNo'] = df_supply[0]['can_supply_staff_no']

                # 查询某人某年礼包领取状态
                order_sql = '''SELECT *  from [order] o where o.status != 2 and o.create_time >= '%s' and o.create_time <= '%s' and o.staff_no = '%s' ''' % (
                begin_date, end_date, staff_no)
                df_order = pd.read_sql(order_sql, con=cls.conn_ss)
                got_num = len(df_order)
                user_item['GOTNUM'] = got_num

                if got_num > 0:
                    order_status = df_order['status'][0]
                    user_item['ORDERSTATUS'] = order_status
                    if order_status == 3:
                        user_list.append(user_item)
                else:
                    user_list.append(user_item)

            df = pd.DataFrame(user_list)
            df = df.to_json(orient='records')

            return df

        except Exception as e:
            print(e)
