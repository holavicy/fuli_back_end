import pymssql
import pandas as pd
import cx_Oracle
import re
import json
import numpy as np
from models.chart import ChartModel


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
        try:
            sql = "select ss.code, ss.name, ss.birthdate,c.hiredate, jr.jobrankcode\
    from bd_psndoc ss\
    inner join hi_psnjob job on ss.pk_psndoc = job.pk_psndoc\
    inner join om_jobrank jr on jr.pk_jobrank = job.pk_jobrank\
    left join (\
      select a.clerkcode, min(a.begindate) as hiredate \
      from hi_psnjob a \
      left join bd_psncl b on a.pk_psncl = b.pk_psncl \
      where b.name = '全职' group by a.clerkcode) c on c.clerkcode = ss.code \
    where job.endflag = 'N'\
    and job.ismainjob = 'Y'\
    and job.lastflag = 'Y'\
    and ss.code = '%s'" % (code)
            print(sql)
            df_records = pd.read_sql(sql, con=cls.db_nc)
            df_records = df_records.to_json(orient='records')
            print(df_records)
            return df_records
        except Exception as e:
            print(e)

    # 获取所有可领取生日礼包的人员
    @classmethod
    def get_user_list(cls, page, page_size, staff_no, name, get_status, get_year):

        try:

            staff_no_sql = ''
            name_sql = ''
            get_year_sql = ''
            if staff_no:
                staff_no_sql = f'AND ss.code = \'{staff_no}\''
            if name:
                name_sql = f'AND ss.name like \'%{name}%\''
            if get_year:
                get_year_sql = f'and b.zzdate <= \'{get_year}\''

            un_supply_user_list = []  # 未申请
            un_confirm_user_list = [] # 已申请待管理员确认
            un_got_user_list = [] # 待领取
            got_user_list = [] # 已领取

            template = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
            re.sub(template, r"\1-01-01", get_year)
            begin_date = re.sub(template, r"\1-01-01", get_year)
            end_date = re.sub(template, r"\1-12-31", get_year)
            year = re.sub(template, r"\1", get_year)

            print(year)

            # records_sql = "select ss.pk_psndoc, ss.code, ss.name, ss.birthdate, b.zzdate from (select ss.pk_psndoc from bd_psndoc ss inner join hi_psnjob job on job.pk_psndoc = ss.pk_psndoc inner join bd_psncl jt on jt.pk_psncl = job.pk_psncl where ss.enablestate = 2 and job.endflag = 'N' and job.poststat = 'Y' and jt.name in ('正式员工','全职','车间在职', '试用期员工', '退休返聘') group by ss.pk_psndoc, ss.name having ss.name not like '%测试%') a join ( \
            #     select job.pk_psndoc, min(job.begindate) as zzdate from hi_psnjob job join bd_psncl jt on job.pk_psncl = jt.pk_psncl where jt.name in ('正式员工','全职','车间在职', '退休返聘') group by job.pk_psndoc) b on a.pk_psndoc = b.pk_psndoc \
            #     join bd_psndoc ss on ss.pk_psndoc = a.pk_psndoc where ss.pk_psndoc not in ( select ss.pk_psndoc from bd_psndoc ss \
            #     left join hi_psnjob job on ss.pk_psndoc = job.pk_psndoc left join org_dept dp on dp.pk_dept = job.pk_dept left join org_dept fdp on fdp.pk_dept = dp.pk_fatherorg \
            #     where job.endflag = 'N' and job.ismainjob = 'Y'and (dp.name in ('电商运营部')or fdp.name in ('广州研发中心')or ss.name in ('王署斌', '龚培春'))) " + staff_no_sql + name_sql + get_year_sql + " order by ss.code"

            records_sql = f'select org.name as orgName, ' \
                f'ss.name, ' \
                f'ss.code, ' \
                f'ss.birthdate,' \
                f'REGEXP_REPLACE (ss.birthdate,\'(\\d{{{4}}})-(\\d{{{2}}})-(\\d{{{2}}})\',\'{year}-\\2-\\3\') AS thisYearBitth, ' \
                f'b.zzdate, ' \
                f'dp.name, ' \
                f'dp2.name as dp2name,' \
                f'{year} - (REGEXP_SUBSTR(ss.birthdate,\'(\d){{{4}}}\')) + 1 as age ,' \
                f'ss.mobile, job.pk_dept ' \
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
                f'and ss.name not in (\'王署斌\', \'龚培春\') ' \
                f'and ss.name not like \'%测试%\' ' \
                f'and jt.name in (\'正式员工\',\'全职\',\'车间在职\', \'试用期员工\', \'退休返聘\') ' \
                f'and b.zzdate <= REGEXP_REPLACE (ss.birthdate,\'(\\d{{{4}}})-(\\d{{{2}}})-(\\d{{{2}}})\',\'{year}-\\2-\\3\') ' \
                f'and mod({year}- (REGEXP_SUBSTR(ss.birthdate,\'(\\d){{{4}}}\')) + 1 , 10) != 0 ' \
                f'{staff_no_sql}' \
                f'{name_sql}' \
                f'order by og.name, org.name, ss.code'

            print(records_sql)

            df_records = pd.read_sql(records_sql, con=cls.db_nc)

            for index, row in df_records.iterrows():
                staff_no = row[2]
                user_item = {}
                user_item['CODE'] = staff_no
                user_item['NAME'] = row[1]
                user_item['BIRTHDATE'] = row[3]
                user_item['THISYEARBIRTH'] = row[4]
                user_item['ZZDATE'] = row[5]
                user_item['mobile'] = row[9]
                user_item['group'] = row[0]

                dept_list = ChartModel.get_dept_list(row[10], [])
                user_item['dept_list'] = dept_list

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
                    # 已申请待管理员确认
                    if order_status == 1:
                        un_confirm_user_list.append(user_item)
                    # 待领取
                    elif order_status == 3:
                        un_got_user_list.append(user_item)
                    # 已领取
                    elif order_status == 4:
                        got_user_list.append(user_item)
                # 没有订单代表没有申请
                else:
                    un_supply_user_list.append(user_item)
            user_list = []
            if get_status:
                if '1' in get_status:
                    user_list = user_list + un_supply_user_list
                if '2' in get_status:
                    user_list = user_list + un_confirm_user_list
                if '3' in get_status:
                    user_list = user_list + un_got_user_list
                if '4' in get_status:
                    user_list = user_list + got_user_list
            else:
                user_list = un_supply_user_list + un_confirm_user_list + un_got_user_list + got_user_list

            total_num = len(user_list)

            if page and page_size:
                min_top = (int(page) - 1) * int(page_size)
                max_top = int(page) * int(page_size)
                user_list = user_list[min_top:max_top]

            df = pd.DataFrame(user_list)
            df = df.to_json(orient='records')

            return total_num, df

        except Exception as e:
            print(e)

    # 获取所有整生日的人员
    @classmethod
    def get_z_birth_user_list(cls, page, page_size, staff_no, name, get_year):

        try:
            staff_no_sql = ''
            name_sql = ''

            if staff_no:
                staff_no_sql = f'AND ss.code = \'{staff_no}\''
            if name:
                name_sql = f'AND ss.name like \'%{name}%\''

            template = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
            re.sub(template, r"\1-01-01", get_year)
            year = re.sub(template, r"\1", get_year)

            print(year)

            records_sql = f'select org.name as orgName, ' \
                f'ss.name, ' \
                f'ss.code, ' \
                f'ss.birthdate,' \
                f'REGEXP_REPLACE (ss.birthdate,\'(\\d{{{4}}})-(\\d{{{2}}})-(\\d{{{2}}})\',\'{year}-\\2-\\3\') AS thisYearBitth, ' \
                f'b.zzdate, ' \
                f'dp.name, ' \
                f'dp2.name as dp2name,' \
                f'{year} - (REGEXP_SUBSTR(ss.birthdate,\'(\d){{{4}}}\')) + 1 as age ,' \
                f'ss.mobile, job.pk_dept ' \
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
                f'and ss.name not in (\'王署斌\', \'龚培春\') ' \
                f'and ss.name not like \'%测试%\' ' \
                f'and jt.name in (\'正式员工\',\'全职\',\'车间在职\', \'试用期员工\', \'退休返聘\') ' \
                f'and b.zzdate <= REGEXP_REPLACE (ss.birthdate,\'(\\d{{{4}}})-(\\d{{{2}}})-(\\d{{{2}}})\',\'{year}-\\2-\\3\') ' \
                f'and mod({year}- (REGEXP_SUBSTR(ss.birthdate,\'(\\d){{{4}}}\')) + 1 , 10) = 0 ' \
                f'{staff_no_sql}' \
                f'{name_sql}' \
                f'order by og.name, org.name, ss.code'

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
                user_item['mobile'] = row[9]
                user_item['group'] = row[0]

                dept_list = ChartModel.get_dept_list(row[10], [])
                user_item['dept_list'] = dept_list

                user_list.append(user_item)

            total_num = len(user_list)

            if page and page_size:
                min_top = (int(page) - 1) * int(page_size)
                max_top = int(page) * int(page_size)
                user_list = user_list[min_top:max_top]

            df = pd.DataFrame(user_list)
            df = df.to_json(orient='records')

            return total_num, df

        except Exception as e:
            print(e)
