
from vnpy_evo.event import EventEngine
from vnpy_evo.trader.engine import MainEngine
from vnpy_evo.trader.object import HistoryRequest
from vnpy_evo.trader.constant import Exchange, Interval
from vnpy_okx import OkxGateway

import vnpy_evo.trader.setting as setting
import  vnpy_evo.trader.database  as db
import  vnpy_evo.trader.setting 
from vnpy_dolphindb import Database as Dolphindb
from vnpy_sqlite_hft import Database as Sqlitedb
import datetime

setting.SETTINGS["database.name"] = "sqlite_hft"
setting.SETTINGS["database.database"] = "database.db"


sqlite_db:Sqlitedb = db.get_database()



dolphin_db = Dolphindb(
    {    
    "database.name": "dolphindb",
    "database.database": "vnpy",
    "database.port": "8848",
    "database.host": "localhost",
    "database.user": "admin",
    "database.password": "123456",
    }
)


# print(dolphin_db)
# print(sqlite_db)

import time

st = time.time()
trades = dolphin_db.load_trade_data(
    "DOGE-USDT",
    Exchange.OKX,
    datetime.datetime(2024, 12, 1),
    datetime.datetime(2024, 12, 20)
)
print(f"cost time {time.time() - st}")

st = time.time()
trades = sqlite_db.load_trade_data(
    "DOGE-USDT",
    Exchange.OKX,
    datetime.datetime(2024, 12, 1),
    datetime.datetime(2024, 12, 20)
)
print(f"cost time {time.time() - st}")

print(len(trades))


# dolphin_db.save_trade_data(trades)
