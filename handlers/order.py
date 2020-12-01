import json
import tornado
from tornado.escape import json_encode
from handlers.base import BaseHandler
from models.order import OrderModel


class OrderListHandler(BaseHandler):

    # 创建订单
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        response = {
            'code': 0,
            'data': '',
            'errorMsg': ''
        }

        response_flag = OrderModel.create_order(data)
        if response_flag == 1:
            response['code'] = -1
            response['errorMsg'] = '您已申请了今年的生日礼包，请勿重新申请'
            self.write(json_encode(response))
        elif response_flag == 2:
            self.write(json_encode(response))
        else:
            response['code'] = -1
            response['errorMsg'] = '数据库错误，请联系管理员'
            self.write(json_encode(response))

    # 获取订单列表
    def get(self):
        page = self.get_argument('page')
        page_size = self.get_argument('pageSize')
        staff_no = self.get_argument('staffNo')
        year = self.get_argument('year')
        order_status = self.get_argument('orderStatus')
        creator = self.get_argument('creator')
        creator_name = self.get_argument('creatorName')
        staff_name = self.get_argument('staffName')

        response = {
            'code': 0,
            'data': '',
            'errorMsg': ''
        }

        total_num, df_records = OrderModel.get_all(page, page_size, staff_no, year, order_status, creator, creator_name, staff_name)
        data = {
            'count': total_num.tolist(),
            'list': json.loads(df_records)
        }
        response['data'] = data
        self.write(json_encode(response))


class OrderStatusHandler(BaseHandler):

    # 修改订单状态 3：待领取 4 已完成 5已取消
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        response = {
            'code': 0,
            'data': '',
            'errorMsg': ''
        }
        order_id = data['orderId']
        status = data['status']
        staff_no = data['staffNo']
        staff_name = data['staffName']

        response_flag = OrderModel.edit_order_status(order_id, status, staff_no, staff_name)

        if response_flag:
            self.write(json_encode(response))
        else:
            response['code'] = -1
            response['errorMsg'] = '更新失败，数据库错误，请联系管理员'
            self.write(json_encode(response))


class OrderOthersHandler(BaseHandler):

    # 获取代他人领取订单列表
    def get(self):
        page = self.get_argument('page')
        page_size = self.get_argument('pageSize')
        creator = self.get_argument('creator')
        year = self.get_argument('year')
        order_status = self.get_argument('orderStatus')

        response = {
            'code': 0,
            'data': '',
            'errorMsg': ''
        }

        total_num, df_records = OrderModel.get_others(page, page_size, creator, year, order_status)
        data = {
            'count': total_num.tolist(),
            'list': json.loads(df_records)
        }
        response['data'] = data
        self.write(json_encode(response))
