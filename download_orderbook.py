from vnpy_evo.event import EventEngine
from vnpy_evo.trader.engine import MainEngine
from vnpy_evo.trader.object import HistoryRequest
from vnpy_evo.trader.constant import Exchange, Interval
from vnpy_okx import OkxGateway

import vnpy_evo.trader.setting as setting
import  vnpy_evo.trader.database  as db

import datetime
import os
import threading
import time
import ccxt_gateway 
from asyncio import run

setting.SETTINGS["database.name"] = "sqlite_hft"
setting.SETTINGS["database.database"] = "database.db"


def connect_ccxt(main_engine: MainEngine):
    """在单独线程中执行连接操作的函数"""
    okx_setting = {
            "API Key": os.getenv("OKX_API_KEY"),
            "Secret Key": os.getenv("OKX_SECRET_KEY"),
            "Passphrase": os.getenv("OKX_PASSPHRASE"),
            "Server": "REAL",
            "Proxy Host": None,
            "Proxy Port": "0",
        }
    OkxGateway.default_setting= okx_setting
    ccxt_gateway.OkxGateway.default_setting = okx_setting
    main_engine.write_log("start connect","OKX")

    main_engine.add_gateway(ccxt_gateway.OkxGateway)
    main_engine.write_log("conected ok","OKX")


async def main():
    """主入口函数"""

    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)
    connect_ccxt(main_engine)
    time.sleep(2)
    
    ccxt_okx = main_engine.get_gateway("CCXT-OKX")

    order_book = ccxt_okx.query_order_book("DOGE-USDT")
    # print(order_book)
    hft_db = db.get_database()
    hft_db.save_orderbook_data(order_book, "OKX")

    while True:
        order_book = await ccxt_okx.subscribe_orderbook("DOGE-USDT", limit=5)
        # print(book.datetime)
        # print(book.timestamp)
        print(order_book)
        print("\n\n\n")
        hft_db.save_orderbook_data(order_book, "OKX")
if __name__ == "__main__":
    run(main())