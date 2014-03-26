#! -*- encoding:utf-8 -*-
import tornado.web
import tornado.ioloop
from views import MainHandler, XlsHandler
from settings import settings


application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/mmsc/center/", MainHandler),
    (r"/xls/", XlsHandler),
], **settings)

if __name__ == "__main__":

    application.listen(8000, address="0.0.0.0")
    tornado.ioloop.IOLoop.instance().start()
