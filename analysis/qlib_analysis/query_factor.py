import qlib
from qlib.config import C

from qlib.data import D
from qlib.contrib.eva.alpha import calc_all_ic, calc_ic
from multiprocessing import freeze_support
from qlib.data.ops import Delta
import matplotlib.pyplot as plt

from statsmodels.tsa.stattools import adfuller, kpss

qlib.init(provider_uri=r"D:/quant/vnpy_demo/qlib_data", region="cn")
all_instrustments = D.instruments()
print(all_instrustments)
s = list(D.list_instruments(all_instrustments, freq="1min").keys())
print(s)
print(len(s))


if __name__ == "__main__":
    freeze_support()
    s = ['BTC-USDT', "ETH-USDT"]
    label="$close"
    factor = "EMA($close, 5)"
    return_factor = "Log($close)-Log(Ref($close, 1))"
    start_time, end_time, freq = "2024-12-01", "2025-03-01", "1min"
    # label="$close"
    # features = D.features(list(s)[:2], [factor, label], start_time, end_time, freq=freq, disk_cache=True)
    features = D.features(s, [factor, return_factor, label], start_time, end_time, freq=freq, disk_cache=True)
    print(features)
    features.to_csv("features.csv")

    log_returns = features[return_factor]

    plt.figure(figsize=(12, 6))
    plt.plot(log_returns.index, log_returns.values)
    plt.title('Log Returns Time Series')
    plt.xlabel('Time')
    plt.ylabel('Log Returns')
    plt.grid(True)
    plt.savefig('log_returns_plot.png')  # 保存图像
    plt.show()

    # ADF 检验
    adf_result = adfuller(log_returns)
    print('ADF Statistic:', adf_result[0])
    print('p-value:', adf_result[1])
    print('Critical Values:')
    for key, value in adf_result[4].items():
        print('\t%s: %.3f' % (key, value))


    label_f = features[label]
    # ADF 检验
    adf_result = adfuller(label_f)
    print('ADF Statistic:', adf_result[0])
    print('p-value:', adf_result[1])
    print('Critical Values:')
    for key, value in adf_result[4].items():
        print('\t%s: %.3f' % (key, value))