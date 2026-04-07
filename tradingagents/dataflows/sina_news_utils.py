import requests
from urllib.parse import urlparse

from datetime import datetime, timedelta
from bs4 import BeautifulSoup

from tradingagents.utils import common_utils

def get_company_news_list_sina(stock_code, start_date, end_date, max_count=10):
    """
    获取上市公司最新新闻，目前只读取新浪财经股票新闻第一页的新闻列表。
    Args:
        stock_code (str): 上市公司股票代码
        start_date (str): 查询时间段的开始日期，格式为yyyymmdd
        end_date (str): 查询时间段的结束日期，格式为yyyymmdd
        max_count (int, optional): 最多返回的新闻数. 默认10.

    Returns:
        list[str]: 上市公司新闻列表
    """
    if common_utils.is_empty(start_date):
        start_date = datetime.now().strftime("%Y%m%d")
    
    if common_utils.is_empty(end_date) <= 0:
        # 如无指定结束日期，则默认为start_date的7天后
        end_date = datetime.strptime(start_date, "%Y%m%d") + timedelta(days=7)

    url = f"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/{stock_code}.phtml"

    news_list = []
    cur_page = 1
    while (True):
        cur_url = url + f"page={cur_page}"
        response = requests.get(cur_url)

        if response.status_code != 200:
            print(f"Request '{cur_url}' failed.")
            # 若当前请求失败，则返回已解析的文档列表内容
            return news_list

        if response.apparent_encoding:
            text = response.content.decode(response.apparent_encoding)
        else:
            text = response.text
            
        url_component = urlparse(url)

        soup = BeautifulSoup(markup=text, features="html.parser")
        data = soup.select(".datelist")
        if len(data) <= 0:
            print(f"Found no {stock_code} news.")
            return []
        
        items = data[0].find_all("a")
        if len(items) <= 0:
            print(f"Found no {stock_code} news.")
            # 若当前请求返回无内容，则返回已解析的文档列表内容
            return news_list       
        
        for item in items:
            news_date = item.get("")
            if common_utils.is_empty(news_date) or news_date < start_date or news_date > end_date:
                continue

            news_title = item.text
            news_link = item.get("href")
            
            if not news_link.startswith(url_component.scheme):
                news_link = url_component.scheme + "://" + url_component.netloc + news_link
            
            news_list.append((news_title, news_link))
            
            if len(news_list) >= max_count:
                # 已达最大新闻数，直接返回
                return news_list
            
        cur_page += 1


def get_company_new_detail_sina(new_url):
    """获取新闻详情，目前暂不支持读取图片内的文本内容。

    Args:
        new_url (str): 新闻详情链接

    Returns:
        str: 新闻详情内容
    """
    if new_url is None or len(new_url) <= 0:
        return ""
    
    response = requests.get(new_url)

    if response.status_code != 200:
        print(f"Request '{new_url}' failed.")
        return ""
    
    if response.apparent_encoding:
        text = response.content.decode(response.apparent_encoding)
    else:
        text = response.text

    
    soup = BeautifulSoup(markup=text, features="html.parser")
    new_content = soup.select(".article")
    if new_content is None or len(new_content) <= 0:
        return ""
    
    return new_content[0].get_text("\n").strip()
    

def get_company_news(stock_code, start_date, end_date, max_count=10):
    """
    获取上市公司最新新闻，目前只读取新浪财经股票新闻第一页的新闻列表。
    Args:
        stock_code (str): 上市公司股票代码
        start_date (str): 查询时间段的开始日期，格式为yyyymmdd
        end_date (str): 查询时间段的结束日期，格式为yyyymmdd
        max_count (int, optional): 最多返回的新闻数. 默认10.

    Returns:
        list[(str, str)]: 上市公司新闻列表及内容
    """
    print(f"get_company_news, stock_code={stock_code}, start_date={start_date}, end_date={end_date}, max_count={max_count}")

    news_list = get_company_news_list_sina(stock_code, start_date, end_date, max_count)
    if common_utils.is_empty(news_list):
        print("news_list is none or empty")
        return ""
    
    news_contents = []
    for new_tile, new_url in news_list:
        new_content = get_company_new_detail_sina(new_url)
        if common_utils.is_empty(new_content):
            print("new_content is none or empty, new_tile={new_tile}, new_url={new_url}")
            continue

        news_contents.append((new_tile, new_content))

    return news_contents

