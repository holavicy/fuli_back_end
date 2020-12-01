import json
import tornado
from tornado.escape import json_encode
from handlers.base import BaseHandler
from models.suggest import SuggestModel


class SuggestDictListHandler(BaseHandler):

    # 获取建议选项列表
    def get(self):

        response = {
            'code': 0,
            'data': '',
            'errorMsg': ''
        }

        df_records = SuggestModel.get_suggest_dict()
        data = {
            'list': json.loads(df_records)
        }
        response['data'] = data
        self.write(json_encode(response))


class SuggestListHandler(BaseHandler):
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        response = {
            'code': 0,
            'data': '',
            'errorMsg': ''
        }
        suggest_ids = data['suggestIds']
        staff_no = data['staffNo']
        staff_name = data['staffName']
        text = data['text']

        response_flag = SuggestModel.create_suggest(suggest_ids, text, staff_no, staff_name)

        if response_flag:
            self.write(json_encode(response))
        else:
            response['code'] = -1
            response['errorMsg'] = '提交失败，数据库错误，请联系管理员'
            self.write(json_encode(response))