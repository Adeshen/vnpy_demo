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

def split_download(req: HistoryRequest, data_gateway):
    """
    分批次下载历史数据，从start到end数据，同时存储在数据库中
    """
    sqlite_db = db.get_database()
    start_time = req.start
    end_time = req.end
    # 时间间隔设置为1小时
    time_delta = datetime.timedelta(hours=1)
    current_time = start_time
    while current_time < end_time:
        # 构建每批次的请求范围
        batch_req = HistoryRequest(
            symbol=req.symbol,
            exchange=req.exchange,
            start=current_time,
            end=min(current_time + time_delta, end_time),  # 避免超出结束时间
            interval=req.interval
        )
        trade_data = data_gateway.query_history_trades(batch_req)
            # 将获取到的交易数据保存到数据库中
        sqlite_db.save_trade_data(trade_data)
        current_time += time_delta
        # print(trade_data)
        # print(trade_data)
    data_gateway.write_log("downloaded data", "OKX", )
def main():
    """主入口函数"""

    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)
    connect_ccxt(main_engine)
    time.sleep(2)
    
    ccxt_okx = main_engine.get_gateway("CCXT-OKX")

    req = HistoryRequest(
        symbol="DOGE-USDT",
        exchange=Exchange.OKX,
        start=datetime.datetime(2024, 12, 8),
        end=datetime.datetime(2024, 12, 9),
        interval=Interval.MINUTE
    )
    # trade_data = ccxt_okx.query_history_trades(
    #     req
    # )
    # print(len(trade_data))
    
    split_download(req, ccxt_okx)
if __name__ == "__main__":
    main()