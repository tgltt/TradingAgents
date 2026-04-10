import requests
from urllib.parse import urlparse

from bs4 import BeautifulSoup

import os
import sys

sys.path.append(os.getcwd())

from tradingagents.utils import common_utils

# https://www.baidu.com/s?tn=baidu&wd=python%E9%85%8D%E7%BD%AE


# http://www.baidu.com/link?url=pvEBHy9IsSMeKJnrCqR-VFEj4VBUo_KQaaS0pA8MJyv8k6LHlb5_ze0XpAFWnQSse7u0X1iQUpcyX3fJMX1fya


url = f"http://www.baidu.com/link?url=pvEBHy9IsSMeKJnrCqR-VFEj4VBUo_KQaaS0pA8MJyv8k6LHlb5_ze0XpAFWnQSse7u0X1iQUpcyX3fJMX1fya"
# url = "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sz301368.phtml"

response = requests.get(url)

if response.status_code != 200:
    print(f"Request '{url}' failed.")

if common_utils.is_empty(response.content) and len(response.history) > 0 and len(response.url) > 0:
    response = requests.get(response.url)

    if response.status_code != 200:
        print(f"Request '{response.url}' failed.")

    if response.apparent_encoding:
        text = response.content.decode(response.apparent_encoding)
    else:
        text = response.text

    print(text)