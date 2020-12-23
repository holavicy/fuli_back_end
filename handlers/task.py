import json
import tornado
from tornado.escape import json_encode
from models.task import TaskModel
from models.dd import DDModel


class TaskHandler(object):

    # 获取一周后过生日的人的useridlist,遍历并发送消息，提醒领取
    @classmethod
    def get_next_week_birth_user_id_list(cls):

        df_records = TaskModel.get_next_week_birth_user_list()
        user_list = json.loads(df_records)
        print('开始')
        for user in user_list:

            got_num = user['GOTNUM']
            # 若未申请，则发送消息提醒相关人员和代领人
            if got_num == 0:
                user_id = user['CODE']
                msg = '您今年的生日礼包已可以申请领取，快来挑选生日礼包吧！'
                # DDModel.send_birth_message(user_id, msg)

                # 如果设置了代领也要提醒代领
                is_others = user['isOthers']

                if is_others == '是':
                    name = user['NAME']
                    others_user_id = user['othersStaffNo']
                    others_msg = '您可帮' + name + '代领生日礼包，快去帮他挑选生日礼包吧！'
                    # DDModel.send_birth_message(others_user_id, others_msg)

    # 获取当前时间未申请以及申请了未领取的人员列表，并遍历发送消息
    @classmethod
    def get_un_finish_user_list(cls):

        df_records = TaskModel.get_un_finish_user_list()
        user_list = json.loads(df_records)
        print('周五开始')
        for index, user in enumerate(user_list):
            print(index)

            got_num = user['GOTNUM']
            user_id = user['CODE']
            print(user_id)
            msg = ''

            if got_num == 0:
                msg = '您今年的生日礼包已可以申请，请尽快登录系统申请您的生日礼包！'
            else:
                msg = '您今年的生日礼包已可以领取，请于周五下午3-5点前往集团大楼4楼409联系福利专员领取！'
            # DDModel.send_birth_message(user_id, msg)
            is_others = user['isOthers']
            if is_others == '是':
                name = user['NAME']

                others_user_id = user['othersStaffNo']
                others_msg = '您可帮' + name + '代领生日礼包，请尽快登录系统进行领取！'
                print(others_msg)
                # DDModel.send_birth_message(others_user_id, others_msg)


    @classmethod
    def my_job(cls):
        print('测试任务')


