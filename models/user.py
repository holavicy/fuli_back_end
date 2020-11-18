import pymssql
import pandas as pd
import cx_Oracle


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
