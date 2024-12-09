import  vnpy_evo.trader.database  as db
import vnpy_evo.trader.setting as setting
from vnpy_evo.trader.constant import Exchange, Interval

from  vnpy_evo.trader.engine import MainEngine

import datetime
setting.SETTINGS["database.name"] = "sqlite"
setting.SETTINGS["database.database"] = "database.db"

sqlite_db = db.get_database()

data = sqlite_db.load_bar_data("BTCUSDT", Exchange.OKX, Interval.MINUTE,
                start=datetime.datetime(2023, 9, 1),
        end=datetime.datetime(2024, 9, 1),
                               )

print(data)