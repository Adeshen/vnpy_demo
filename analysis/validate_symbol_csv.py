import pandas as pd
import os
import time

def check_missing_minutes(ohlcv_df, freq='1min'):

    if ohlcv_df.empty:
        print("数据为空，无法检查缺失的分钟")
        return []

    # 1. 生成完整的分钟级时间范围
    full_time_range = pd.date_range(
        start=ohlcv_df.index.min(),
        end=ohlcv_df.index.max(),
        freq=freq  # 'T'表示分钟频率
    )
    
    # 2. 提取实际存在的分钟索引
    existing_minutes = ohlcv_df.index
    
    # 3. 计算缺失的分钟
    missing_minutes = full_time_range.difference(existing_minutes)
    
    return missing_minutes
# 帮我校验D:\quant\vnpy_demo\1min_2024-12-01_2025-04-22的csv文件是否有问题，
# 1. 可能有 空数据， 直接删除
# 2. 可能有 时间戳确实， open，high，low，close，沿用前一个时间戳的， volume 全为0

if __name__ == '__main__':


    symbols = os.listdir(r'D:/quant/vnpy_demo/1min_2024-12-01_2025-04-22')
    # 读取csv文件
    for symbol in symbols:
        symbol_csv = f'D:/quant/vnpy_demo/1min_2024-12-01_2025-04-22/{symbol}'
        df = pd.read_csv(symbol_csv)
        # 检查是否有空数据
        if len(df) == 0:
            print(f'{symbol} has empty data')
            # 删除空数据
            os.remove(symbol_csv)

        # 检查是否有时间戳缺失
        if len(df) > 0:
            # 检查是否有时间戳缺失
            df['datetime'] = pd.to_datetime(df['datetime'])
            df = df.set_index('datetime')
            missing_minutes = check_missing_minutes(df)
            print(missing_minutes)
            # 检查是否有时间戳缺失
            