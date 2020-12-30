import json
import tornado
from tornado.escape import json_encode
from handlers.base import BaseHandler
from models.export import ExportModel


class ExportGoodsHandler(BaseHandler):

    def get(self):
        response = {
            'code': 0,
            'data': '',
            'errorMsg': ''
        }

        goods_name = self.get_argument('goodsName')
        goods_status = self.get_argument('goodsStatus')

        url = ExportModel.export_goods(goods_name, goods_status)
        data = {
            'url': url
        }
        response['data'] = data
        self.write(json_encode(response))


class ExportChartGoodsHandler(BaseHandler):

    def get(self):
        response = {
            'code': 0,
            'data': '',
            'errorMsg': ''
        }

        url = ExportModel.export_chart_goods()
        data = {
            'url': url
        }
        response['data'] = data
        self.write(json_encode(response))


class ExportGoodsStockInHandler(BaseHandler):

    def get(self):
        goods_name = self.get_argument('goodsName')
        begin_date = self.get_argument('beginDate')
        end_date = self.get_argument('endDate')

        response = {
            'code': 0,
            'data': '',
            'errorMsg': ''
        }

        url = ExportModel.goods_stock_in_detail_report(goods_name, begin_date, end_date)
        data = {
            'url': url
        }
        response['data'] = data
        self.write(json_encode(response))


class ExportGoodsStockOutHandler(BaseHandler):

    def get(self):
        goods_name = self.get_argument('goodsName')
        begin_date = self.get_argument('beginDate')
        end_date = self.get_argument('endDate')

        response = {
            'code': 0,
            'data': '',
            'errorMsg': ''
        }

        url = ExportModel.goods_stock_out_detail_report(goods_name, begin_date, end_date)
        data = {
            'url': url
        }
        response['data'] = data
        self.write(json_encode(response))


class ExportGiftHandler(BaseHandler):

    def get(self):
        gift_name = self.get_argument('giftName')
        year = self.get_argument('year')

        response = {
            'code': 0,
            'data': '',
            'errorMsg': ''
        }

        url = ExportModel.export_gift(gift_name, year)
        data = {
            'url': url
        }
        response['data'] = data
        self.write(json_encode(response))


class ExportGiftSumHandler(BaseHandler):

    def get(self):

        response = {
            'code': 0,
            'data': '',
            'errorMsg': ''
        }

        url = ExportModel.export_gift_sum()
        data = {
            'url': url
        }
        response['data'] = data
        self.write(json_encode(response))


class ExportStaffHandler(BaseHandler):

    def get(self):

        response = {
            'code': 0,
            'data': '',
            'errorMsg': ''
        }

        staff_no = self.get_argument('staffNo')
        name = self.get_argument('name')
        get_status = self.get_argument('getStatus')
        get_year = self.get_argument('getYear')

        url = ExportModel.export_staff(staff_no, name, get_status, get_year)
        data = {
            'url': url
        }
        response['data'] = data
        self.write(json_encode(response))


class ExportZStaffHandler(BaseHandler):

    def get(self):

        response = {
            'code': 0,
            'data': '',
            'errorMsg': ''
        }

        staff_no = self.get_argument('staffNo')
        name = self.get_argument('name')
        get_year = self.get_argument('getYear')

        url = ExportModel.export_z_staff(staff_no, name, get_year)
        data = {
            'url': url
        }
        response['data'] = data
        self.write(json_encode(response))