import os
import pandas as pd
from pytdx.crawler.history_financial_crawler import HistoryFinancialListCrawler

crawler = HistoryFinancialListCrawler()
list_data = crawler.fetch_and_parse()
print(pd.DataFrame(data=list_data))


from pytdx.crawler.base_crawler import demo_reporthook
from pytdx.crawler.history_financial_crawler import HistoryFinancialCrawler

datacrawler = HistoryFinancialCrawler()
pd.set_option('display.max_columns', None)

cache_dir = os.path.join("output", "tdx")
os.makedirs(cache_dir, exist_ok=True)

result = datacrawler.fetch_and_parse(reporthook=demo_reporthook, 
                                     filename='gpcw20251231.zip', 
                                     path_to_download=os.path.join(cache_dir, "tmpfile.zip"))
# df = datacrawler.to_df(data=result)
# print(df)

# from pytdx.reader import HistoryFinancialReader

# print(HistoryFinancialReader().get_df(os.path.join(cache_dir, "tmpfile.zip")))
# print(HistoryFinancialReader().get_df('/tmp/gpcw20170930.dat'))

from pytdx.hq import TdxHq_API
api = TdxHq_API()
api.connect('101.33.225.16', 7709)

data1 = api.get_company_info_content(0, '000001', '000001.txt', 0, 100)
print(data1)

data2 = api.get_finance_info(0, '000001')
print(data2)
