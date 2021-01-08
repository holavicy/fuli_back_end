import pymssql
import requests
import urllib.parse
import hashlib
import time
import pandas as pd
from common.tool import TaskErr, get_now


class DDModel(object):

    url = "https://oapi.dingtalk.com"
    appKey = 'dingfizsybn5gydpuost'
    appSecret = 'xzoq0h_N3wfBoty8BdGEYrs3T9NnC5Rjm6HKNrXkV2h4XI4a5gGR8m2HT13wKxNg'
    agent_id = '927117753'
    CorpId = 'dingcd0f5a2514db343b35c2f4657eb6378f'

    conn_ss = pymssql.connect(host='192.168.40.229:1433', port=3306, user='serverapp', password='wetown2020',
                              database='DingDB')


    '''
    获取access_token
    params: appKey, appSecret
    '''
    @classmethod
    def get_access_token(cls):
        response = requests.get(
            url=cls.url + "/gettoken",
            params=dict(appkey=cls.appKey, appsecret=cls.appSecret)
        )
        access_token = response.json()["access_token"]
        return access_token

    '''
    获取用户基本信息
    params: code, access_token
    '''
    @classmethod
    def get_user_info(cls, code, access_token):
        response = requests.get(
            url=cls.url + "/user/getuserinfo",
            params=dict(access_token=access_token, code=code)
        )
        response = response.json()
        if response.get('errcode') != 0:
            raise TaskErr(1, response)
        return response

    '''
    获取用户详细信息
    :param: access_token, userid
    '''
    @classmethod
    def get_user_detail(cls, access_token, user_id):
        response = requests.get(
            url=cls.url + "/user/get",
            params=dict(access_token=access_token, userid=user_id)
        )

        response = response.json()
        return response

    '''
    管理员审核通过后钉钉消息通知员工
    param: access_token, agent_id, msg, userid_list
    '''
    @classmethod
    def send_message(cls, staff_no):

        access_token = cls.get_access_token()
        user_id = cls.get_user_id_by_staff_no(staff_no)
        print(user_id)

        now = get_now()

        url = cls.url + '/topapi/message/corpconversation/asyncsend_v2?access_token=' + access_token
        HEADERS = {'Content-Type': 'application/json'}
        target_url = urllib.parse.quote('http://192.168.40.229:8081/gift/#/orderList')
        print(target_url)
        data = {
            "agent_id": cls.agent_id,
            "userid_list": user_id,
            "msg": {
                    "msgtype": "oa",
                    "oa": {
                        "message_url": "eapp://pages/index/index",
                        "pc_message_url": "dingtalk://dingtalkclient/action/openapp?corpid="+cls.CorpId+"&container_type=work_platform&app_id=0_"+cls.agent_id+"&redirect_type=jump&redirect_url="+target_url,
                        "head": {
                            "bgcolor": "FFBBBBBB",
                            "text": "福利管理系统"
                        },
                        "body": {
                            "title": "您有一个生日礼包可以前往领取啦",
                            "content": now + ",管理员已通过您提交的领取生日礼包申请，请于周五下午3-5点前往集团大楼4楼409联系福利专员领取",
                        }
                    }
                }
        }
        res = requests.post(url=url, headers=HEADERS, json=data)
        print(res.text)
        return res.text

    '''
    设置代领后钉钉消息通知代领人
    '''
    @classmethod
    def send_supply_message(cls, staff_no, msg):
        access_token = cls.get_access_token()
        user_id = cls.get_user_id_by_staff_no(staff_no)
        print('user_id')
        print(user_id)

        now = get_now()

        url = cls.url + '/topapi/message/corpconversation/asyncsend_v2?access_token=' + access_token
        HEADERS = {'Content-Type': 'application/json'}
        target_url = urllib.parse.quote('http://192.168.40.229:8081/gift')
        data = {
            "agent_id": cls.agent_id,
            "userid_list": user_id,
            "msg": {
                "msgtype": "oa",
                "oa": {
                    "message_url": "eapp://pages/index/index",
                    "pc_message_url": "dingtalk://dingtalkclient/action/openapp?corpid=" + cls.CorpId + "&container_type=work_platform&app_id=0_" + cls.agent_id + "&redirect_type=jump&redirect_url=" + target_url,
                    "head": {
                        "bgcolor": "FFBBBBBB",
                        "text": "福利管理系统"
                    },
                    "body": {
                        "title": "您有一个代领消息",
                        "content": now + "," + msg,
                    }
                }
            }
        }
        res = requests.post(url=url, headers=HEADERS, json=data)
        print(res.text)
        return res.text

    '''
   每日提醒一周后过生日的人
   '''

    @classmethod
    def send_birth_message(cls, staff_no, msg):
        access_token = cls.get_access_token()
        user_id = cls.get_user_id_by_staff_no(staff_no)

        now = get_now()

        url = cls.url + '/topapi/message/corpconversation/asyncsend_v2?access_token=' + access_token
        HEADERS = {'Content-Type': 'application/json'}
        target_url = urllib.parse.quote('http://192.168.40.229:8081/gift')
        data = {
            "agent_id": cls.agent_id,
            "userid_list": user_id,
            "msg": {
                "msgtype": "oa",
                "oa": {
                    "message_url": "eapp://pages/index/index",
                    "pc_message_url": "dingtalk://dingtalkclient/action/openapp?corpid=" + cls.CorpId + "&container_type=work_platform&app_id=0_" + cls.agent_id + "&redirect_type=jump&redirect_url=" + target_url,
                    "head": {
                        "bgcolor": "FFBBBBBB",
                        "text": "福利管理系统"
                    },
                    "body": {
                        "title": "您有一个生日礼包可申请领取！",
                        "content": now + "," + msg,
                    }
                }
            }
        }
        res = requests.post(url=url, headers=HEADERS, json=data)
        print(res.text)
        return res.text

    '''
    获取钉钉jsp权鉴数据
    param: request'''
    @classmethod
    def get_config(cls, url):
        timestamp = str(int(round(time.time()))) + '000'
        nonce_str = 'abcdefg'
        signed_url = url
        access_token = cls.get_access_token()
        print('access_token')
        print(access_token)
        ticket = cls.get_js_api_ticket(access_token)
        print('ticket')
        print(ticket)
        signature = cls.sign(ticket, nonce_str, timestamp, signed_url)
        print('signature')
        print(signature)
        data = {
            "jsticket": ticket,
            "signature": signature,
            "nonceStr": nonce_str,
            "timeStamp": timestamp,
            "corpId": cls.CorpId,
            "agentId": cls.agent_id
        }
        return data

    '''
    获取jsapi_ticket
    param: access_token
    '''
    @classmethod
    def get_js_api_ticket(cls, access_token):
        response = requests.get(
            url=cls.url + "/get_jsapi_ticket",
            params=dict(access_token=access_token)
        )
        ticket = response.json()["ticket"]
        return ticket

    '''
    获取sign
    param: ticket, nonce_str, time_stamp, signed_url
    '''
    @classmethod
    def sign(cls, ticket, nonce_str, time_stamp, signed_url):
        plain_tex = "jsapi_ticket=" + ticket + "&noncestr=" + nonce_str + "&timestamp=" + time_stamp + "&url=" + signed_url
        print(plain_tex)
        signature = hashlib.sha1(plain_tex.encode('utf8'))
        return signature.hexdigest()

    @classmethod
    def get_user_id_by_staff_no(cls, staff_no):
        try:
            sql = "SELECT dm.UserID FROM DingMan dm WHERE dm.JobID = '%s'" % (staff_no)
            print(sql)
            df = pd.read_sql(sql, con=cls.conn_ss)
            user_id = df['UserID'][0]

            return user_id
        except Exception as e:
            print(e)
