import json
import tornado
from tornado.escape import json_encode
from handlers.base import BaseHandler
from models.giftBag import GiftBagModel


class GiftBagListHandler(BaseHandler):

    # 查询礼包
    def get(self):
        page = self.get_argument('page')
        page_size = self.get_argument('pageSize')
        gift_name = self.get_argument('giftName')
        goods_name = self.get_argument('goodsName')
        gift_status = self.get_argument('giftStatus')
        staff_no = self.get_argument('staffNo')

        response = {
            'code': 0,
            'data': '',
            'errorMsg': ''
        }

        total_num, df_records = GiftBagModel.get_all(page, page_size, gift_name, goods_name, gift_status, staff_no)
        if isinstance(total_num, int):
            total_num = total_num
        else:
            total_num = total_num.tolist()
        data = {
            'count': total_num,
            'list': json.loads(df_records)
        }
        response['data'] = data
        self.write(json_encode(response))

    # 新增礼包
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        response = {
            'code': 0,
            'data': '',
            'errorMsg': ''
        }

        response_flag = GiftBagModel.create_gift_bag(data)
        if response_flag:
            self.write(json_encode(response))
        else:
            response['code'] = -1
            response['errorMsg'] = '数据库错误，请联系管理员'
            self.write(json_encode(response))


class GiftBagStatusHandler(BaseHandler):

    # 修改礼包状态
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        response = {
            'code': 0,
            'data': '',
            'errorMsg': ''
        }
        gift_bag_id = data['id']
        status = data['status']
        staff_no = data['staffNo']

        response_flag = GiftBagModel.edit_gift_bag_status(gift_bag_id, status, staff_no)

        if response_flag:
            self.write(json_encode(response))
        else:
            response['code'] = -1
            response['errorMsg'] = '更新失败，数据库错误，请联系管理员'
            self.write(json_encode(response))


class GiftBagHandler(BaseHandler):

    # 修改礼包信息
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        response = {
            'code': 0,
            'data': '',
            'errorMsg': ''
        }

        response_flag = GiftBagModel.edit_gift_bag_info(data)

        if response_flag:
            self.write(json_encode(response))
        else:
            response['code'] = -1
            response['errorMsg'] = '更新失败，数据库错误，请联系管理员'
            self.write(json_encode(response))
