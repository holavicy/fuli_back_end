import pymssql
import pandas as pd
from common.tool import get_now


class ChartModel(object):
    conn_ss = pymssql.connect(host='192.168.40.229:1433', port=3306, user='serverapp', password='wetown2020',
                              database='GiftDB')

    @classmethod
    def gift_summary(cls, year):
        sql = "SELECT o.gift_id, o.gift_name, COUNT(*) as num FROM [order] o WHERE o.status !=2 AND o.[year] = '%s' GROUP BY o.gift_id, o.gift_name ORDER BY num desc;" % (year)
        result_list = pd.read_sql(sql, con=cls.conn_ss)
        return result_list
