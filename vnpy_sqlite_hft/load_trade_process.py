import queue
import threading
import time
import multiprocessing
from datetime import timedelta, datetime
import pandas as pd

class LoadTradeProcess(multiprocessing.Process):
    def __init__(
            self, db, symbol, exchange, 
            trade_queue, 
            share_dict,
            event: multiprocessing.Event, 
            stop_event: multiprocessing.Event,
            disk_level_start_time: datetime, 
            disk_level_timedelta: timedelta,
            tick_start_time: datetime, 
            tick_level_timedelta: timedelta,
            pre_tick_timedelta: timedelta,
        ):
        super().__init__()
        self.db = db
        self.symbol = symbol
        self.exchange = exchange

        self.disk_level_time = disk_level_start_time
        self.disk_level_timedelta = disk_level_timedelta

        self.tick_time = tick_start_time
        self.tick_level_timedelta = tick_level_timedelta
        self.pre_tick_timedelta = pre_tick_timedelta
        
        self.share_dict = share_dict

        self.trade_queue = trade_queue
        self.event = event  # 用于通知进程加载数据
        self.stop_event = stop_event  # 用于终止进程
        self.running = True

    def run(self):
        while self.running:
            if self.trade_queue.qsize() > 25600:
                time.sleep(0.5)
                continue
            # self.event.wait()  # 等待通知
            # self.event.clear()  # 清除事件，等待下一个信号
            try:
                start_time = self.disk_level_time
                end_time = self.disk_level_time + self.disk_level_timedelta
                # 从数据库加载交易数据
                trade_data = self.db.load_trade_data(
                    symbol=self.symbol, 
                    exchange=self.exchange, 
                    start=start_time, 
                    end=end_time
                )
                # 将交易数据转换成 DataFrame 并排序
                history_trades = pd.DataFrame([trade.__dict__ for trade in trade_data]).sort_values(by="datetime", ascending=False).reset_index(drop=True)
                print(f"Loaded {len(trade_data)} history trades from {start_time} - {end_time}")

                self.share_dict["history_trades"] = history_trades
                # 更新队列的时间窗口
                trade_queue = queue.Queue()

                while self.tick_time < end_time:
                    start_time = self.tick_time - self.pre_tick_timedelta
                    trade_series = history_trades[
                        (history_trades["datetime"] > start_time) & (history_trades["datetime"] < self.tick_time)
                    ]
                    trade_queue.put(trade_series)
                    self.tick_time += self.tick_level_timedelta
                
                # 将数据放入主队列
                while not trade_queue.empty():
                    self.trade_queue.put(trade_queue.get())
                self.disk_level_time = self.tick_time - self.pre_tick_timedelta
                print(f"Producer process finished, loading data completed.")
            except Exception as e:
                print(f"Error in producer process: {e}")

    def stop(self):
        self.running = False
        self.stop_event.set()