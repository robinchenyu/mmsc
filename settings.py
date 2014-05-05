#! -*- encoding: utf-8 -*-
import os
settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    # "cookie_secret": "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
    # "login_url": "/login",
    # "xsrf_cookies": True,
    "debug": True,
    "mmsc_port": 8000,
    "mmsc_path": r"/mmsc/center/",
    "uma_mms_url": "http://10.116.40.67:8888/",
}
