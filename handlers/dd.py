import tornado.web
from tornado.escape import json_encode
import requests
from models.dd import DDModel
from handlers.base import BaseHandler


class UserHandler(BaseHandler):
    url = "https://oapi.dingtalk.com"
    appkey = 'dingfizsybn5gydpuost'
    appsecret = 'xzoq0h_N3wfBoty8BdGEYrs3T9NnC5Rjm6HKNrXkV2h4XI4a5gGR8m2HT13wKxNg'

    def get(self):
        code = self.get_argument('code')
        access_token = DDModel.get_access_token()
        user_info = DDModel.get_user_info(code, access_token)
        user_id = user_info['userid']
        user_detail = DDModel.get_user_detail(access_token, user_id)
        self.write(json_encode(user_detail))


class MSGHandler(BaseHandler):

    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        user_id = data['userId']
        res = DDModel.send_message(user_id)
        self.write(json_encode(res))


class SupplyMSGHandler(BaseHandler):

    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        user_id = data['userId']
        msg = data['msg']
        res = DDModel.send_supply_message(user_id, msg)
        self.write(json_encode(res))


class AuthHandler(BaseHandler):
    def get(self):
        url = self.get_argument('url')
        config = DDModel.get_config(url)
        self.write(json_encode(config))


class UserInfoHandler(BaseHandler):

    def get(self):
        user_id = self.get_argument('userId')
        access_token = DDModel.get_access_token()
        user_detail = DDModel.get_user_detail(access_token, user_id)
        self.write(json_encode(user_detail))
