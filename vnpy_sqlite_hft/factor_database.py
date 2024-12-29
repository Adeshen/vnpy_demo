from datetime import datetime
from typing import List
from dataclasses import dataclass, field
from typing import Dict
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


path: str = str(get_file_path("database.db"))
db: PeeweeSqliteDatabase = PeeweeSqliteDatabase(path)

class DbFactorData(Model):
    """因子数据表映射对象"""
    id = AutoField()  # 主键
    symbol = CharField()  # 标的代码
    exchange = CharField()  # 交易所
    datetime = DateTimeField()  # 时间戳
    factor_name = CharField()  # 因子名称
    factor_value = FloatField()  # 因子值

    class Meta:
        database = db  # 使用全局的SQLite数据库
        indexes = ((("symbol", "exchange", "datetime", "factor_name"), True),)  # 复合唯一索引


class DbFactorPerformance(Model):
    """因子表现结果表映射对象"""
    id = AutoField()  # 主键
    factor_name = CharField()  # 因子名称
    start_date = DateTimeField()  # 起始日期
    end_date = DateTimeField()  # 结束日期
    mean_return = FloatField(null=True)  # 平均收益
    std_deviation = FloatField(null=True)  # 标准差
    sharpe_ratio = FloatField(null=True)  # 夏普比率
    max_drawdown = FloatField(null=True)  # 最大回撤
    ic_mean = FloatField(null=True)  # IC均值
    ic_std = FloatField(null=True)  # IC标准差
    ir = FloatField(null=True)  # 信息比率
    created_at = DateTimeField(default=datetime.now)  # 记录创建时间

    class Meta:
        database = db  # 使用全局的SQLite数据库
        indexes = ((("factor_name", "start_date", "end_date"), True),)  # 复合唯一索引

