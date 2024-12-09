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
import vnpy_novastrategy

setting.SETTINGS["database.name"] = "sqlite"
setting.SETTINGS["database.database"] = "database.db"

back = vnpy_novastrategy.BacktestingEngine()