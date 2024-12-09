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

setting.SETTINGS["database.name"] = "sqlite"
setting.SETTINGS["database.database"] = "database.db"


def connect_in_thread(main_engine: MainEngine):
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
    main_engine.write_log("start connect","OKX")
    okx = main_engine.get_gateway("OKX")

    okx.rest_api.connect(
        okx_setting["API Key"],
        okx_setting["Secret Key"],
        okx_setting["Passphrase"],
        okx_setting["Server"],
        okx_setting["Proxy Host"],
        int(okx_setting["Proxy Port"])
    )
    # main_engine.connect(
    #     setting=okx_setting,
    #     gateway_name="OKX",
    # )
    main_engine.write_log("conected ok","OKX")

def main():
    """主入口函数"""

    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)
    main_engine.add_gateway(OkxGateway)
    # connect_thread = threading.Thread(target=connect_in_thread, args=(main_engine,))
    # connect_thread.start()
    connect_in_thread(main_engine)
    time.sleep(2)
    req = HistoryRequest(
        symbol="BTC-USDT",
        exchange=Exchange.OKX,
        start=datetime.datetime(2024, 9, 1),
        end=datetime.datetime(2024, 9, 2),
        interval=Interval.MINUTE
        )
    
    bardatas = main_engine.query_history(
        req=req,
        gateway_name="OKX",
    )

    sqlite_db = db.get_database()
    sqlite_db.save_bar_data(bardatas)
    # main_engine.write_log("bardata", "OKX")
    # main_engine.write_log(bardatas, "OKX")
    
if __name__ == "__main__":
    main()