import os
import pandas as pd
import re
from datetime import datetime
import pyarrow.feather as feather
from functools import partial
from concurrent.futures import ProcessPoolExecutor, as_completed

def read_feather_data(symbol: str, start_time: str, end_time: str, base_dir: str = "./okx_feather_data"):
    """
    根据币种和时间范围读取Feather数据

    参数:
    symbol (str): 交易对符号，如 "BTC-USDT-SWAP"
    start_time (str): 开始时间（YYYY-MM-DD格式）
    end_time (str): 结束时间（YYYY-MM-DD格式）
    base_dir (str): Feather文件根目录

    返回:
    pd.DataFrame: 合并后的数据
    """

    if isinstance(start_time, str):
        # 转换时间字符串为datetime对象
        start_date = datetime.strptime(start_time, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_time, "%Y-%m-%d").date()
    else:
        start_date = start_time.date()
        end_date = end_time.date()

    # 构建交易对目录路径
    pair_dir = os.path.join(base_dir, symbol)

    # 检查目录是否存在
    if not os.path.exists(pair_dir):
        raise FileNotFoundError(f"交易对目录不存在: {pair_dir}")

    # 收集符合条件的文件
    combined_df = None
    for date in pd.date_range(start=start_date, end=end_date):
        date_str = date.strftime("%Y-%m-%d")
        file_name = f"{symbol}-trades-{date_str}.feather"
        file_path = os.path.join(pair_dir, file_name)

        if os.path.exists(file_path):
            df = feather.read_feather(file_path)
            if combined_df is None:
                combined_df = df
            else:
                combined_df = pd.concat([combined_df, df], ignore_index=True)
            logger.info(f"读取文件: {file_path}, 日期: {date_str}")

    if combined_df is None:
        return pd.DataFrame()
    # 确保时间列正确排序
    combined_df['datetime'] = pd.to_datetime(combined_df['datetime'], unit='ms')

    return combined_df


def check_missing_minutes(ohlcv_df, freq='1min'):
    if ohlcv_df.empty:
        logger.info("数据为空，无法检查缺失的分钟")
        return []

    # 1. 生成完整的分钟级时间范围
    full_time_range = pd.date_range(
        start=ohlcv_df.index.min(),
        end=ohlcv_df.index.max(),
        freq=freq
    )

    # 2. 提取实际存在的分钟索引
    existing_minutes = ohlcv_df.index

    # 3. 计算缺失的分钟
    missing_minutes = full_time_range.difference(existing_minutes)

    return missing_minutes


def merge_ohlcv_data(symbol, start_time, end_time, freq='1min', file_format='feather'):
    """
    合并多个OHLCV数据

    参数:
    symbol (str): 交易对符号
    start_time (str): 开始时间（YYYY-MM-DD格式）
    end_time (str): 结束时间（YYYY-MM-DD格式）
    freq (str): 重采样频率

    返回:
    pd.DataFrame: 合并后的OHLCV数据
    """
    count = 0
    ohlcvs = pd.DataFrame()
    ohlc_path = f"{freq}_{start_time}_{end_time}"
    os.makedirs(ohlc_path, exist_ok=True)
    # file_path = f"{ohlc_path}/{symbol}_{freq}_{start_time}_{end_time}.{file_format}"
    file_path = f"{ohlc_path}/{symbol}.{file_format}"

    if os.path.exists(file_path):
        logger.info(f"文件已存在: {file_path}")
        return feather.read_feather(file_path)

    try:
        for date in pd.date_range(start=start_time, end=end_time, freq="2D"):
            logger.info(date)
            df = read_feather_data(
                symbol=symbol,
                start_time=date,
                end_time=date + pd.DateOffset(days=1),
                base_dir="./okx_feather_data"
            )
            count += len(df)
            df.set_index('datetime', inplace=True)

            # 按1分钟周期重采样，生成K线
            ohlcv = df.resample(freq).agg(
                open=('price', 'first'),
                high=('price', 'max'),
                low=('price', 'min'),
                close=('price', 'last'),
                volume=('volume', 'sum')
            )
            ohlcvs = pd.concat([ohlcvs, ohlcv], ignore_index=False)

    except Exception as e:
        logger.error(f"读取失败: {str(e)}")

    if file_format == "feather":
        feather.write_feather(ohlcvs, file_path)
    else:
        ohlcvs.to_csv(file_path)
    
    print(f"保存到 {file_path} ")

    # ohlcvs = feather.read_feather(file_path)

    # ohlcvs.drop([ohlcvs.index[2],ohlcvs.index[1000]], inplace=True)
    missing_minutes = check_missing_minutes(ohlcvs)

    logger.info("缺失的分钟:", missing_minutes)

    return ohlcvs


def process_symbol(symbol, start_time, end_time, freq):
    try:
        return merge_ohlcv_data(symbol, start_time, end_time, freq)
    except Exception as e:
        logger.error(f"处理 {symbol} 时出错: {e}")
        return None


if __name__ == "__main__":
    freq = '1min'
    start_time = "2024-12-01"
    end_time = "2025-04-22"

    symbols = os.listdir("./okx_feather_data")

    # print(feather.read_feather(r"F:\quant\vnpy_demo\okx_feather_data\INCH-USDT\INCH-USDT-trades-2024-12-01.feather"))
    # for symbol in os.listdir("./okx_feather_data"):

    #     ohlc = merge_ohlcv_data(
    #         start_time=start_time,
    #         end_time=end_time,
    #         symbol=symbol,
    #         freq=freq,
    #         file_format="csv"
    #     )

        # 构造参数
    symbols = os.listdir("./okx_feather_data")

    print(symbols)
    # 使用 partial 固定除 symbol 之外的参数
    process_func = partial(
        merge_ohlcv_data,
        start_time=start_time,
        end_time=end_time,
        freq=freq,
        file_format="csv"
    )

    print("开始处理数据...")
    print(f"处理的交易对数量: {len(symbols)}")
    print("开始处理数据...")
    with ProcessPoolExecutor(max_workers=32) as executor:
        futures = [executor.submit(process_func, symbol) for symbol in symbols]
        for future in as_completed(futures):
            try:
                result = future.result()
                print("成功处理:", result)
            except Exception as e:
                print("发生异常:", e)
