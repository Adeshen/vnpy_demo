import  vnpy_evo.trader.database  as db
import vnpy_evo.trader.setting as setting
from vnpy_evo.trader.constant import Exchange, Interval
from vnpy_evo.trader.object import TickData

from  vnpy_evo.trader.engine import MainEngine
from vnpy_sqlite_hft import TradeData

import datetime
setting.SETTINGS["database.name"] = "sqlite_hft"
setting.SETTINGS["database.database"] = "database.db"

# x and y given as array_like objects
import plotly.express as px
import pandas as pd

def draw_trade_scatter(trades: list[TradeData]):
    print("trade list size",len(trades))
    x = []
    y = []
    side_list = []  # 用于存储每个交易的side属性
    for trade in trades:
        x.append(trade.datetime)
        y.append(trade.price)
        if trade.side == 0:
            side_list.append('buy')
        # side_list.append(trade.side)
        else:
            side_list.append('sell')

    # 根据side属性设置不同颜色，这里简单示例，假设side取值为 'buy' 和 'sell'，你可按需调整
    color_discrete_map = {
        "buy": 'green',
        "sell": 'blue'
    }
    fig = px.scatter(x=x, y=y, color=side_list, color_discrete_map=color_discrete_map)
    fig.show()

def draw_trade_scatter_v2(trades: list[TradeData]):
    # 提取交易数据中的关键信息到DataFrame，方便后续处理
    trade_data = []
    for trade in trades:
        trade_data.append({
            'datetime': trade.datetime,
            'price': trade.price,
            'side': "buy" if trade.side == 0 else "sell",
            'volume': trade.volume
        })
    df = pd.DataFrame(trade_data)

    # 根据size进行分组，并统计每组的数量
    # size_counts = df['size'].value_counts().reset_index()
    # size_counts.columns = ['size', 'count']

    # 创建散点图，颜色按side区分，点的大小按size的数量映射（可根据实际调整大小比例等参数）
    fig = px.scatter(df, x='datetime', y='price', color='side',
                     size='volume', size_max=60,  # 可调整size_max控制最大点的大小
                     color_discrete_map={
                         'buy': 'green',
                         'sell': 'red'
                     },
                     hover_name='volume')  # 鼠标悬停显示size信息

    fig.show()

def draw_ticker_scatter(
        tickers: list[TickData],
    ):
    ticker_data = []
    for ticker in tickers:
        ticker_data.append({
            'datetime': ticker.datetime,
            'price': ticker.last_price,
            'volume': ticker.last_volume
        })
    df = pd.DataFrame(ticker_data)

    # 根据size进行分组，并统计每组的数量
    # size_counts = df['size'].value_counts().reset_index()
    # size_counts.columns = ['size', 'count']
    print(df)
    # 创建散点图，颜色按side区分，点的大小按size的数量映射（可根据实际调整大小比例等参数）
    fig = px.scatter(df, x='datetime', y='price',
                     size='volume', size_max=60,  # 可调整size_max控制最大点的大小
                     hover_name='volume')  # 鼠标悬停显示size信息

    fig.show()

def main():
    sqlite_db = db.get_database()

    # trades = sqlite_db.load_trade_data(
    #     symbol="DOEG-USDT", 
    #     exchange=Exchange.OKX, 
    #     start=datetime.datetime(2024, 12, 8, 2, 18) , 
    #     end=datetime.datetime(2024, 12, 8, 2, 25) )
    # draw_trade_scatter_v2(trades)

    tickers = sqlite_db.load_tick_data(
        "DOGE/USDT", 
        Exchange.OKX,
        start=datetime.datetime(2024, 12, 8, 2, 18) , 
        end=datetime.datetime(2024, 12, 17, 2, 25)                   
        )

    draw_ticker_scatter(tickers)
if __name__ == '__main__':
    main()