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
import asyncio

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

class TickDownloader:
    def __init__(self, gateway):
        self.tick_data_queue = asyncio.Queue()  # 用于保存数据的队列
        self.hft_db = db.get_database()
        self.gateway = gateway
    async def save_tick_data(self):
        # 后台任务负责异步保存数据
        while True:
            # 等待队列中有数据
            tick_datas = await self.tick_data_queue.get()
            if tick_datas:
                # 保存数据到数据库
                self.hft_db.save_tick_data(tick_datas)
                print(f"Saved {len(tick_datas)} tick data.")
                # 清空队列
                self.tick_data_queue.task_done()

    async def down_save_ticker_depth(self, symbol):
        # 创建后台保存任务
        asyncio.create_task(self.save_tick_data())

        tick_datas = []
        while True:
            tick_data = await self.gateway.subscribe_ticker_depth(symbol)
            tick_datas.append(tick_data)

            # 如果队列中数据超过100个，进行保存操作
            if len(tick_datas) > 100:
                # 将数据放入队列进行保存
                await self.tick_data_queue.put(tick_datas)
                tick_datas = []  # 清空本次的 tick_data 数据

            # 返回当前的 tick_data
        
        

async def main():
    """主入口函数"""

    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)
    connect_ccxt(main_engine)
    time.sleep(2)
    
    ccxt_okx = main_engine.get_gateway("CCXT-OKX")


    d = TickDownloader(ccxt_okx)

    await d.down_save_ticker_depth("DOGE-USDT")
    # hft_db = db.get_database()
    # tick_datas = []
    # while True:
    #     tick_data = await ccxt_okx.subscribe_ticker_depth("DOGE-USDT", )
    #     tick_datas.append(tick_data)
    #     if len(tick_datas) > 100:
    #         hft_db.save_tick_data(tick_datas)
    #         del tick_datas
if __name__ == "__main__":
    run(main())