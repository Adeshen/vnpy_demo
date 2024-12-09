# vnpy demo

主要用于熟悉vnpy的各个组件实际使用功能呢。


## download history data

通过ccxt 提供的fetch_ohlcv接口，将其集成到okxgateway中，可以正常下载数据。
但是由于okx的接口， 限制成100条/请求。
因而请求需要按照 时间 来进行拆分，，借此实现下载任意年份的数据。

