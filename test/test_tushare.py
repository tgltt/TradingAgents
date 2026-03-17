from typing import Annotated, Dict
from datetime import datetime
import pandas as pd

import yfinance as yf

import sxsc_tushare as sx
sx.set_token("baab01b29616c4c2a7bc206eac9ed3c34c944aba977c438323157edb")
api = sx.get_api(env="prd")

def get_tushare_tech_data_online(
    symbol: Annotated[str, "stock symbol of the company"],
    start_date: Annotated[str, "Start date in yyyymmdd format"],
    end_date: Annotated[str, "End date in yyyymmdd format"],
):
    # Fetch historical data for the specified date range
    data = api.daily(ts_code="600036.SH", start_date=start_date, end_date=end_date)

    # Check if data is empty
    if len(data) <= 0:
        return (
            f"No data found for symbol '{symbol}' between {start_date} and {end_date}"
        )

    selected_columns = ["open", "high", "low", "close", "vol", "amount"]
    data = data[selected_columns]
    # Convert DataFrame to CSV string
    csv_string = data.to_csv(index=False)
    
    # Add header information
    header = f"# Stock data for {symbol.upper()} from {start_date} to {end_date}\n"
    header += f"# Total records: {len(data)}\n"
    header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    return header + csv_string

df = api.cb_daily(ts_code="110086.SH", start_date="20240319", end_date="20240321")
print(df)

# stock_info = api.stock_company(ts_code="600036.SH")
# print(stock_info)

# business_express = api.express(ts_code="600036.SH",
#                                start_date="20250101", 
#                                end_date="20251231")
# print(business_express)

# data = get_tushare_tech_data_online(symbol="600036.SH", start_date="20180701", end_date="20180718")
# print(data)

# data = yf.download(
#                     "600036.SH",
#                     start="20180201",
#                     end="20180301",
#                     multi_level_index=False,
#                     progress=False,
#                     auto_adjust=True,
#                 )

# print(data)


# business_express = api.fina_indicator(ts_code="600036.SH", start_date="20240101", end_date="20250523")
# business_express = business_express[["eps", "bps", "retainedps", "cfps", "profit_dedt", "gross_margin", "roe", "debt_to_assets", "or_yoy", "op_yoy", "fixed_assets"]]
# print(business_express)

# dt = pd.to_datetime("20250209")
# print(dt - pd.DateOffset(years=1))

# , fields=["introduction", "main_business", "business_scope"]
# data = api.stock_basic(ts_code="600036.SH", fields=["name", "industry"])
# print(data)

# data = api.stock_company(ts_code="600036.SH", fields=["reg_capital"])
# print(data)

from tradingagents.dataflows.interface import get_fundamentals_tushare

data = get_fundamentals_tushare(symbol="600036.SH", cur_date="20260317", look_back_years=3)
print(data)