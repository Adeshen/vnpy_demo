import os
import pandas as pd
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm

def remove_none_csv(file_path):
    """
    删除文件路径中的 None 字符串
    """
    df = pd.read_csv(file_path, encoding='utf-8')
    if len(df) == 0:
        print(f"文件 {file_path} 为空，删除")
        os.remove(file_path)
    return 

for file in os.listdir(r"F:\quant\vnpy_demo\1min_2024-12-01_2025-04-22"):
    # with ProcessPoolExecutor() as executor:
    #     futures = [executor.submit(remove_none_csv, os.path.join(r"F:\quant\vnpy_demo\1min_2024-12-01_2025-04-22", file)) for file in os.listdir(r"F:\quant\vnpy_demo\1min_2024-12-01_2025-04-22")]
    #     for future in tqdm(futures):
    #         future.result()
    remove_none_csv(os.path.join(r"F:\quant\vnpy_demo\1min_2024-12-01_2025-04-22", file))

