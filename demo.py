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
    ccxt_gateway.OkxGateway.default_setting = okx_setting
    main_engine.write_log("start connect","OKX")

    main_engine.add_gateway(ccxt_gateway.OkxGateway)

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


def query_long_history_to_db(
        main_engine: MainEngine,
        symbol: str,
        exchange: Exchange, 
        start: datetime.datetime, 
        end: datetime.datetime , 
        interval: Interval):
    sqlite_db = db.get_database()

    # 将一个start 到 end 的请求 分割成 多个请求
    # 每个请求的时间间隔
    interval_time = end - start
    

    default_limit = 300
    timeframe_map = {
        '1s': 1,
        '1m': 60,
        '15m': 900,
        '1h': 3600,
        '1d': 86400,
        "d": 86400,
        "w": 86400 * 7,
    }
    request_count = (interval_time.total_seconds() / timeframe_map[interval.value]) // default_limit + 1
    print(f"interval_time: {interval_time.total_seconds()} s, request count {request_count}")

    for i in range(int(request_count)):
        start_time = start + datetime.timedelta(seconds=default_limit * timeframe_map[interval.value] * i)
        end_time = start + datetime.timedelta(seconds=default_limit * timeframe_map[interval.value] * (i + 1))
        if end_time > end:
            end_time = end
        
        print(start_time)
        print(end_time)
        req = HistoryRequest(
            symbol=symbol,
            exchange=exchange,
            start=start_time,
            end=end_time,
            interval=interval
        )
        bardatas = main_engine.query_history(
            req=req,
            gateway_name="CCXT-OKX",
        )
        sqlite_db.save_bar_data(bardatas)


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
        start=datetime.datetime(2020, 1, 1),
        end=datetime.datetime(2024, 12, 8),
        interval=Interval.MINUTE
        )
    
    
    sqlite_db = db.get_database()
    sqlite_db.delete_bar_data("BTC-USDT", Exchange.OKX, Interval.MINUTE)
    # query_long_history_to_db(
    #     main_engine=main_engine,
    #     symbol="BTC-USDT",
    #     exchange=Exchange.OKX,
    #     start=datetime.datetime(2020, 1, 1),
    #     end=datetime.datetime(2024, 12, 8),
    #     interval=Interval.MINUTE
    # )
    
    bardatas = main_engine.query_history(
        req=req,
        gateway_name="CCXT-OKX",
    )

    sqlite_db.save_bar_data(bardatas)

    # main_engine.write_log("bardata", "OKX")
    # main_engine.write_log(bardatas, "OKX")
    
if __name__ == "__main__":
    main()