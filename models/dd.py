import requests
import urllib.parse


class DDModel(object):

    url = "https://oapi.dingtalk.com"
    appKey = 'dingfizsybn5gydpuost'
    appSecret = 'xzoq0h_N3wfBoty8BdGEYrs3T9NnC5Rjm6HKNrXkV2h4XI4a5gGR8m2HT13wKxNg'
    agent_id = '927117753'
    CorpId = 'dingcd0f5a2514db343b35c2f4657eb6378f'


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
    发送钉钉工作通知
    param: access_token, agent_id, msg, userid_list
    '''
    @classmethod
    def send_message(cls, user_id):
        access_token = cls.get_access_token()

        url = cls.url + '/topapi/message/corpconversation/asyncsend_v2?access_token=' + access_token
        HEADERS = {'Content-Type': 'application/json'}
        target_url = urllib.parse.quote('http://127.0.0.1:8080/#/orderList')
        print(target_url)
        data = {
            "agent_id": cls.agent_id,
            "userid_list": user_id,
            # "msg": {
            #      "msgtype": "action_card",
            #      "action_card": {
            #         "title": "您有一个生日礼包可以领取啦【测试，请忽略】",
            #         "markdown": "管理员已通过您提交的领取生日礼包申请，现在可以前往领取生日礼包，详细可联系福利管理员",
            #         "single_title": "查看详情",
            #         "single_url": "dingtalk://dingtalkclient/action/openapp?corpid="+cls.CorpId+"&container_type=work_platform&app_id=0_"+cls.agent_id+"&redirect_type=jump&redirect_url="+target_url
            #      }
            # }
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
                            "content": "管理员已通过您提交的领取生日礼包申请，现在可以前往领取生日礼包，具体领取方式可联系福利管理员",
                        }
                    }
                }
        }
        res = requests.post(url=url, headers=HEADERS, json=data)
        print(res.text)
        return res.text