class FactorPerformanceManager:
    """因子表现结果管理类"""

    def __init__(self):
        """初始化"""
        self.db = db
        self.db.connect()
        self.db.create_tables([DbFactorPerformance])  # 创建因子表现结果表

    def save_factor_performance(self, performance_data: Dict) -> bool:
        """
        保存因子表现结果
        :param performance_data: 因子表现数据，包含factor_name, start_date, end_date, mean_return, std_deviation, sharpe_ratio, max_drawdown, ic_mean, ic_std, ir
        :return: 是否保存成功
        """
        # 将数据插入到数据库中
        DbFactorPerformance.create(**performance_data)
        return True

    def load_factor_performance(
        self,
        factor_name: str,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> List[Dict]:
        """
        读取因子表现结果
        :param factor_name: 因子名称
        :param start_date: 起始日期（可选）
        :param end_date: 结束日期（可选）
        :return: 因子表现结果列表
        """
        query = DbFactorPerformance.select().where(
            DbFactorPerformance.factor_name == factor_name
        )
        if start_date:
            query = query.where(DbFactorPerformance.start_date >= start_date)
        if end_date:
            query = query.where(DbFactorPerformance.end_date <= end_date)

        performance_results = []
        for db_performance in query:
            performance_results.append({
                "factor_name": db_performance.factor_name,
                "start_date": db_performance.start_date,
                "end_date": db_performance.end_date,
                "mean_return": db_performance.mean_return,
                "std_deviation": db_performance.std_deviation,
                "sharpe_ratio": db_performance.sharpe_ratio,
                "max_drawdown": db_performance.max_drawdown,
                "ic_mean": db_performance.ic_mean,
                "ic_std": db_performance.ic_std,
                "ir": db_performance.ir,
                "created_at": db_performance.created_at,
            })
        return performance_results

    def delete_factor_performance(
        self,
        factor_name: str,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> int:
        """
        删除因子表现结果
        :param factor_name: 因子名称
        :param start_date: 起始日期（可选）
        :param end_date: 结束日期（可选）
        :return: 删除的记录数
        """
        query = DbFactorPerformance.delete().where(
            DbFactorPerformance.factor_name == factor_name
        )
        if start_date:
            query = query.where(DbFactorPerformance.start_date >= start_date)
        if end_date:
            query = query.where(DbFactorPerformance.end_date <= end_date)
        return query.execute()
    

class CrossSectionalFactorStorage:
    """截面因子存放类"""

    def __init__(self):
        """初始化"""
        self.db = db
        self.db.connect()
        self.db.create_tables([DbFactorData])  # 创建因子数据表

    def save_cross_sectional_factors(self, factors: List[Dict]) -> bool:
        """
        保存截面因子数据
        :param factors: 因子数据列表，每个元素是一个字典，包含symbol, exchange, datetime, factor_name, factor_value
        :return: 是否保存成功
        """
        # 将数据转换为字典列表
        data = []
        for item in factors:
            item["datetime"] = convert_tz(item["datetime"])  # 调整时区
            data.append(item)

        # 使用upsert操作将数据更新到数据库中
        with self.db.atomic():
            for c in chunked(data, 50):
                DbFactorData.insert_many(c).on_conflict_replace().execute()
        return True

    def load_cross_sectional_factors(
        self,
        datetime: datetime,
        factor_name: str,
        exchange: str = None
    ) -> List[Dict]:
        """
        读取某一时间点的截面因子数据
        :param datetime: 时间点
        :param factor_name: 因子名称
        :param exchange: 交易所（可选）
        :return: 因子数据列表
        """
        query = DbFactorData.select().where(
            (DbFactorData.datetime == datetime)
            & (DbFactorData.factor_name == factor_name)
        )
        if exchange:
            query = query.where(DbFactorData.exchange == exchange)

        factors = []
        for db_factor in query:
            factors.append({
                "symbol": db_factor.symbol,
                "exchange": db_factor.exchange,
                "datetime": db_factor.datetime,
                "factor_name": db_factor.factor_name,
                "factor_value": db_factor.factor_value,
            })
        return factors

    def delete_cross_sectional_factors(
        self,
        datetime: datetime,
        factor_name: str,
        exchange: str = None
    ) -> int:
        """
        删除某一时间点的截面因子数据
        :param datetime: 时间点
        :param factor_name: 因子名称
        :param exchange: 交易所（可选）
        :return: 删除的记录数
        """
        query = DbFactorData.delete().where(
            (DbFactorData.datetime == datetime)
            & (DbFactorData.factor_name == factor_name)
        )
        if exchange:
            query = query.where(DbFactorData.exchange == exchange)
        return query.execute()

    def get_cross_sectional_factor_names(self) -> List[str]:
        """
        获取所有截面因子名称
        :return: 因子名称列表
        """
        query = DbFactorData.select(DbFactorData.factor_name).distinct()
        return [item.factor_name for item in query]
    
def test_cross_factor():
    # 初始化截面因子存放类
    factor_storage = CrossSectionalFactorStorage()

    # 保存截面因子数据
    factors = [
        {
            "symbol": "000001",
            "exchange": "SSE",
            "datetime": datetime(2023, 10, 1),
            "factor_name": "momentum",
            "factor_value": 0.12,
        },
        {
            "symbol": "000002",
            "exchange": "SSE",
            "datetime": datetime(2023, 10, 1),
            "factor_name": "momentum",
            "factor_value": 0.15,
        },
    ]
    factor_storage.save_cross_sectional_factors(factors)

    # 读取某一时间点的截面因子数据
    loaded_factors = factor_storage.load_cross_sectional_factors(
        datetime=datetime(2023, 10, 1),
        factor_name="momentum",
        exchange="SSE"
    )
    print(loaded_factors)

    # 删除某一时间点的截面因子数据
    deleted_count = factor_storage.delete_cross_sectional_factors(
        datetime=datetime(2023, 10, 1),
        factor_name="momentum",
        exchange="SSE"
    )
    print(f"Deleted {deleted_count} records")

    # 获取所有截面因子名称
    factor_names = factor_storage.get_cross_sectional_factor_names()
    print(f"Factor names: {factor_names}")


def test_factor_performance():

    # 初始化因子表现结果管理类
    performance_manager = FactorPerformanceManager()

    # 保存因子表现结果
    performance_data = {
        "factor_name": "momentum",
        "start_date": datetime(2023, 1, 1),
        "end_date": datetime(2023, 10, 1),
        "mean_return": 0.12,
        "std_deviation": 0.05,
        "sharpe_ratio": 1.2,
        "max_drawdown": -0.08,
        "ic_mean": 0.15,
        "ic_std": 0.03,
        "ir": 0.5,
    }
    performance_manager.save_factor_performance(performance_data)

    # 读取因子表现结果
    loaded_performance = performance_manager.load_factor_performance(
        factor_name="momentum",
        start_date=datetime(2023, 1, 1),
        end_date=datetime(2023, 12, 31)
    )
    print(loaded_performance)

    # 删除因子表现结果
    deleted_count = performance_manager.delete_factor_performance(
        factor_name="momentum",
        start_date=datetime(2023, 1, 1),
        end_date=datetime(2023, 12, 31)
    )
    print(f"Deleted {deleted_count} records")


if __name__ == "__main__":
    test_cross_factor()
    test_factor_performance()