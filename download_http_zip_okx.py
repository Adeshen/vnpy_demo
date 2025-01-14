import subprocess
import datetime

# 定义基础URL和交易对
base_url = "https://www.okx.com/cdn/okex/traderecords/trades/daily"
trade_pair = "DOGE-USDT"

# 定义日期范围
start_date = datetime.date(2024, 12, 1)
end_date = datetime.date(2025, 1, 14)

# 遍历日期范围
current_date = start_date
while current_date <= end_date:
    # 格式化日期
    date_str = current_date.strftime("%Y%m%d")
    # 构建下载URL
    url = f"{base_url}/{date_str}/{trade_pair}-trades-{current_date.strftime('%Y-%m-%d')}.zip"
    # 使用wget下载文件
    subprocess.run(["wget", url])
    # 增加一天
    current_date += datetime.timedelta(days=1)

print("下载完成")