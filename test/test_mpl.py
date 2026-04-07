import mplfinance as mpf
import pandas as pd


# 示例数据，通常你会从数据源（如Yahoo Finance, Alpha Vantage等）获取这些数据
data = {
    'Date': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04'],
    'Open': [100, 101, 102, 103],
    'High': [105, 106, 107, 108],
    'Low': [95, 96, 97, 98],
    'Close': [102, 103, 104, 105],
    'Volume': [1000, 1500, 2000, 2500]
}

df = pd.DataFrame(data)
df['Date'] = pd.to_datetime(df['Date'])
df.set_index('Date', inplace=True)

# 绘制K线图
mpf.plot(df, type='candle', style='charles', title='Stock Candlestick Chart')
