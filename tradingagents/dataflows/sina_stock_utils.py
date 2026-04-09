import requests
from urllib.parse import urlparse

from datetime import datetime, timedelta
from bs4 import BeautifulSoup

from tradingagents.utils import common_utils

INFO_TYPE_NEWS = 0
INFO_TYPE_BULLETINS = 1

def _get_company_news_or_bulletin_list_sina(url, stock_code, start_date, end_date, max_count):
    """
    获取上市公司最新新闻，目前只读取新浪财经股票新闻第一页的新闻列表。
    Args:
        url (str): 待获取信息所在的URL
        stock_code (str): 上市公司股票代码
        start_date (str): 查询时间段的开始日期，格式为yyyymmdd
        end_date (str): 查询时间段的结束日期，格式为yyyymmdd
        max_count (int, optional): 最多返回的新闻数. 默认10.

    Returns:
        list[(str, str, str)]: 上市公司新闻列表
    """
    if common_utils.is_empty(start_date):
        start_date = datetime.now().strftime("%Y%m%d")
    
    if common_utils.is_empty(end_date):
        # 如无指定结束日期，则默认为start_date的60天后
        end_date = datetime.strptime(start_date, "%Y%m%d") + timedelta(days=60)
        end_date = datetime.strftime(end_date, "%Y%m%d")
    
    start_date_value = datetime.strptime(start_date, "%Y%m%d")
    end_date_value = datetime.strptime(end_date, "%Y%m%d")

    news_list = []

    news_window_size = (end_date_value - start_date_value).days
    if news_window_size <= 0:
        return news_list

    cur_page = 1
    while (True):
        cur_url = url + f"?page={cur_page}"
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
        
        items = data[0].find_all("ul")
        if len(items) <= 0:
            print(f"Found no {stock_code} news.")
            # 若当前请求返回无内容，则返回已解析的文档列表内容
            return news_list

        item_contents = [str(item_content) for item_content in items[0].contents]
        items = ("".join(item_contents)).split("<br/>")
        for item in items:
            new_date_end_index = item.find("<a ")
            if new_date_end_index < 0:
                continue

            news_date = item[:new_date_end_index].strip().replace("-", "")[:8]
            if common_utils.is_empty(news_date):
                continue

            if news_date > end_date:
                continue

            if news_date < start_date:
                # 当前新闻已超出待提取新闻列表的时间窗口下限
                return news_list

            item_soup = BeautifulSoup(markup=item, features="html.parser")
            news = item_soup.find_all("a")
            if len(news) <= 0:
                continue

            news_title = news[0].text
            news_link = news[0].get("href")
            
            if not news_link.startswith(url_component.scheme):
                news_link = url_component.scheme + "://" + url_component.netloc + news_link
            
            news_list.append((news_title, news_date, news_link))
            
            if len(news_list) >= max_count:
                # 已达最大新闻数，直接返回
                return news_list
            
        cur_page += 1


def get_company_news_list_sina(stock_code, start_date, end_date, max_count=10):
    """
    获取上市公司指定时间段的新闻。
    Args:
        stock_code (str): 上市公司股票代码
        start_date (str): 查询时间段的开始日期，格式为yyyymmdd
        end_date (str): 查询时间段的结束日期，格式为yyyymmdd
        max_count (int, optional): 最多返回的新闻数. 默认10.

    Returns:
        list[(str, str, str)]: 上市公司新闻列表
    """
    url = f"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/{stock_code.lower()}.phtml"
    return _get_company_news_or_bulletin_list_sina(url=url, 
                                                   stock_code=stock_code,
                                                   start_date=start_date,
                                                   end_date=end_date,
                                                   max_count=max_count)


