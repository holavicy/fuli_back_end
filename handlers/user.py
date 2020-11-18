import json
import tornado
from tornado.escape import json_encode
from handlers.base import BaseHandler
from models.user import UserModel


class UserInfoHandler(BaseHandler):

    # 查询礼包
    def get(self):
        code = self.get_argument('code')

        response = {
            'code': 0,
            'data': '',
            'errorMsg': ''
        }

        df_records = UserModel.get_user_info(code)
        data = {
            'list': json.loads(df_records)
        }
        response['data'] = data
        self.write(json_encode(response))