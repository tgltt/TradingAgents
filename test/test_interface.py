from tradingagents.dataflows import interface


# data = interface._download_tushare_stock_price_data(symbol="600036.SH", start_date="20260302", end_date="20260311", look_back_days=100, save_to_file=True)
# print(data)

# data = interface.get_stock_stats_indicators_window(symbol="600036.SH", indicator="macd", curr_date="20260311", look_back_days=20, online=True)
# print(data)

# data = interface.get_tushare_tech_data_offline(symbol="600036.SH", start_date="20260302", end_date="20260311")
# data = interface.get_tushare_tech_data_online(symbol="600036.SH", start_date="20260302", end_date="20260312")
# print(data)


data = interface.get_fundamentals_tushare(symbol="600036.SH", cur_date="20260312", look_back_years=2)
print(data)