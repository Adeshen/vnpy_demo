import qlib
from qlib.config import C

from qlib.data import D
from qlib.contrib.eva.alpha import calc_all_ic, calc_ic
from multiprocessing import freeze_support
from qlib.data.ops import Delta

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
    start_time, end_time, freq = "2024-12-01", "2025-03-01", "1min"
    # label="$close"
    # features = D.features(list(s)[:2], [factor, label], start_time, end_time, freq=freq, disk_cache=True)
    features = D.features(s, [factor, label], start_time, end_time, freq=freq, disk_cache=True)
    print(features)