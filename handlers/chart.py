import json
import tornado
from tornado.escape import json_encode
from handlers.base import BaseHandler
from models.chart import ChartModel


class GoodsStockHandler(BaseHandler):

    def get(self):
        response = {
            'code': 0,
            'data': '',
            'errorMsg': ''
        }

        df_records = ChartModel.goods_stock_report()
        data = {
            'list': json.loads(df_records)
        }
        response['data'] = data
        self.write(json_encode(response))


class GoodsStockInDetailHandler(BaseHandler):

    def get(self):
        page = self.get_argument('page')
        page_size = self.get_argument('pageSize')
        goods_name = self.get_argument('goodsName')
        begin_date = self.get_argument('beginDate')
        end_date = self.get_argument('endDate')

        response = {
            'code': 0,
            'data': '',
            'errorMsg': ''
        }

        total_num, df_records = ChartModel.goods_stock_in_detail_report(goods_name, begin_date, end_date, page, page_size)
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


class GoodsStockOutDetailHandler(BaseHandler):

    def get(self):
        page = self.get_argument('page')
        page_size = self.get_argument('pageSize')
        goods_name = self.get_argument('goodsName')
        begin_date = self.get_argument('beginDate')
        end_date = self.get_argument('endDate')

        response = {
            'code': 0,
            'data': '',
            'errorMsg': ''
        }

        total_num, df_records = ChartModel.goods_stock_out_detail_report(goods_name, begin_date, end_date, page, page_size)
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


class GiftRecordHandler(BaseHandler):

    def get(self):
        try:
            page = self.get_argument('page')
            page_size = self.get_argument('pageSize')
            gift_name = self.get_argument('giftName')
            year = self.get_argument('year')

            response = {
                'code': 0,
                'data': '',
                'errorMsg': ''
            }

            total_num, df_records = ChartModel.gift_record(gift_name, year, page, page_size)
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
        except Exception as e:
            print(e)


class GiftSumReportHandler(BaseHandler):

    def get(self):
        response = {
            'code': 0,
            'data': '',
            'errorMsg': ''
        }

        df_records = ChartModel.gift_sum_report()
        data = {
            'list': json.loads(df_records)
        }
        response['data'] = data
        self.write(json_encode(response))
