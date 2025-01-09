# vnpy demo

主要用于熟悉vnpy的各个组件实际使用功能呢。

## usage
1. 安装依赖
```
pip install -r requestments.txt
```
注意: ta-lib 可能安装失败，可使用 conda install -c conda-forge ta-lib

2. 设置环境python环境库的环境变量

```
export PYTHONPATH=$(this project path)
```

3. 获取OKX的api key(自行在okx上申请)。只是下载K线与历史交易数据，无需申请。

```
export OKX_API_KEY=xxxxxxxxx
export OKX_SECRET_KEY=xxxxxxxxxx
export OKX_PASSPHRASE=xxxxx
```

## download history data


1. 历史k线数据下载: 
将ccxt 提供的fetch_ohlcv接口集成到okxgateway中，可以下载数据。
但是由于okx的接口， 限制成100条/请求，增加分片下载的机制，借此实现下载任意年份的K线数据。可以存储在sqlite数据库中。

2. 历史交易数据下载:
此外，针对高频场景，额外实现了对接okx的历史交易数据的接口，可以实现下载最近三个月的历史交易数据，同样保存在sqlite数据库中。

3. 实时orderbook数据下载：
提供了http接口，与websocket接口。okx的websocket普通vip大概速度是推送一次/100ms。

4. 实时tick数据下载：
提供了websocket接口。将orderbook数据和ticker market数据整合到一个tickdata当中，并存储到sqlite数据库中。

5. dolphindb 测试：
同样查询400条数据
dolphindb 只需要1.133秒，
而 sqlitedb 需要 几分钟，差距数百倍，决定后续弃用sqlite

## draw analysis

1. 实现绘制历史交易的图表。
![draw_trade_data](assets/draw_trade_data.png)


# backtest analysis

``` bash
(base) root@VM-8-15-ubuntu:~/vnpy_demo# python demo_backtest.py 
2024-12-14 16:49:09.034753      Loading history data.
2024-12-14 16:49:12.530133      Bar data of BTC-USDT.OKX loaded, total count: 86401.
2024-12-14 16:49:12.530195      History data all loaded.
2024-12-14 16:49:12.638018      The strategy is inited.
2024-12-14 16:49:12.638085      Starting to replay history data.
100%|█████████████████████████████████████████████████████████████████████████████████████| 72001/72001 [00:00<00:00, 215069.61it/s]
2024-12-14 16:49:12.975401      Replaying history data finished.
2024-12-14 16:49:12.978638      Calculating daily PnL.
2024-12-14 16:49:12.980412      Calculation of daily PnL finished.
            trade_count     turnover  commission  slippage  trading_pnl  holding_pnl   total_pnl        net_pnl
date                                                                                                           
2024-01-11            1   704070.640   98.569890       0.0    19550.986        0.000   19550.986   19452.416110
2024-01-12            0        0.000    0.000000       0.0        0.000   -35712.495  -35712.495  -35712.495000
2024-01-13            2  1105376.971  154.752776       0.0    27390.051   -20316.751    7073.300    6918.547224
2024-01-14            0        0.000    0.000000       0.0        0.000     2356.578    2356.578    2356.578000
2024-01-15            0        0.000    0.000000       0.0        0.000     5971.329    5971.329    5971.329000
2024-01-16            1   411364.560   57.591038       0.0      -21.873    -9276.054   -9297.927   -9355.518038
2024-01-17            1   612665.388   85.773154       0.0   -12898.620        0.000  -12898.620  -12984.393154
2024-01-18            0        0.000    0.000000       0.0        0.000     2014.924    2014.924    2014.924000
2024-01-19            2  1546535.010  216.514901       0.0    42697.165   -24294.872   18402.293   18185.778099
2024-01-20            0        0.000    0.000000       0.0        0.000   -15207.210  -15207.210  -15207.210000
```