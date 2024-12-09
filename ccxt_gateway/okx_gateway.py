from vnpy_evo.event import EventEngine
from vnpy_evo.trader.constant import (
    Direction,
    Exchange,
    Interval,
    Offset,
    OrderType,
    Product,
    Status
)
from vnpy_evo.trader.gateway import BaseGateway
from vnpy_evo.trader.utility import round_to, ZoneInfo
from vnpy_evo.trader.object import (
    AccountData,
    BarData,
    CancelRequest,
    ContractData,
    HistoryRequest,
    OrderData,
    OrderRequest,
    PositionData,
    SubscribeRequest,
    TickData,
    TradeData
)
from vnpy_rest import Request, RestClient
from vnpy_websocket import WebsocketClient
import vnpy_okx  

import ccxt
import datetime

def parse_timestamp(timestamp) -> datetime.datetime:
    """Parse timestamp to datetime"""
    dt: datetime.datetime = datetime.datetime.fromtimestamp(int(timestamp) / 1000)
    return dt

class OkxGateway(vnpy_okx.OkxGateway):
    """
    The OKX trading gateway for VeighNa.

    Only support net mode
    """

    default_name = "CCXT-OKX"

    default_setting: dict = {
        "API Key": "",
        "Secret Key": "",
        "Passphrase": "",
    }

    def __init__(self, event_engine: EventEngine, gateway_name: str) -> None:
        """
        The init method of the gateway.

        event_engine: the global event engine object of VeighNa
        gateway_name: the unique name for identifying the gateway
        """
        super().__init__(event_engine, gateway_name)

        self.ccxt_okx = ccxt.okx(
            {
                "apiKey": self.default_setting["API Key"],
                "secret": self.default_setting["Secret Key"],
                "password": self.default_setting["Passphrase"],
                # "options": {'defaultType': 'futures'}
            }
        )

    def query_history(self, 
                      req: HistoryRequest,
                      ):

        default_limit = 1000
        timeframe_map = {
            '1s': 1,
            '1m': 60,
            '15m': 900,
            '1h': 3600,
            '1d': 86400,
        }
        time_detla = (req.end - req.start)
        print(time_detla)
        # 获取数据
        request_count = (time_detla.total_seconds()/timeframe_map[req.interval.value]) // default_limit + 1

        history_bars: list[BarData] = []
        exchange = self.ccxt_okx
        for i in range(int(request_count)):
            print(i," in ", int(request_count))

            start_time = req.start + datetime.timedelta(seconds=i * default_limit * timeframe_map[req.interval.value])
            
            ohlcvs = exchange.fetch_ohlcv(req.symbol, 
                                         req.interval.value, 
                                         start_time.timestamp(),
                                         limit=default_limit)
            part_bars: list[BarData] = []
            for ohlcv in ohlcvs:
                bar = BarData(
                    gateway_name=self.gateway_name,
                    symbol=req.symbol,
                    exchange=Exchange.OKX,
                    interval=req.interval,
                    datetime=parse_timestamp(ohlcv[0]),
                    open_price=float(ohlcv[1]),
                    high_price=(ohlcv[2]),
                    low_price=(ohlcv[3]),
                    close_price=(ohlcv[4]),
                )
                part_bars.append(bar)
            start_time = part_bars[0].datatime
            end_time = part_bars[-1].datatime
            msg: str = f"Query part kline history finished, {req.symbol} - {req.interval.value}, {start_time} - {end_time}"
            self.write_log(msg)

            history_bars.extend(part_bars)

        start_time = history_bars[0].datatime
        end_time = history_bars[-1].datatime
        msg: str = f"Query all kline history finished, {req.symbol} - {req.interval.value}, {start_time} - {end_time}"
        self.write_log(msg)

        return history_bars