import  vnpy_evo.trader.database  as db
import vnpy_evo.trader.setting as setting
from vnpy_evo.trader.constant import Exchange, Interval, Direction
from vnpy_evo.trader.object import TickData, BarData

from  vnpy_evo.trader.engine import MainEngine
from vnpy_sqlite_hft import TradeData
import plotly.graph_objects as go
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

def draw_trade_and_bar_scatter(
        bars: list[BarData],
        trades: list[TradeData]
    ):
    # 处理BarData，转换为适合绘图的数据格式
    trade_min_time = min([trade.datetime for trade in trades])
    trade_max_time = max([trade.datetime for trade in trades])
    print(f"TradeData 最早时间: {trade_min_time}, 最晚时间: {trade_max_time}")

    # 处理BarData，过滤出时间在 TradeData 范围内的Bar
    bar_data = []
    for bar in bars:
        if trade_min_time <= bar.datetime <= trade_max_time:
            bar_data.append({
                'datetime': bar.datetime,
                'open': bar.open_price, 
                'high': bar.high_price, 
                'low': bar.low_price,
                'close': bar.close_price,  # 使用 'close' 作为价格
                'volume': bar.volume
            })
    df_bars = pd.DataFrame(bar_data)

    # 找到最早和最晚的时间
    bar_min_time = df_bars['datetime'].min()
    bar_max_time = df_bars['datetime'].max()
    print(f"BarData 最早时间: {bar_min_time}, 最晚时间: {bar_max_time}")

    # 处理TradeData，过滤出时间在 BarData 范围内的交易
    trade_data_long = []  # 存储 Long 交易
    trade_data_short = []  # 存储 Short 交易
    for trade in trades:
        if bar_min_time <= trade.datetime <= bar_max_time:
            trade_info = {
                'datetime': trade.datetime,
                'price': trade.price,
                'volume': trade.volume
            }
            if trade.direction == Direction.LONG:
                trade_data_long.append(trade_info)
            elif trade.direction == Direction.SHORT:
                trade_data_short.append(trade_info)
    print(f"trade 交易时间：long({len(trade_data_long)}) short({len(trade_data_short)}) ")
    df_trades_long = pd.DataFrame(trade_data_long)
    df_trades_short = pd.DataFrame(trade_data_short)

    # 创建价格的折线图
    price_trace = go.Scatter(
        x=df_bars['datetime'],
        y=df_bars['close'],
        mode='lines',
        name='Price',
        line=dict(color='royalblue')
    )

    # 创建交易量的条形图
    volume_trace = go.Bar(
        x=df_bars['datetime'],
        y=df_bars['volume'],
        name='Volume',
        marker=dict(color='orange'),
        yaxis='y2'  # 绑定到第二个 y 轴
    )

    # 创建 Long 交易数据的散点图
    trade_trace_long = go.Scatter(
        x=df_trades_long['datetime'],
        y=df_trades_long['price'],
        mode='markers',
        name='Long Trade',
        marker=dict(color='green', size=10, symbol='triangle-up')
    )

    # 创建 Short 交易数据的散点图
    trade_trace_short = go.Scatter(
        x=df_trades_short['datetime'],
        y=df_trades_short['price'],
        mode='markers',
        name='Short Trade',
        marker=dict(color='red', size=10, symbol='triangle-down')
    )

    # 创建布局，设置双Y轴
    layout = go.Layout(
        title='Price, Volume and Trades Over Time',
        xaxis=dict(title='Datetime'),
        yaxis=dict(
            title='Price',
            side='left',
            showgrid=False
        ),
        yaxis2=dict(
            title='Volume',
            side='right',
            overlaying='y',  # 与左边的y轴重叠
            showgrid=False
        ),
        barmode='stack',  # 条形图的叠加方式
        hovermode='x unified'  # 鼠标悬停时显示统一信息
    )

    # 创建图形并显示
    fig = go.Figure(data=[price_trace, trade_trace_long, trade_trace_short], layout=layout)
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