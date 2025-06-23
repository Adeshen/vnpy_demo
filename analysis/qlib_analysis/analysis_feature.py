from pyexpat import features
import pandas as pd
import matplotlib.pyplot as plt

from statsmodels.tsa.stattools import adfuller, kpss
from arch import arch_model
import numpy as np
from statsmodels.graphics.tsaplots import plot_pacf, plot_acf
from statsmodels.tsa.stattools import pacf
from statsmodels.tsa.ar_model import AutoReg


if __name__ == '__main__':
    label="$close"
    factor = "EMA($close, 5)"
    return_factor = "Log($close)-Log(Ref($close, 1))"


    features = pd.read_csv('features.csv')
    features['datetime'] = pd.to_datetime(features['datetime'])
    btc_features = features[features['instrument'] == 'BTC-USDT']
    eth_features = features[features['instrument'] == 'ETH-USDT']

    log_returns = btc_features[return_factor]

    plt.figure(figsize=(12, 6))

    plt.plot(btc_features['datetime'], log_returns.values)
    plt.title('BTC Log Returns Time Series')
    plt.xlabel('Time')
    plt.ylabel('Log Returns')
    plt.grid(True)
    plt.savefig('log_returns_plot.png')  # 保存图像
    # plt.show()

    model = arch_model(log_returns, vol='GARCH', p=1, q=1, dist='Normal')
    results = model.fit(disp='off')  # disp='off' 关闭迭代输出

    # 输出模型参数估计结果
    print(results.summary())
    # forecast = results.forecast(horizon=5)
    # volatility_forecast = np.sqrt(forecast.variance.iloc[-1].values)
    # print("未来 5 期波动率预测:")
    # for i, vol in enumerate(volatility_forecast, 1):
    #     print(f"第 {i} 期: {vol:.6f}")


    # 绘制 PACF 图
    plt.figure(figsize=(12, 6))
    pacf_values = pacf(log_returns, nlags=40)
    print("PACF Values:")
    for lag, value in enumerate(pacf_values):
        print(f"Lag {lag}: {value:.4f}")
    plt.xlabel('Lag')
    plt.ylabel('Partial Autocorrelation')
    plt.savefig('Partial_Autocorrelation.pdf', format='pdf')
    
    plt.grid(True)
    # plt.show()
        

    # 2. 拟合 AR(1) 模型
    ar_model = AutoReg(log_returns, lags=5)
    results = ar_model.fit()

    # 3. 输出模型结果
    print(results.summary())


    # # ADF 检验
    # adf_result = adfuller(log_returns)
    # print('ADF Statistic:', adf_result[0])
    # print('p-value:', adf_result[1])
    # print('Critical Values:')
    # for key, value in adf_result[4].items():
    #     print('\t%s: %.3f' % (key, value))

    # label_f = features[label]
    # # ADF 检验
    # adf_result = adfuller(label_f)
    # print('ADF Statistic:', adf_result[0])
    # print('p-value:', adf_result[1])
    # print('Critical Values:')
    # for key, value in adf_result[4].items():
    #     print('\t%s: %.3f' % (key, value))