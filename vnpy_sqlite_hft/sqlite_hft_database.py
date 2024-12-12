from datetime import datetime
from typing import List
from dataclasses import dataclass, field

from peewee import (
    AutoField,
    CharField,
    DateTimeField,
    FloatField, IntegerField,
    BooleanField,
    Model,
    SqliteDatabase as PeeweeSqliteDatabase,
    ModelSelect,
    ModelDelete,
    chunked,
    fn
)

from vnpy_evo.trader.constant import Exchange, Interval
from vnpy_evo.trader.object import BaseData, BarData, TickData
from vnpy_evo.trader.utility import get_file_path
from vnpy_evo.trader.database import (
    BaseDatabase,
    BarOverview,
    DB_TZ,
    TickOverview,
    convert_tz
)

import vnpy_sqlite 

path: str = str(get_file_path("database.db"))
db: PeeweeSqliteDatabase = PeeweeSqliteDatabase(path)

@dataclass
class TradeData(BaseData):
    symbol: str
    exchange: Exchange
    tradeid: str
    side: bool
    datetime: datetime = None

    price: float = 0
    volume: float = 0

    def __post_init__(self) -> None:
        """存储在内存的逐笔交易数据"""
        self.vt_symbol: str = f"{self.symbol}.{self.exchange.value}"
        self.vt_tradeid: str = f"{self.gateway_name}.{self.tradeid}"

@dataclass
class TradeOverview(BaseData):
    """K线数据表映射对象"""
    
    symbol: str
    exchange: str
    count: int
    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        """存储在内存的逐笔交易数据"""
        self.vt_symbol: str = f"{self.symbol}.{self.exchange.value}"

class DbTradeData(Model):
    """逐笔交易 数据表映射对象"""

    tradeid: str = CharField()
    symbol: str = CharField()
    exchange: str = CharField()
    datetime: datetime = DateTimeField()

    side: bool = BooleanField()
    price: float = FloatField()
    volume: float = FloatField()

    class Meta:
        database: PeeweeSqliteDatabase = db
        indexes: tuple = ((("tradeid", "exchange", "symbol", "datetime"), True),)

class DbTradeOverview(Model):
    """K线数据表映射对象"""
    
    symbol: str = CharField()
    exchange: str = CharField()
    count: int = IntegerField()
    start: datetime = DateTimeField()
    end: datetime = DateTimeField()

    class Meta:
        database: PeeweeSqliteDatabase = db
        indexes: tuple = ((("symbol", "exchange"), True),)


class SqliteHFT(vnpy_sqlite.Database):
    """
    The database of the sqlite_hft.
    high frequant trade database.
    """
    def __init__(self) -> None:
        """"""
        super().__init__()
        self.db.create_tables([DbTradeData, DbTradeOverview])

    def save_trade_data(self, trades: List[TradeData], stream: bool = False):
        """
        Save trade data.
        """
        trade: TradeData = trades[0]
        symbol: str = trade.symbol
        exchange: Exchange = trade.exchange

        # 将TickData数据转换为字典，并调整时区
        data: list = []

        for trade in trades:
            trade.datetime = convert_tz(trade.datetime)

            d: dict = trade.__dict__
            d["exchange"] = d["exchange"].value
            d.pop("vt_symbol")
            d.pop("vt_tradeid")
            d.pop("gateway_name")
            data.append(d)

        with self.db.atomic():
            for c in chunked(data, 10):
                DbTradeData.insert_many(c).on_conflict_replace().execute()

                # 更新K线汇总数据
        overview: DbTradeOverview = DbTradeOverview.get_or_none(
            DbTradeOverview.symbol == symbol,
            DbTradeOverview.exchange == exchange.value,
        )

        if not overview:
            overview = DbTradeOverview()
            overview.symbol = symbol
            overview.exchange = exchange.value
            overview.start = trades[0].datetime
            overview.end = trades[-1].datetime
            overview.count = len(trades)
        elif stream:
            overview.end = trades[-1].datetime
            overview.count += len(trades)
        else:
            overview.start = min(trades[0].datetime, overview.start)
            overview.end = max(trades[-1].datetime, overview.end)

            s: ModelSelect = DbTradeData.select().where(
                (DbTradeData.symbol == symbol)
                & (DbTradeData.exchange == exchange.value)
            )
            overview.count = s.count()

        overview.save()


    def load_trade_data(self, symbol: str, exchange: Exchange, start: datetime, end: datetime):
        """
        Load trade data.
        """
        query: ModelSelect = DbTradeData.select().where(
            DbTradeData.symbol == symbol
            & DbTradeData.exchange == exchange.value
            & DbTradeData.datetime >= start
            & DbTradeData.datetime <= end
        )

        trades: List[TradeData] = []
        for db_trade in query:
            
            trade: TradeData = TradeData(
                gateway_name="DB",
                symbol=db_trade.symbol,
                exchange=Exchange(db_trade.exchange),
                tradeid=db_trade.tradeid,
                datetime=datetime.fromtimestamp(db_trade.datetime.timestamp(), DB_TZ),
                side=db_trade.side,
                price=db_trade.price,
                volume=db_trade.volume,
            )

            trades.append(trade)

        return trades
    
    def delete_trade_data(
        self, 
        symbol: str,
        exchange: Exchange,
    ) -> int:
        """删除K线数据"""
        d: ModelDelete = DbTradeData.delete().where(
            (DbTradeData.symbol == symbol)
            & (DbTradeData.exchange == exchange.value)
        )
        count: int = d.execute()

        # 删除K线汇总数据
        d2: ModelDelete = DbTradeOverview.delete().where(
            (DbTradeOverview.symbol == symbol)
            & (DbTradeOverview.exchange == exchange.value)
        )
        d2.execute()

        return count

    def get_trade_overview(self) -> List[TradeOverview]:
        """查询数据库中的Tick汇总信息"""
        
        s: ModelSelect = DbTradeOverview.select()
        overviews: list = []
        for overview in s:
            overview.exchange = Exchange(overview.exchange)
            overviews.append(overview)

        return overviews
    
    def init_trade_overview(self) -> None:
        """初始化数据库中的K线汇总信息"""
        s: ModelSelect = (
            DbTradeData.select(
                DbTradeData.symbol,
                DbTradeData.exchange,
            ).group_by(
                DbTradeData.symbol,
                DbTradeData.exchange,
            )
        )

        for data in s:
            overview: DbTradeOverview = DbTradeOverview()
            overview.symbol = data.symbol
            overview.exchange = data.exchange
            overview.count = data.count

            start_bar: DbTradeData = (
                DbTradeData.select()
                .where(
                    (DbTradeData.symbol == data.symbol)
                    & (DbTradeData.exchange == data.exchange)
                )
                .order_by(DbTradeData.datetime.asc())
                .first()
            )
            overview.start = start_bar.datetime

            end_bar: DbTradeData = (
                DbTradeData.select()
                .where(
                    (DbTradeData.symbol == data.symbol)
                    & (DbTradeData.exchange == data.exchange)
                )
                .order_by(DbTradeData.datetime.desc())
                .first()
            )
            overview.end = end_bar.datetime

            overview.save()