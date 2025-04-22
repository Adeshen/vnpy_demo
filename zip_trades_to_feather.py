import os
import zipfile
import pandas as pd
import re
import pyarrow.feather as feather  # 确保安装：pip install pyarrow

# 配置参数
zip_dir = "./okx_trade_data"       # ZIP文件目录
output_root = "./okx_feather_data" # Feather输出根目录
pattern = r"([A-Z]+-[A-Z]+(-SWAP)?)(?=-trades)"

# 创建输出目录
os.makedirs(output_root, exist_ok=True)

# 获取所有交易对目录
pair_dirs = [d for d in os.listdir(zip_dir) if os.path.isdir(os.path.join(zip_dir, d))]

print(pair_dirs)

for pair in pair_dirs:
    pair_dir = os.path.join(zip_dir, pair)
    output_dir = os.path.join(output_root, pair)
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取当前交易对的所有ZIP文件
    zip_files = [f for f in os.listdir(pair_dir) if f.endswith('.zip')]
    
    for zip_file in zip_files:
        zip_path = os.path.join(pair_dir, zip_file)
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as z:
                # 提取CSV文件名
                csv_file = z.namelist()[0]
                match = re.search(pattern, csv_file)
                if not match:
                    print(f"跳过异常文件: {zip_file}")
                    continue
                symbol = match.group(1)
                
                # 解压到临时路径
                temp_csv = os.path.join(pair_dir, csv_file)
                z.extract(csv_file, path=pair_dir)
                
                # 读取和处理数据
                df = pd.read_csv(temp_csv, encoding='latin1')
                df.columns = ['tradeid', 'side', 'volume', 'price', 'datetime']
                # df['side'] = df['side'] == 'sell'
                # df['symbol'] = symbol
                # df['exchange'] = "OKX"
                df['datetime'] = pd.to_datetime(df['datetime'])
                df = df[["tradeid",  "side", "datetime", "price", "volume"]]
                # print(df)

                # 转换为Feather格式
                date_str = re.search(r"(\d{4}-\d{2}-\d{2})", csv_file).group(1)
                feather_file = f"{symbol}-trades-{date_str}.feather"
                feather_path = os.path.join(output_dir, feather_file)
                
                # 保存Feather文件
                feather.write_feather(df, feather_path)
                print(f"转换成功: {feather_file} | 行数: {len(df)}")
                
                # 清理临时文件
                os.remove(temp_csv)
                
        except Exception as e:
            print(f"处理失败: {zip_file} | 错误: {str(e)}")
            continue

print("所有文件转换完成")