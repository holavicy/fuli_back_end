import json
import tornado
from tornado.escape import json_encode
from handlers.base import BaseHandler
from models.like import LikeModel


class LikeListHandler(BaseHandler):

    # 新增礼包
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
