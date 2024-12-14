from vnpy_evo.event import EventEngine
from vnpy_evo.trader.engine import MainEngine
from vnpy_evo.trader.object import HistoryRequest
from vnpy_evo.trader.constant import Exchange, Interval
from vnpy_okx import OkxGateway

import vnpy_evo.trader.setting as setting
import  vnpy_evo.trader.database  as db

from datetime import datetime
import os
import threading
import time
import vnpy_novastrategy

from vnpy_novastrategy.backtesting import (
    BacktestingEngine,
    Interval,
    OptimizationSetting
)

from strategy.trend_strategy import TrendStrategy 
from strategy.turtle_strategy import TurtleStrategy 

setting.SETTINGS["database.name"] = "sqlite_hft"
setting.SETTINGS["database.database"] = "database.db"


engine = BacktestingEngine()

engine.set_parameters(
    interval=Interval.MINUTE,
    start=datetime(2024, 1, 1),
    end=datetime(2024,3,1),
    capital=1_000_000,
)

engine.add_contract(
    "BTC-USDT.OKX",
    pricetick=0.01,
    size=1,
    min_volume=0.01,
    rate=0.014 / 100,
    slippage=0.0
)

# setting = {
#     "boll_window": 7,
#     "boll_dev": 1,
#     "atr_window": 2,
#     "sl_multiplier": 6.5,
#     "risk_level": 5000
# }
# engine.add_strategy(TrendStrategy, setting)

setting = {
    "entry_window": 70,
    "exit_window": 60,
    "atr_window": 12,
    "risk_level": 5000
}

engine.add_strategy(TurtleStrategy, setting)

engine.load_data()
engine.run_backtesting()
result = engine.calculate_result()

print(result)
for trade in engine.trades.values():
    print(f"{trade.tradeid} [{trade.datetime}] {trade.direction.value} {trade.volume} @ {trade.price}")


