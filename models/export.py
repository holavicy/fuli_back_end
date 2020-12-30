import json
import xlwt
import re
from time import time, strftime, localtime
from datetime import datetime, timedelta
from common.tool import get_now
from models.goods import GoodsModel
from models.chart import ChartModel
from models.user import UserModel


class ExportModel(object):

    # 导出商品
    @classmethod
    def export_goods(cls, goods_name, goods_status):
        total_num, res = GoodsModel.get_all('', '', goods_name, goods_status)
        result_list = json.loads(res)
        url = cls.write_excel_goods(result_list)
        return url

    # 将数组写入excel，并保存
    @classmethod
    def write_excel_goods(cls, data):
        try:
            book = xlwt.Workbook()  # 新建一个Excel
            sheet = book.add_sheet('导出数据')  # 创建sheet
            title = ['ID', '商品名称', '库存', '单位', '均价']  # 写表头

            # 循环将表头写入到sheet页
            i = 0
            for header in title:
                sheet.write(0, i, header)
                i += 1

            # 写数据
            for index, item in enumerate(data):
                print(index, item)
                sheet.write(index + 1, 0, item['id'])
                sheet.write(index + 1, 1, item['name'])
                sheet.write(index + 1, 2, item['num'])
                sheet.write(index + 1, 3, item['unit'])
                sheet.write(index + 1, 4, item['price'])
            timestamp = str(time())
            filename = 'files/export/' + timestamp + ".xls"
            book.save(filename)
            return 'export/' + timestamp + ".xls"
        except Exception as e:
            print(e)

    # 导出商品库存报表
    @classmethod
    def export_chart_goods(cls):
        res = ChartModel.goods_stock_report()
        result_list = json.loads(res)
        url = cls.write_excel_chart_goods(result_list)
        return url

    # 将数组写入excel，并保存
    @classmethod
    def write_excel_chart_goods(cls, data):
        try:
            book = xlwt.Workbook()  # 新建一个Excel
            sheet = book.add_sheet('导出数据')  # 创建sheet
            title = ['商品ID', '商品名称', '总入库数量', '总出库数量', '库存数量', '均价', '总入库数量*均价']  # 写表头

            # 循环将表头写入到sheet页
            i = 0
            for header in title:
                sheet.write(0, i, header)
                i += 1

            # 写数据
            for index, item in enumerate(data):
                print(index, item)
                sheet.write(index + 1, 0, item['id'])
                sheet.write(index + 1, 1, item['name'])
                sheet.write(index + 1, 2, item['allIn'])
                sheet.write(index + 1, 3, item['allOut'])
                sheet.write(index + 1, 4, item['stock'])
                sheet.write(index + 1, 5, item['price'])
                sheet.write(index + 1, 6, item['totalInAmount'])
            timestamp = str(time())
            filename = 'files/export/goods_stock_' + timestamp + ".xls"
            book.save(filename)
            return 'export/goods_stock_' + timestamp + ".xls"
        except Exception as e:
            print(e)

    # 商品入库明细报表
    @classmethod
    def goods_stock_in_detail_report(cls, goods_name, begin_date, end_date):
        total_num, res = ChartModel.goods_stock_in_detail_report(goods_name, begin_date, end_date, '', '')
        result_list = json.loads(res)
        url = cls.write_excel_chart_goods_stock_in(result_list)
        return url

    @classmethod
    def write_excel_chart_goods_stock_in(cls, data):
        try:
            book = xlwt.Workbook()  # 新建一个Excel
            sheet = book.add_sheet('导出数据')  # 创建sheet
            title = ['商品ID', '商品名称', '入库日期', '入库数量', '当前入库单价', '当前入库总价', '入库说明']  # 写表头

            # 循环将表头写入到sheet页
            i = 0
            for header in title:
                sheet.write(0, i, header)
                i += 1

            # 写数据
            for index, item in enumerate(data):
                print(index, item)
                time_stamp = item['create_time'] # 毫秒级时间戳
                # 转换成localtime
                time_local = localtime(time_stamp / 1000)
                dt = strftime("%Y-%m-%d %H:%M:%S", time_local)
                print(dt)
                print(type(dt))
                # 转换成新的时间格式(精确到秒)
                create_time = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S') - timedelta(hours=8, minutes=0, seconds=0)
                create_time = create_time.strftime('%Y-%m-%d %H:%M:%S')  # 只取年月日，时分秒
                print(create_time)
                print(type(create_time))
                # create_time = datetime.strptime(str(time_local), '%Y-%m-%d %H:%M:%S')-timedelta(hours=8)
                sheet.write(index + 1, 0, item['id'])
                sheet.write(index + 1, 1, item['name'])
                sheet.write(index + 1, 2, create_time)
                sheet.write(index + 1, 3, item['num'])
                sheet.write(index + 1, 4, item['price'])
                sheet.write(index + 1, 5, item['amount'])
                sheet.write(index + 1, 6, item['change_des'])
            timestamp = str(time())
            filename = 'files/export/goods_stock_in_' + timestamp + ".xls"
            book.save(filename)
            return 'export/goods_stock_in_' + timestamp + ".xls"
        except Exception as e:
            print(e)

    # 商品出库明细报表
    @classmethod
    def goods_stock_out_detail_report(cls, goods_name, begin_date, end_date):
        total_num, res = ChartModel.goods_stock_out_detail_report(goods_name, begin_date, end_date, '', '')
        result_list = json.loads(res)
        url = cls.write_excel_chart_goods_stock_out(result_list)
        return url

    @classmethod
    def write_excel_chart_goods_stock_out(cls, data):
        try:
            book = xlwt.Workbook()  # 新建一个Excel
            sheet = book.add_sheet('导出数据')  # 创建sheet
            title = ['商品ID', '商品名称', '出库日期', '出库数量', '当前出库单价', '当前出库总价', '出库说明']  # 写表头

            # 循环将表头写入到sheet页
            i = 0
            for header in title:
                sheet.write(0, i, header)
                i += 1

            # 写数据
            for index, item in enumerate(data):
                print(index, item)
                time_stamp = item['create_time'] # 毫秒级时间戳
                # 转换成localtime
                time_local = localtime(time_stamp / 1000)
                dt = strftime("%Y-%m-%d %H:%M:%S", time_local)
                print(dt)
                print(type(dt))
                # 转换成新的时间格式(精确到秒)
                create_time = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S') - timedelta(hours=8, minutes=0, seconds=0)
                create_time = create_time.strftime('%Y-%m-%d %H:%M:%S')  # 只取年月日，时分秒
                print(create_time)
                print(type(create_time))
                # create_time = datetime.strptime(str(time_local), '%Y-%m-%d %H:%M:%S')-timedelta(hours=8)
                sheet.write(index + 1, 0, item['id'])
                sheet.write(index + 1, 1, item['name'])
                sheet.write(index + 1, 2, create_time)
                sheet.write(index + 1, 3, item['num'])
                sheet.write(index + 1, 4, item['price'])
                sheet.write(index + 1, 5, item['amount'])
                sheet.write(index + 1, 6, item['change_des'])
            timestamp = str(time())
            filename = 'files/export/goods_stock_out_' + timestamp + ".xls"
            book.save(filename)
            return 'export/goods_stock_out_' + timestamp + ".xls"
        except Exception as e:
            print(e)

    # 礼包领取明细报表
    @classmethod
    def export_gift(cls, gift_name, year):
        total_num, res = ChartModel.gift_record(gift_name, year, '', '')
        result_list = json.loads(res)
        data_list = []
        for index, item in enumerate(result_list):
            if len(item['goods_list']) > 0:
                for goodsIndex, goods in enumerate(item['goods_list']):
                    goods_item = goods
                    goods_item['order_id'] = item['order_id']
                    goods_item['birth_date'] = item['birth_date']
                    goods_item['finish_time'] = item['finish_time']
                    goods_item['index'] = index + 1
                    goods_item['gift_name'] = item['gift_name']
                    goods_item['org_name'] = item['org_name']
                    goods_item['staff_name'] = item['staff_name']
                    goods_item['staff_no'] = item['staff_no']
                    goods_item['dept_list'] = item['dept_list']
                    goods_item['rowspan'] = False
                    goods_item['rowNum'] = 0

                    if goodsIndex == 0:

                        goods_item['rowspan'] = True
                        goods_item['rowNum'] = len(item['goods_list'])

                    print(goods_item)
                    data_list.append(goods_item)

        url = cls.write_excel_export_gift(data_list)
        return url

    @classmethod
    def write_excel_export_gift(cls, data):
        try:
            book = xlwt.Workbook()  # 新建一个Excel
            sheet = book.add_sheet('导出数据')  # 创建sheet
            title = ['序号', '礼包方案名称', '商品名称', '商品数量', '商品当前出库单价', '商品当前出库总价', '领取人', '领取人工号', '领取人公司', '领取人一级部门', '领取人二级部门', '领取人三级部门', '领取人生日', '领取日期']  # 写表头

            # 循环将表头写入到sheet页
            i = 0
            for header in title:
                sheet.write(0, i, header)
                i += 1

            # 写数据
            for index, item in enumerate(data):
                time_stamp = item['finish_time'] # 毫秒级时间戳
                # 转换成localtime
                time_local = localtime(time_stamp / 1000)
                dt = strftime("%Y-%m-%d %H:%M:%S", time_local)
                # 转换成新的时间格式(精确到秒)
                finish_time = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S') - timedelta(hours=8, minutes=0, seconds=0)
                finish_time = finish_time.strftime('%Y-%m-%d')  # 只取年月日，时分秒

                sheet.write(index + 1, 2, item['goods_name'])
                sheet.write(index + 1, 3, item['goods_num'])
                sheet.write(index + 1, 4, item['goods_price'])
                sheet.write(index + 1, 5, item['total_amount'])

                alignment = xlwt.Alignment()  # 创建对其格式的对象 Create Alignment
                alignment.horz = xlwt.Alignment.HORZ_CENTER  # 我猜是左右的对其，水平居中 May be: HORZ_GENERAL, HORZ_LEFT, HORZ_CENTER, HORZ_RIGHT, HORZ_FILLED, HORZ_JUSTIFIED, HORZ_CENTER_ACROSS_SEL, HORZ_DISTRIBUTED
                alignment.vert = xlwt.Alignment.VERT_CENTER  # 我猜是上下的对其 May be: VERT_TOP, VERT_CENTER, VERT_BOTTOM, VERT_JUSTIFIED, VERT_DISTRIBUTED
                style = xlwt.XFStyle()  # 创建样式对象 Create Style
                style.alignment = alignment  # 将格式Alignment对象加入到样式对象Add Alignment to Style
                if item['rowspan']:
                    sheet.write_merge(index + 1, index + item['rowNum'], 0, 0, item['index'], style)
                    sheet.write_merge(index + 1, index + item['rowNum'], 1, 1, item['gift_name'], style)
                    sheet.write_merge(index + 1, index + item['rowNum'], 6, 6, item['staff_name'], style)
                    sheet.write_merge(index + 1, index + item['rowNum'], 7, 7, item['staff_no'], style)
                    sheet.write_merge(index + 1, index + item['rowNum'], 8, 8, item['org_name'], style)
                    sheet.write_merge(index + 1, index + item['rowNum'], 9, 9, item['dept_list'][0], style)
                    sheet.write_merge(index + 1, index + item['rowNum'], 10, 10, item['dept_list'][1], style)
                    sheet.write_merge(index + 1, index + item['rowNum'], 11, 11, item['dept_list'][2], style)
                    sheet.write_merge(index + 1, index + item['rowNum'], 12, 12, item['birth_date'], style)
                    sheet.write_merge(index + 1, index + item['rowNum'], 13, 13, finish_time, style)
            timestamp = str(time())
            filename = 'files/export/gift_record_' + timestamp + ".xls"
            book.save(filename)
            return 'export/gift_record_' + timestamp + ".xls"
        except Exception as e:
            print(e)

    # 礼包领取汇总报表
    @classmethod
    def export_gift_sum(cls):
        df_records = ChartModel.gift_sum_report()
        result_list = json.loads(df_records)
        data_list = []
        for index, item in enumerate(result_list):
            if len(item['goods_list']) > 0:
                print(type(item['goods_list']))
                for goodsIndex, goods in enumerate(item['goods_list']):
                    goods_item = goods
                    goods_item['gift_id'] = item['gift_id']
                    goods_item['gift_name'] = item['gift_name']
                    goods_item['gift_num'] = item['gift_num']
                    goods_item['index'] = index + 1
                    goods_item['all_amount'] = item['all_amount']
                    goods_item['rowspan'] = False
                    goods_item['rowNum'] = 0
                    print(goods_item)
                    if goodsIndex == 0:
                        goods_item['rowspan'] = True
                        goods_item['rowNum'] = len(item['goods_list'])

                    data_list.append(goods_item)

        url = cls.write_excel_export_gift_sum(data_list)
        return url

    @classmethod
    def write_excel_export_gift_sum(cls, data):
        try:
            book = xlwt.Workbook()  # 新建一个Excel
            sheet = book.add_sheet('导出数据')  # 创建sheet
            title = ['序号', '礼包方案内容', '总共领取', '商品名称', '数量', '出库均价', '出库总价', '礼包商品出库总价合计']  # 写表头

            # 循环将表头写入到sheet页
            i = 0
            for header in title:
                sheet.write(0, i, header)
                i += 1

            # 写数据
            for index, item in enumerate(data):

                sheet.write(index + 1, 3, item['goods_name'])
                sheet.write(index + 1, 4, item['goods_num'])
                sheet.write(index + 1, 5, item['goods_avg_price'])
                sheet.write(index + 1, 6, item['goods_total_amount'])

                alignment = xlwt.Alignment()  # 创建对其格式的对象 Create Alignment
                alignment.horz = xlwt.Alignment.HORZ_CENTER  # 我猜是左右的对其，水平居中 May be: HORZ_GENERAL, HORZ_LEFT, HORZ_CENTER, HORZ_RIGHT, HORZ_FILLED, HORZ_JUSTIFIED, HORZ_CENTER_ACROSS_SEL, HORZ_DISTRIBUTED
                alignment.vert = xlwt.Alignment.VERT_CENTER  # 我猜是上下的对其 May be: VERT_TOP, VERT_CENTER, VERT_BOTTOM, VERT_JUSTIFIED, VERT_DISTRIBUTED
                style = xlwt.XFStyle()  # 创建样式对象 Create Style
                style.alignment = alignment  # 将格式Alignment对象加入到样式对象Add Alignment to Style
                if item['rowspan']:
                    sheet.write_merge(index + 1, index + item['rowNum'], 0, 0, item['index'], style)
                    sheet.write_merge(index + 1, index + item['rowNum'], 1, 1, item['gift_name'], style)
                    sheet.write_merge(index + 1, index + item['rowNum'], 2, 2, item['gift_num'], style)
                    sheet.write_merge(index + 1, index + item['rowNum'], 7, 7, item['all_amount'], style)
            timestamp = str(time())
            filename = 'files/export/gift_record_sum_' + timestamp + ".xls"
            book.save(filename)
            return 'export/gift_record_sum_' + timestamp + ".xls"
        except Exception as e:
            print(e)

    # 一般生日礼包人员统计报表
    @classmethod
    def export_staff(cls, staff_no, name, get_status, get_year):
        print('start')
        total_num, df_records = UserModel.get_user_list('', '', staff_no, name, get_status, get_year)
        result_list = json.loads(df_records)

        template = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
        year = re.sub(template, r"\1", get_year)
        url = cls.write_excel_chart_staff(result_list, year)
        return url

    @classmethod
    def write_excel_chart_staff(cls, data, year):
        try:
            book = xlwt.Workbook()  # 新建一个Excel
            sheet = book.add_sheet('导出数据')  # 创建sheet
            title = ['序号', '工号', '公司', '一级部门', '二级部门', '三级部门', '姓名', '出生日期', '联系方式', '领取状态']  # 写表头

            # 循环将表头写入到sheet页
            i = 0
            for header in title:
                sheet.write(0, i, header)
                i += 1

            # 写数据
            for index, item in enumerate(data):
                print(index, item)
                print(item['dept_list'])
                print(type(item['dept_list']))
                sheet.write(index + 1, 0, index + 1)
                sheet.write(index + 1, 1, item['CODE'])
                sheet.write(index + 1, 2, item['group'])
                sheet.write(index + 1, 3, item['dept_list'][0])
                if len(item['dept_list']) > 1:
                    sheet.write(index + 1, 4, item['dept_list'][1])
                else:
                    sheet.write(index + 1, 4, '')
                if len(item['dept_list']) > 2:
                    sheet.write(index + 1, 5, item['dept_list'][2])
                else:
                    sheet.write(index + 1, 5, '')
                sheet.write(index + 1, 6, item['NAME'])
                sheet.write(index + 1, 7, item['BIRTHDATE'])
                sheet.write(index + 1, 8, item['mobile'])
                if item['GOTNUM'] > 0:
                    if item['ORDERSTATUS'] == 1:
                        sheet.write(index + 1, 9, '待管理员确认')
                    elif item['ORDERSTATUS'] == 3:
                        sheet.write(index + 1, 9, '待领取')
                    elif item['ORDERSTATUS'] == 4:
                        sheet.write(index + 1, 9, '已领取')
                else:
                    sheet.write(index + 1, 9, '未申请')

            timestamp = str(time())
            filename = 'files/export/staff_' + str(year) + '_' + timestamp + ".xls"
            book.save(filename)
            return 'export/staff_' + str(year) + '_' + timestamp + ".xls"
        except Exception as e:
            print(e)

    # 整生日礼包人员统计报表
    @classmethod
    def export_z_staff(cls, staff_no, name, get_year):
        print(get_year)
        total_num, df_records = UserModel.get_z_birth_user_list('', '', staff_no, name, get_year)
        result_list = json.loads(df_records)

        template = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
        year = re.sub(template, r"\1", get_year)

        url = cls.write_excel_chart_z_staff(result_list, year)
        return url

    @classmethod
    def write_excel_chart_z_staff(cls, data, year):
        try:
            book = xlwt.Workbook()  # 新建一个Excel
            sheet = book.add_sheet('导出数据')  # 创建sheet
            title = ['序号', '工号', '公司', '一级部门', '二级部门', '三级部门', '姓名', '出生日期', '联系方式']  # 写表头

            # 循环将表头写入到sheet页
            i = 0
            for header in title:
                sheet.write(0, i, header)
                i += 1

            # 写数据
            for index, item in enumerate(data):
                sheet.write(index + 1, 0, index + 1)
                sheet.write(index + 1, 1, item['CODE'])
                sheet.write(index + 1, 2, item['group'])
                sheet.write(index + 1, 3, item['dept_list'][0])
                if len(item['dept_list']) > 1:
                    sheet.write(index + 1, 4, item['dept_list'][1])
                else:
                    sheet.write(index + 1, 4, '')
                if len(item['dept_list']) > 2:
                    sheet.write(index + 1, 5, item['dept_list'][2])
                else:
                    sheet.write(index + 1, 5, '')
                sheet.write(index + 1, 6, item['NAME'])
                sheet.write(index + 1, 7, item['BIRTHDATE'])
                sheet.write(index + 1, 8, item['mobile'])

            timestamp = str(time())
            filename = 'files/export/staff_z_' + str(year) + '_' + timestamp + ".xls"
            book.save(filename)
            return 'export/staff_z_' + str(year) + '_' + timestamp + ".xls"
        except Exception as e:
            print(e)
