import json
import tornado
from tornado.escape import json_encode
from handlers.base import BaseHandler
from models.like import LikeModel


class LikeListHandler(BaseHandler):

    # 新增喜欢
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        response = {
            'code': 0,
            'data': '',
            'errorMsg': ''
        }

        response_flag = LikeModel.create_like(data)
        if response_flag:
            self.write(json_encode(response))
        else:
            response['code'] = -1
            response['errorMsg'] = '数据库错误，请联系管理员'
            self.write(json_encode(response))

    # 获取喜欢列表
    def get(self):
        staff_no = self.get_argument('staffNo')
        goods_id = self.get_argument('goodsId')

        response = {
            'code': 0,
            'data': '',
            'errorMsg': ''
        }

        total_num, df_records = LikeModel.get_all(staff_no, goods_id)
        data = {
            'count': total_num.tolist(),
            'list': json.loads(df_records)
        }
        response['data'] = data
        self.write(json_encode(response))


class CancelLikeHandler(BaseHandler):
    # 取消喜欢
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        response = {
            'code': 0,
            'data': '',
            'errorMsg': ''
        }

        response_flag = LikeModel.cancel_like(data)
        if response_flag:
            self.write(json_encode(response))
        else:
            response['code'] = -1
            response['errorMsg'] = '数据库错误，请联系管理员'
            self.write(json_encode(response))