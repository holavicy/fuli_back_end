import pymssql
import pandas as pd


class SuggestModel(object):

    conn_ss = pymssql.connect(host='192.168.40.229:1433', port=3306, user='serverapp', password='wetown2020',
                              database='GiftDB')

    # 获取所有建议选项
    @classmethod
    def get_suggest_dict(cls):
        sql = "SELECT * FROM suggest_dict sd WHERE sd.status = 1"
        df_records = pd.read_sql(sql, con=cls.conn_ss)
        df_records = df_records.to_json(orient='records', date_format='iso', date_unit='s')

        return df_records

    # 新增员工提交的建议
    @classmethod
    def create_suggest(cls, suggest_ids, text, staff_no, staff_name):
        try:
            suggest_id_list = suggest_ids.split(",")

            cursor = cls.conn_ss.cursor()
            for suggest_id in suggest_id_list:
                base_sql = "insert into dbo.[suggests] ({}) values ({})"
                sql_item = ['suggest_id', 'staff_no', 'staff_name']
                sql_values = ["\'" + suggest_id + "\'", "\'" + staff_no + "\'", "\'" + staff_name + "\'"]
                if suggest_id == '9':
                    sql_item.append('text')
                    sql_values.append("\'"+text+"\'")
                sql = base_sql.format(','.join(sql_item), ','.join(list(map(str, sql_values))))
                cursor.execute(sql)
            cls.conn_ss.commit()
            cursor.close()
            return True
        except Exception as e:
            print(e)
            cls.conn_ss.rollback()
            return False
