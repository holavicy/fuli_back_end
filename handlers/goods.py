import json
import tornado
from tornado.escape import json_encode
from models.goods import GoodsModel
from handlers.base import BaseHandler


class GoodsListHandler(BaseHandler):
    # 获取商品列表
    def get(self):
        page = self.get_argument('page')
        page_size = self.get_argument('pageSize')
        name = self.get_argument('goodsName')
        status = self.get_argument('goodsStatus')

        response = {
            'code': 0,
            'data': '',
            'errorMsg': ''
        }

        total_num, df_records = GoodsModel.get_all(page, page_size, name, status)
        data = {
            'count': total_num.tolist(),
            'list': json.loads(df_records)
        }
        response['data'] = data
        self.write(json_encode(response))

    # 新增商品
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        response = {
            'code': 0,
            'data': '',
            'errorMsg': ''
        }
        goods_info = {
            'name': data['name'],
            'unit': data['unit'],
            'image_url': data['imageUrl'],
            'price': data['price']
        }
        num = data['num']
        staff_no = data['staffNo']

        response_flag = GoodsModel.create_goods(goods_info, num, staff_no)

        if response_flag:
            self.write(json_encode(response))
        else:
            response['code'] = -1
            response['errorMsg'] = '数据库错误，请联系管理员'
            self.write(json_encode(response))


class GoodsStatusHandler(BaseHandler):
    # 修改商品状态 status 1：上架 2：删除 3：下架
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        response = {
            'code': 0,
            'data': '',
            'errorMsg': ''
        }
        goods_id = data['id']
        status = data['status']
        staff_no = data['staffNo']

        # response_flag: 1.属于某个礼包 2.下架成功 3 下架失败
        response_flag = GoodsModel.edit_goods_status(goods_id, status, staff_no)
        print(response_flag)

        if response_flag == 1:
            response['code'] = -1
            response['errorMsg'] = '商品属于某个礼包，请先将此商品从礼包中移除，再进行操作'
            self.write(json_encode(response))
        elif response_flag == 2:
            self.write(json_encode(response))
        else:
            response['code'] = -1
            response['errorMsg'] = '更新失败，数据库错误，请联系管理员'
            self.write(json_encode(response))


class GoodsHandler(BaseHandler):
    # 修改商品基础信息（名称、单位、单价、图片）
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        response = {
            'code': 0,
            'data': '',
            'errorMsg': ''
        }

        name = data['name']
        unit = data['unit']
        price = data['price']
        image_url = data['imageUrl']
        update_by = data['staffNo']
        goods_id = data['id']

        response_flag = GoodsModel.edit_goods_info(goods_id, name, unit, price, image_url, update_by)

        if response_flag:
            self.write(json_encode(response))
        else:
            response['code'] = -1
            response['errorMsg'] = '更新失败，数据库错误，请联系管理员'
            self.write(json_encode(response))


class GoodsStockHandler(BaseHandler):

    # 根据id 获取商品库存变化记录
    def get(self):
        goods_id = self.get_argument('id')
        page = self.get_argument('page')
        page_size = self.get_argument('pageSize')

        response = {
            'code': 0,
            'data': '',
            'errorMsg': ''
        }

        total_num, df_records = GoodsModel.get_goods_stock(page, page_size, goods_id)

        data = {
            'count': total_num.tolist(),
            'list': json.loads(df_records)
        }
        response['data'] = data
        self.write(json_encode(response))

    # 根据goods_id新增该商品的库存明细记录，以修改商品的库存
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        response = {
            'code': 0,
            'data': '',
            'errorMsg': ''
        }

        goods_id = data['goodsId']
        change_type = data['changeType']
        num = data['num']
        change_des = data['desc']
        create_by = data['staffNo']
        price = data['price']

        info = {
            'goods_id': goods_id,
            'change_type': change_type,
            'num': num,
            'change_des': change_des,
            'create_by': create_by,
            'price': price
        }

        response_flag = GoodsModel.add_stock_detail(info)

        if response_flag:
            self.write(json_encode(response))
        else:
            response['code'] = -1
            response['errorMsg'] = '修改库存失败，数据库错误，请联系管理员'
            self.write(json_encode(response))


class GoodsStockDeleteHandler(BaseHandler):

    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        response = {
            'code': 0,
            'data': '',
            'errorMsg': ''
        }

        stock_id = data['id']
        create_by = data['staffNo']

        response_flag = GoodsModel.delete_stock_detail(stock_id, create_by)

        if response_flag == 2:
            self.write(json_encode(response))
        elif response_flag == 1:
            response['code'] = -1
            response['errorMsg'] = '商品的入库数不得小于商品的出库数，请检查后再操作'
            self.write(json_encode(response))
        else:
            response['code'] = -1
            response['errorMsg'] = '修改库存失败，数据库错误，请联系管理员'
            self.write(json_encode(response))


class GoodsStockUpdateHandler(BaseHandler):
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        response = {
            'code': 0,
            'data': '',
            'errorMsg': ''
        }

        stock_id = data['stockId']
        change_type = data['changeType']
        num = data['num']
        desc = data['desc']
        create_by = data['staffNo']
        price = data['price']
        goods_id = data['goodsId']

        response_flag = GoodsModel.update_stock_detail(change_type, num, desc, stock_id, create_by, price, goods_id)

        if response_flag == 2:
            self.write(json_encode(response))
        elif response_flag == 1:
            response['code'] = -1
            response['errorMsg'] = '商品的入库数不得小于商品的出库数，请检查后再操作'
            self.write(json_encode(response))
        else:
            response['code'] = -1
            response['errorMsg'] = '修改库存失败，数据库错误，请联系管理员'
            self.write(json_encode(response))
