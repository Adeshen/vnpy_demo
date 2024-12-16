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
)
from vnpy_evo.trader.constant import (
    Direction,
    Exchange,
    Interval,
    Offset,
    OrderType,
    Product,
    Status
)
import datetime
import pandas as pd

def parse_tick_data(json_data_bid_ask: dict, json_data_market: dict, exchange: Exchange, gateway_name:str) -> TickData:
    # 从第一个 JSON 提取数据（bids, asks, timestamp, datetime）
    bids = json_data_bid_ask.get('bids', [])
    asks = json_data_bid_ask.get('asks', [])
    timestamp = json_data_bid_ask.get('timestamp')
    datetime_str = json_data_bid_ask.get('datetime')

    # 解析 datetime 字符串为 datetime 对象
    datetime_obj = datetime.datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S.%fZ")

    # 从第二个 JSON 提取市场数据（价格等）
    symbol = json_data_market.get('symbol')
    high_price = json_data_market.get('high', 0)
    low_price = json_data_market.get('low', 0)
    last_price = json_data_market.get('last', 0)
    last_volume = json_data_market.get("info").get("lastSz", 0)
    bid_price = json_data_market.get('bid', 0)
    bid_volume = json_data_market.get('bidVolume', 0)
    ask_price = json_data_market.get('ask', 0)
    ask_volume = json_data_market.get('askVolume', 0)
    vwap = json_data_market.get('vwap', 0)
    open_price = json_data_market.get('open', 0)
    close_price = json_data_market.get('close', 0)
    pre_close = json_data_market.get('previousClose', 0)

    # 设置 bid_ask_price_1, bid_ask_volume_1 等字段
    bid_price_1, bid_volume_1 = (bids[0][0], bids[0][1]) if bids else (0, 0)
    ask_price_1, ask_volume_1 = (asks[0][0], asks[0][1]) if asks else (0, 0)

    # 其它 bids 和 asks 的数据填充到相应的字段
    bid_price_2, bid_volume_2 = (bids[1][0], bids[1][1]) if len(bids) > 1 else (0, 0)
    ask_price_2, ask_volume_2 = (asks[1][0], asks[1][1]) if len(asks) > 1 else (0, 0)

    bid_price_3, bid_volume_3 = (bids[2][0], bids[2][1]) if len(bids) > 2 else (0, 0)
    ask_price_3, ask_volume_3 = (asks[2][0], asks[2][1]) if len(asks) > 2 else (0, 0)

    bid_price_4, bid_volume_4 = (bids[3][0], bids[3][1]) if len(bids) > 3 else (0, 0)
    ask_price_4, ask_volume_4 = (asks[3][0], asks[3][1]) if len(asks) > 3 else (0, 0)

    bid_price_5, bid_volume_5 = (bids[4][0], bids[4][1]) if len(bids) > 4 else (0, 0)
    ask_price_5, ask_volume_5 = (asks[4][0], asks[4][1]) if len(asks) > 4 else (0, 0)

    # 构造 TickData 对象
    tick_data = TickData(
        gateway_name=gateway_name,
        symbol=symbol,
        exchange=exchange,
        datetime=datetime_obj,
        high_price=high_price,
        low_price=low_price,
        last_price=last_price,
        last_volume=last_volume,
        open_price=open_price,
        # close_price=close_price,
        pre_close=pre_close if pre_close != None else 0,
       
        bid_price_1=bid_price_1,
        bid_volume_1=bid_volume_1,
        ask_price_1=ask_price_1,
        ask_volume_1=ask_volume_1,
        # vwap=vwap,
        bid_price_2=bid_price_2,
        bid_volume_2=bid_volume_2,
        ask_price_2=ask_price_2,
        ask_volume_2=ask_volume_2,
        bid_price_3=bid_price_3,
        bid_volume_3=bid_volume_3,
        ask_price_3=ask_price_3,
        ask_volume_3=ask_volume_3,
        bid_price_4=bid_price_4,
        bid_volume_4=bid_volume_4,
        ask_price_4=ask_price_4,
        ask_volume_4=ask_volume_4,
        bid_price_5=bid_price_5,
        bid_volume_5=bid_volume_5,
        ask_price_5=ask_price_5,
        ask_volume_5=ask_volume_5,
        localtime=datetime_obj,
    )

    return tick_data

def convert_tickdata_to_dataframe(
        tick_data_list: list[TickData],
    )-> pd.DataFrame:
    data = []
    for tick in tick_data_list:
        row = {
            'symbol': tick.symbol,
            'exchange': tick.exchange,
            'datetime': tick.datetime,
            'name': tick.name,
            'volume': tick.volume,
            'turnover': tick.turnover,
            'open_interest': tick.open_interest,
            'last_price': tick.last_price,
            'last_volume': tick.last_volume,
            'limit_up': tick.limit_up,
            'limit_down': tick.limit_down,
            'open_price': tick.open_price,
            'high_price': tick.high_price,
            'low_price': tick.low_price,
            'pre_close': tick.pre_close,
            'bid_price_1': tick.bid_price_1,
            'bid_price_2': tick.bid_price_2,
            'bid_price_3': tick.bid_price_3,
            'bid_price_4': tick.bid_price_4,
            'bid_price_5': tick.bid_price_5,
            'ask_price_1': tick.ask_price_1,
            'ask_price_2': tick.ask_price_2,
            'ask_price_3': tick.ask_price_3,
            'ask_price_4': tick.ask_price_4,
            'ask_price_5': tick.ask_price_5,
            'bid_volume_1': tick.bid_volume_1,
            'bid_volume_2': tick.bid_volume_2,
            'bid_volume_3': tick.bid_volume_3,
            'bid_volume_4': tick.bid_volume_4,
            'bid_volume_5': tick.bid_volume_5,
            'ask_volume_1': tick.ask_volume_1,
            'ask_volume_2': tick.ask_volume_2,
            'ask_volume_3': tick.ask_volume_3,
            'ask_volume_4': tick.ask_volume_4,
            'ask_volume_5': tick.ask_volume_5,
            'localtime': tick.localtime
        }
        data.append(row)
    
    return pd.DataFrame(data)
