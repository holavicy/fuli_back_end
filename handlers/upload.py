import os
import tornado.web
from handlers.base import BaseHandler
from time import time
from tornado.escape import json_encode
from pandas import read_excel
from models.goods import GoodsModel


class UploadImage(BaseHandler):
    basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def post(self):
        staff_no = self.get_argument('staffNo')
        response = {
            'code': 0,
            'data': '',
            'errorMsg': ''
        }
        try:
            files = self.request.files['file'] # list类型中包含一个字典
            if files[0]:
                dict_img = files[0]
                img_name = dict_img.filename
                temp_list = img_name.split('.')
                length = len(temp_list)
                img_type = temp_list[length - 1]
                filename = str(staff_no) + str(time()) + "." + img_type
                with open('files/goodsImages/{}'.format(filename), 'wb') as f:
                    f.write(dict_img['body'])
                url = 'files/goodsImages/' + filename
                response['data'] = url
                self.write(json_encode(response))
            else:
                response['code'] = -1
                response['errorMsg'] = '上传失败，文件为空'
                self.write(json_encode(response))
        except:
            response['code'] = -1
            response['errorMsg'] = '上传失败，系统出错，请联系管理员'
            self.write(json_encode(response))


class UploadGoods(BaseHandler):
    basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def post(self):
        staff_no = self.get_argument('staffNo')
        response = {
            'code': 0,
            'data': '',
            'errorMsg': ''
        }
        try:
            files = self.request.files['file']  # list类型中包含一个字典
            if files[0]:
                file = files[0]
                file_data_frame = read_excel(file.body)
                response_flag = GoodsModel.batch_import_goods(file_data_frame, staff_no)

                if response_flag:
                    self.write(json_encode(response))
                else:
                    response['code'] = -1
                    response['errorMsg'] = '导入失败，数据库错误，请联系管理员'
                    self.write(json_encode(response))

            else:
                response['code'] = -1
                response['errorMsg'] = '导入失败，文件为空'
                self.write(json_encode(response))
        except Exception as e:
            print(e)
            response['code'] = -1
            response['errorMsg'] = '导入失败，系统出错，请联系管理员'
            self.write(json_encode(response))