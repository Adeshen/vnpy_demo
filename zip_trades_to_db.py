import vnpy_evo.trader.setting as setting
import  vnpy_evo.trader.database  as db
import  vnpy_evo.trader.setting 
from vnpy_dolphindb import Database as Dolphindb
from vnpy_sqlite_hft import Database as Sqlitedb
import datetime


dolphin_db = Dolphindb(
    {    
    "database.name": "dolphindb",
    "database.database": "vnpy",
    "database.port": "8848",
    "database.host": "localhost",
    "database.user": "admin",
    "database.password": "123456",
    }
)

import os
import zipfile
import pandas as pd
import numpy as np
import re
# 定义存放 zip 文件的目录
zip_dir = "./history_data"  # 当前目录，可以根据需要修改
# 获取所有 zip 文件
zip_files = [f for f in os.listdir(zip_dir) if f.endswith('.zip')]
pattern = r"([A-Z]+-[A-Z]+(-SWAP)?)(?=-trades)"


# 遍历每个 zip 文件
for zip_file in zip_files:
    # 构建完整的文件路径
    zip_path = os.path.join(zip_dir, zip_file)
    
    # 解压 zip 文件
    with zipfile.ZipFile(zip_path, 'r') as z:
        # 假设每个 zip 文件中只有一个 CSV 文件
        csv_file = z.namelist()[0]  # 获取第一个文件的名称
        z.extract(csv_file, path=zip_dir)  # 解压到当前目录
        match = re.search(pattern, csv_file)
        if match:
            symbol = match.group(1)  # 提取匹配的内容
            print(f"文件路径: {csv_file} -> 提取的内容: {symbol}")
        else:
            raise ValueError(f"文件路径: {csv_file} -> 未找到匹配的symbol")
            # print(f"文件路径: {csv_file} -> 未找到匹配的内容")

        # 读取 CSV 文件到 DataFrame
        csv_path = os.path.join(zip_dir, csv_file)
        print(csv_path)
        df = pd.read_csv(csv_path, encoding='latin1')
        df.columns=['tradeid', 'side', 'volume' , 'price', 'datetime']
        df['side'] = df['side'] == 'sell'
        df['symbol'] = symbol
        df['exchange'] = "OKX"

        df = df[["symbol", "exchange", "tradeid", "side", "datetime", "price", "volume"]]
        print(f"Data from {zip_file}:")
        print(df.head())
        dolphin_db.save_trade_data_df(df)  
        # 打印 DataFrame 的前几行
        
        # 删除解压后的 CSV 文件（可选）
        os.remove(csv_path)

print("所有文件处理完成")