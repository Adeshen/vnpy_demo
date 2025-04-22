import os
import requests
from datetime import date, timedelta
from requests.exceptions import RequestException

def download_trade_data(
    trade_pairs, 
    start_date, 
    end_date, 
    output_dir="./data", 
    max_retries=3
):
    """
    批量下载OKX交易对历史数据
    
    :param trade_pairs: 交易对列表（如 ["DOGE-USDT", "BTC-USDT"]）
    :param start_date: 开始日期（datetime.date对象）
    :param end_date: 结束日期（datetime.date对象）
    :param output_dir: 根存储目录（默认./data）
    :param max_retries: 下载失败最大重试次数（默认3次）
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # 创建根目录
    os.makedirs(output_dir, exist_ok=True)
    
    with requests.Session() as session:
        session.headers.update(headers)
        
        for pair in trade_pairs:
            pair_dir = os.path.join(output_dir, pair)
            os.makedirs(pair_dir, exist_ok=True)
            
            current_date = start_date
            while current_date <= end_date:
                # 生成文件信息
                date_str = current_date.strftime("%Y%m%d")
                file_date_str = current_date.strftime("%Y-%m-%d")
                url = f"https://www.okx.com/cdn/okex/traderecords/trades/daily/{date_str}/{pair}-trades-{file_date_str}.zip"
                filename = f"{pair}-trades-{file_date_str}.zip"
                file_path = os.path.join(pair_dir, filename)
                
                # 跳过已存在的有效文件
                if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                    print(f"⏩ 已存在: {filename}")
                    current_date += timedelta(days=1)
                    continue
                
                # 下载逻辑（带重试机制）
                retries = 0
                while retries <= max_retries:
                    try:
                        response = session.get(url, timeout=10)
                        response.raise_for_status()
                        
                        with open(file_path, 'wb') as f:
                            f.write(response.content)
                        print(f"✅ 成功: {pair} | {file_date_str}")
                        break
                    except RequestException as e:
                        retries += 1
                        if retries > max_retries:
                            print(f"❌ 失败: {pair} | {file_date_str} | 错误: {e}")
                        else:
                            print(f"🔄 重试({retries}/{max_retries}): {pair} | {file_date_str}")
                
                current_date += timedelta(days=1)

# 定义下载参数
# trade_pairs = ["BTC-USDT", "ETH-USDT"]
# OKX高流动性交易对列表（2024年更新）
top_50_pairs = [
    "BTC-USDT", "ETH-USDT", "XRP-USDT", "DOGE-USDT", "ADA-USDT",
    "SOL-USDT", "DOT-USDT", "AVAX-USDT", "LINK-USDT", "LTC-USDT",
    "BCH-USDT", "TRX-USDT", "UNI-USDT", "MATIC-USDT", "ETC-USDT",
    "EOS-USDT", "XLM-USDT", "ALGO-USDT", "FIL-USDT", "AAVE-USDT",
    "ATOM-USDT", "XTZ-USDT", "MANA-USDT", "SAND-USDT", "AXS-USDT",
    "DYDX-USDT", "GRT-USDT", "1INCH-USDT", "ENJ-USDT", "ZEC-USDT",
    "XMR-USDT", "DASH-USDT", "COMP-USDT", "YFI-USDT", "CRV-USDT",
    "SNX-USDT", "MKR-USDT", "FTT-USDT", "SRM-USDT", "RAY-USDT",
    "KNC-USDT", "BAL-USDT", "UMA-USDT", "BNT-USDT", "REN-USDT",
    "OXT-USDT", "NMR-USDT", "LRC-USDT", "ZRX-USDT", "SUSHI-USDT"
]
trade_pairs = top_50_pairs

start_date = date(2024, 12, 1)
end_date = date(2025, 4, 22)
output_dir = "./okx_trade_data"

# 开始下载
download_trade_data(
    trade_pairs=trade_pairs,
    start_date=start_date,
    end_date=end_date,
    output_dir=output_dir,
    max_retries=2
)