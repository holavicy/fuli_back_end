import tornado.web
import tornado.httpserver
import tornado.ioloop
import logging
import time
from apscheduler.schedulers.tornado import TornadoScheduler
from handlers import goods as goods_handlers
from handlers import giftBag as giftBag_handlers
from handlers import dd as dd_handlers
from handlers import upload as upload_handlers
from handlers import order as order_handlers
from handlers import user as user_handlers
from handlers import like as like_handlers
from handlers import supply as supply_handlers
from handlers import suggest as suggest_handlers
from handlers import suggest as suggest_handlers
from handlers import chart as chart_handlers
from handlers.task import TaskHandler
from handlers import export as export_handlers

HANDLERS = [
    # 商品相关
    (r"/api/goods", goods_handlers.GoodsListHandler),
    (r"/api/uploadImage", upload_handlers.UploadImage),
    (r"/api/importGoods", upload_handlers.UploadGoods),
    (r"/api/setGoodsStatus", goods_handlers.GoodsStatusHandler),
    (r"/api/updateGoodsInfo", goods_handlers.GoodsHandler),
    (r"/api/getStockRecords", goods_handlers.GoodsStockHandler),
    (r"/api/addStockChangeDetail", goods_handlers.GoodsStockHandler),
    (r"/api/deleteStock", goods_handlers.GoodsStockDeleteHandler),
    (r"/api/updateStockChangeDetail", goods_handlers.GoodsStockUpdateHandler),
    # 礼包相关
    (r"/api/giftBag", giftBag_handlers.GiftBagListHandler),
    (r"/api/setGiftBagStatus", giftBag_handlers.GiftBagStatusHandler),
    (r"/api/editGiftBag", giftBag_handlers.GiftBagHandler),
    # 订单相关
    (r"/api/createOrder", order_handlers.OrderListHandler),
    (r"/api/getOrderList", order_handlers.OrderListHandler),
    (r"/api/editOrderStatus", order_handlers.OrderStatusHandler),
    (r"/api/getOthersOrder", order_handlers.OrderOthersHandler),
    # 钉钉相关
    (r"/api/getUserInfo", dd_handlers.UserHandler),
    (r"/api/sendMsg", dd_handlers.MSGHandler),
    (r"/api/sendSupplyMsg", dd_handlers.SupplyMSGHandler),
    (r"/api/getConfig", dd_handlers.AuthHandler),
    (r"/api/getUserInfoByUserId", dd_handlers.UserInfoHandler),
    # 喜欢某商品相关
    (r"/api/like", like_handlers.LikeListHandler),
    (r"/api/isLike", like_handlers.LikeListHandler),
    (r"/api/cancelLike", like_handlers.CancelLikeHandler),
    # 用户相关
    (r"/api/getUserInfoNC", user_handlers.UserInfoHandler),
    (r"/api/getUserList", user_handlers.UserListHandler),
    (r"/api/zBirthStaff", user_handlers.ZBirthUserListHandler),
    # 代领相关
    (r"/api/supply", supply_handlers.SupplyListHandler),
    (r"/api/cancelSupply", supply_handlers.SupplyStatusHandler),
    # 建议相关
    (r"/api/suggestDict", suggest_handlers.SuggestDictListHandler),
    (r"/api/suggest", suggest_handlers.SuggestListHandler),
    (r"/api/suggestRecords", suggest_handlers.SuggestListHandler),
    # 报表相关
    (r"/api/goodsStockReport", chart_handlers.GoodsStockHandler),
    (r"/api/goodsStockInDetailReport", chart_handlers.GoodsStockInDetailHandler),
    (r"/api/goodsStockOutDetailReport", chart_handlers.GoodsStockOutDetailHandler),
    (r"/api/giftRecordReport", chart_handlers.GiftRecordHandler),
    (r"/api/giftSumReport", chart_handlers.GiftSumReportHandler),
    # 导出相关
    (r"/api/exportGoods", export_handlers.ExportGoodsHandler),
    (r"/api/exportChartGoods", export_handlers.ExportChartGoodsHandler),
    (r"/api/exportGoodsStockInDetailReport", export_handlers.ExportGoodsStockInHandler),
    (r"/api/exportGoodsStockOutDetailReport", export_handlers.ExportGoodsStockOutHandler),
    (r"/api/exportGift", export_handlers.ExportGiftHandler),
    (r"/api/exportGiftSum", export_handlers.ExportGiftSumHandler),
    (r"/api/exportStaff", export_handlers.ExportStaffHandler),
    (r"/api/exportZStaff", export_handlers.ExportZStaffHandler),
]
logging.basicConfig(filename=f"./log/web.{time.strftime('%Y_%m_%d')}.txt",
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

sched = TornadoScheduler()

# 每天提醒一周后过生日（未申请）的人可申请礼包
# sched.add_job(TaskHandler.get_next_week_birth_user_id_list, 'cron', day='1-31', hour=9, minute=0, start_date='2021-01-01 00:00:00')
# sched.add_job(TaskHandler.get_next_week_birth_user_id_list, 'interval', seconds = 5)

# 每周五提醒未申请领取的员工及时申请领取
# sched.add_job(TaskHandler.get_un_finish_user_list, 'cron', day_of_week='5', hour=9, minute=30, start_date='2021-01-01 00:00:00')
# sched.add_job(TaskHandler.get_un_finish_user_list, 'interval', seconds = 14)

sched.start()


def run():
    app = tornado.web.Application(
        HANDLERS
    )
    http_server = tornado.httpserver.HTTPServer(app)
    port = 8082
    http_server.listen(port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    run()
