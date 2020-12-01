import tornado.web
import tornado.httpserver
import tornado.ioloop
from handlers import goods as goods_handlers
from handlers import giftBag as giftBag_handlers
from handlers import dd as dd_handlers
from handlers import upload as upload_handlers
from handlers import order as order_handlers
from handlers import user as user_handlers
from handlers import like as like_handlers
from handlers import supply as supply_handlers
from handlers import suggest as suggest_handlers

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
    # 用户相关
    (r"/api/getUserInfoNC", user_handlers.UserInfoHandler),
    (r"/api/getUserList", user_handlers.UserListHandler),
    # 代领相关
    (r"/api/supply", supply_handlers.SupplyListHandler),
    (r"/api/cancelSupply", supply_handlers.SupplyStatusHandler),
    # 建议相关
    (r"/api/suggestDict", suggest_handlers.SuggestDictListHandler),
    (r"/api/suggest", suggest_handlers.SuggestListHandler)
]


def run():
    app = tornado.web.Application(
        HANDLERS
    )
    http_server = tornado.httpserver.HTTPServer(app)
    port = 8888
    http_server.listen(port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    run()
