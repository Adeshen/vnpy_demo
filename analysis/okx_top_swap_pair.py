import ccxt
import json
import pandas as pd

# 初始化 OKX 交易所实例
api = ccxt.okx()
api.load_markets()

# 获取市场信息
markets = api.fetch_markets()
print("市场信息已保存到 markets.json")
print(f"市场标的数量: {len(markets)}")

# 筛选出不同类型的市场
spot_markets = [m for m in markets if m['type'] == 'spot']
margin_markets = [m for m in markets if m['type'] == 'margin']
swap_markets = [m for m in markets if m['type'] == 'swap' and m['quoteId'] == 'USDT']
future_markets = [m for m in markets if m['type'] == 'future']
option_markets = [m for m in markets if m['type'] == 'option']

# 将市场信息保存到文件
with open("markets.json", "w") as f:
    json.dump(markets, f, indent=4)

print(f"现货市场数量: {len(spot_markets)}")
print(f"保证金市场数量: {len(margin_markets)}")
print(f"永续合约市场数量: {len(swap_markets)}")
print(f"期货市场数量: {len(future_markets)}")
print(f"期权市场数量: {len(option_markets)}")

# 获取每个永续合约市场的持仓价值
for market in swap_markets:
    try:
        open_interest = api.fetchOpenInterest(symbol=market['symbol'])
        market['openInterestValue'] = open_interest["openInterestValue"]
    except Exception as e:
        print(f"获取 {market['symbol']} 持仓价值时出错: {e}")
        market['openInterestValue'] = 0

# 按持仓价值对永续合约市场排序
sorted_markets = sorted(swap_markets, key=lambda x: x['openInterestValue'] if 'openInterestValue' in x else 0, reverse=True)

# 将排序后的永续合约市场信息保存到文件
with open("swap_markets.json", "w") as f:
    json.dump(sorted_markets, f, indent=4)

# 取前 30 个交易对的基础币种和持仓价值
top_30_data = []
for market in sorted_markets[:30]:
    symbol_parts = market['id'].split('-')[0]
    top_30_data.append({
        '基础币种': symbol_parts,
        '持仓价值': market['openInterestValue']
    })

# 创建 DataFrame
spot_df = pd.DataFrame(spot_markets)
swap_df = pd.DataFrame(swap_markets)
future_df = pd.DataFrame(future_markets)
option_df = pd.DataFrame(option_markets)
top_30_df = pd.DataFrame(top_30_data)

# 创建 ExcelWriter 对象
with pd.ExcelWriter('okx_market_data.xlsx') as writer:
    spot_df.to_excel(writer, sheet_name='现货市场', index=False)
    swap_df.to_excel(writer, sheet_name='永续合约市场', index=False)
    future_df.to_excel(writer, sheet_name='期货市场', index=False)
    option_df.to_excel(writer, sheet_name='期权市场', index=False)
    top_30_df.to_excel(writer, sheet_name='前 30 永续合约', index=False)

print("数据已保存到 okx_market_data.xlsx 文件中。")
    