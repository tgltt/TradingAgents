import requests
from urllib.parse import urlparse

from bs4 import BeautifulSoup

def get_company_news_list_sina(stock_code, max_count=10):
    """
    获取上市公司最新新闻，目前只读取新浪财经股票新闻第一页的新闻列表。
    Args:
        stock_code (str): 上市公司股票代码
        max_count (int, optional): 最多返回的新闻数. 默认10.

    Returns:
        list[str]: 上市公司新闻列表
    """
    url = f"https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/{stock_code}.phtml"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Request '{url}' failed.")
        return []

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
        return []
    
    news_list = []
    for item in items:
        news_title = item.text
        news_link = item.get("href")
        
        if not news_link.startswith(url_component.scheme):
            news_link = url_component.scheme + "://" + url_component.netloc + news_link
        
        news_list.append((news_title, news_link))
        
        if len(news_list) >= max_count:
            break

    return news_list

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
    
data = get_company_news_list_sina("sz301176", 3)
for title, url in data:
    content = get_company_new_detail_sina(url)
    print("-" * 20, "\n标题：", title, "\n链接：", url, "\n内容：", content, "\n", "-" * 20, "\n")
    
# content = get_company_new_detail_sina("https://finance.sina.com.cn/7x24/2026-03-24/doc-inhsamht7229360.shtml")
# print(content)