def get_company_bulletins_list_sina(stock_code, start_date, end_date, max_count=10):
    """
    获取上市公司指定时间段的公告。
    Args:
        stock_code (str): 上市公司股票代码
        start_date (str): 查询时间段的开始日期，格式为yyyymmdd
        end_date (str): 查询时间段的结束日期，格式为yyyymmdd
        max_count (int, optional): 最多返回的新闻数. 默认10.

    Returns:
        list[(str, str, str)]: 上市公司公告列表
    """
    url = f"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllBulletin/stockid/{stock_code.lower()}.phtml"
    return _get_company_news_or_bulletin_list_sina(url=url, 
                                                   stock_code=stock_code,
                                                   start_date=start_date,
                                                   end_date=end_date,
                                                   max_count=max_count)


def get_company_new_or_bulletin_detail_sina(url):
    """获取新闻或公告详情，目前暂不支持读取图片内的文本内容。

    Args:
        url (str): 新闻或公告详情链接

    Returns:
        str: 新闻详情内容
    """
    if url is None or len(url) <= 0:
        return ""
    
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Request '{url}' failed.")
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
    

def _get_company_news_or_bulletins(stock_code, start_date, end_date=None, max_count=10, info_type=INFO_TYPE_NEWS):
    """
    获取上市公司最新新闻，目前只读取新浪财经股票新闻第一页的新闻列表。
    Args:
        stock_code (str): 上市公司股票代码
        start_date (str): 查询时间段的开始日期，格式为yyyymmdd
        end_date (str): 查询时间段的结束日期，格式为yyyymmdd
        max_count (int, optional): 最多返回的新闻数. 默认10
        info_type (int, optional): 查询的资讯类型：0 - 新闻, 1 - 公告

    Returns:
        list[(str, str, str)]: 上市公司新闻列表及内容
    """
    print(f"get_company_news, stock_code={stock_code}, start_date={start_date}, end_date={end_date}, max_count={max_count}")

    if info_type == INFO_TYPE_NEWS:
        info_list = get_company_news_list_sina(stock_code, start_date, end_date, max_count)
    else:
        info_list = get_company_bulletins_list_sina(stock_code, start_date, end_date, max_count)

    if common_utils.is_empty(info_list):
        print(f"info_list is none or empty, info_type={info_type}")
        return ""
    
    info_contents = []
    for info_title, info_date, info_url in info_list:
        info_content = get_company_new_or_bulletin_detail_sina(info_url)
        if common_utils.is_empty(info_content):
            print("info_content is none or empty, info_title={info_title}, info_url={info_url}")
            continue

        info_contents.append({"info_title": info_title, "info_date": info_date, "info_content": info_content})

    return info_contents


def get_company_news(stock_code, start_date, end_date=None, max_count=10):
    """
    获取上市公司指定时间段的新闻。
    Args:
        stock_code (str): 上市公司股票代码
        start_date (str): 查询时间段的开始日期，格式为yyyymmdd
        end_date (str): 查询时间段的结束日期，格式为yyyymmdd
        max_count (int, optional): 最多返回的新闻数. 默认10

    Returns:
        list[(str, str, str)]: 上市公司新闻列表及内容
    """
    return _get_company_news_or_bulletins(stock_code=stock_code,
                                          start_date=start_date,
                                          end_date=end_date,
                                          max_count=max_count,
                                          info_type=INFO_TYPE_NEWS)


def get_company_bulletins(stock_code, start_date, end_date=None, max_count=10):
    """
    获取上市公司指定时间段的公告。
    Args:
        stock_code (str): 上市公司股票代码
        start_date (str): 查询时间段的开始日期，格式为yyyymmdd
        end_date (str): 查询时间段的结束日期，格式为yyyymmdd
        max_count (int, optional): 最多返回的新闻数. 默认10

    Returns:
        list[(str, str, str)]: 上市公司新闻列表及内容
    """
    return _get_company_news_or_bulletins(stock_code=stock_code,
                                          start_date=start_date,
                                          end_date=end_date,
                                          max_count=max_count,
                                          info_type=INFO_TYPE_BULLETINS)


if __name__ == "__main__":
    # news_list = get_company_news(stock_code="SZ002403", start_date="20260301", end_date="20260407", max_count=1)
    # print(news_list)
    pass