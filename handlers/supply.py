import json
import tornado
from tornado.escape import json_encode
from handlers.base import BaseHandler
from models.supply import SupplyModel


class SupplyListHandler(BaseHandler):

    # 创建代领
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        response = {
            'code': 0,
            'data': '',
            'errorMsg': ''
        }

        response_flag = SupplyModel.create_supply(data)
        if response_flag:
            self.write(json_encode(response))
        else:
            response['code'] = -1
            response['errorMsg'] = '数据库错误，请联系管理员'
            self.write(json_encode(response))

    # 获取代领列表
    def get(self):
        page = self.get_argument('page')
        page_size = self.get_argument('pageSize')
        staff_no = self.get_argument('staffNo')
        year = self.get_argument('year')
        supply_staff_no = self.get_argument('supplyStaffNo')

        response = {
            'code': 0,
            'data': '',
            'errorMsg': ''
        }

        total_num, df_records = SupplyModel.get_all(page, page_size, staff_no, year, supply_staff_no)
        data = {
            'count': total_num.tolist(),
            'list': json.loads(df_records)
        }
        response['data'] = data
        self.write(json_encode(response))


class SupplyStatusHandler(BaseHandler):

    # 取消代领
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        response = {
            'code': 0,
            'data': '',
            'errorMsg': ''
        }

        response_flag = SupplyModel.update_supply_status(data)
        if response_flag:
            self.write(json_encode(response))
        else:
            response['code'] = -1
            response['errorMsg'] = '数据库错误，请联系管理员'
            self.write(json_encode(response))
