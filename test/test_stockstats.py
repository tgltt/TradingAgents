from typing import Annotated, Dict
import os
from datetime import datetime
import pandas as pd

from stockstats import wrap


df = pd.read_csv(r"data\market_data\price_data\600036.SH-tushare-data-20230101-20260408.csv")
df = df[["close", "low", "high"]]
df = wrap(df)

df["macd"]
df["kdjk_18"]
df["kdjd_18"]
df["bias_18"] = (df["close"] - df["close_18_sma"]) / df["close_18_sma"] * 100

print(df)