import requests
from urllib.parse import urlparse

from bs4 import BeautifulSoup

import os
import sys

sys.path.append(os.getcwd())

from tradingagents.utils import common_utils

import logging
from tradingagents.log.log import TRADING_AGENTS_GRAPH
tag_logger = logging.getLogger(TRADING_AGENTS_GRAPH)


def baidu_search(keyword, max_count=10):
    tag_logger.info("baidu_search")

    search_result_list = get_search_result_list(keyword=keyword, max_count=max_count)
    if common_utils.is_empty(search_result_list):
        tag_logger.warning("search_result_list is none or empty")
        return ""
    
    search_results = []
    for item_title, item_link in search_result_list:
        item_content = get_baidu_search_item_content(item_url=item_link)
        search_results.append(item_content)

    return "\n\n".join(search_results)
    

def get_search_result_list(keyword, max_count=10):
    tag_logger.info("get_search_result_list")

    search_result_list = []
    if common_utils.is_empty(keyword):
        tag_logger.warning("keyword is none or empty")
        return search_result_list
    
    url = f"https://www.baidu.com/s?tn=baidu&wd={keyword}"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
        "accept-language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "referer": "https://www.baidu.com/s?tn=baidu&wd=Langgraph%E6%95%99%E7%A8%8B",
        "sec-ch-ua": '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "cookie": "BDUSS_BFESS=WQ4OVJKfjV0ZzNaMnZuMmVPaVJEYXhzV0M0eW5UaDBIczhTTXcwdmxOWWcwR0ZnRVFBQUFBJCQAAAAAAAAAAAEAAAC89mEFdGdsdHQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACBDOmAgQzpge; MCITY=-%3A; PSTM=1771245228; BIDUPSID=3573D258A964C2AA4699A120C91C4644; BAIDUID=7757787F70013BCC4A51DA20CD1E32D0:FG=1; BD_UPN=12314753; H_WISE_SIDS_BFESS=60278_63147_67862_68057_68002_68143_68149_68147_68153_68139_68165_68229_68263_68296_68342_68370_68456_68437_68511_68540_68547_68555_68506_68515_68588_68618_68622_68611_68602_68695_68661_68734_68724_68776_68793_68822_68882_68903_68913; BAIDUID_BFESS=7757787F70013BCC4A51DA20CD1E32D0:FG=1; ZFY=jk:AU6YUkpedXpMI4HSZdBOhmUbMNWRZWQRo9eVIgb9s:C; delPer=0; BD_CK_SAM=1; BD_HOME=1; baikeVisitId=b28630e5-8c8c-4d86-9060-9c5e9b57ff3b; __bid_n=19a8ae8106723044222b0a; COOKIE_SESSION=150788_0_8_8_6_6_1_0_8_6_1_0_150774_0_13_0_1775813505_0_1775813492%7C9%238538561_306_1758632159%7C9; BDRCVFR[I1GM4qgEDat]=mk3SLVN4HKm; H_PS_PSSID=60278_63147_67862_68165_68229_68263_68296_68370_68456_68437_68540_68547_68506_68515_68622_68611_68695_68734_68724_68776_68882_68903_68913_68831_68928_68978_69002_69012_69018_69024_69016_69056_68553_69074_69035_69085_69095_69087; BA_HECTOR=8h2l2ka42gak8g0kah80a40180210l1ktm8j627; H_WISE_SIDS=60278_63147_67862_68165_68229_68263_68296_68370_68456_68437_68540_68547_68506_68515_68622_68611_68695_68734_68724_68776_68882_68903_68913_68831_68928_68978_69002_69012_69018_69024_69016_69056_68553_69074_69035_69085_69095_69087; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; PSINO=6; H_PS_645EC=0954IDkQWSYx%2BvAgJmBzRVsINENJ8VFYQfSYf3BR4ZvOo8rDy51PsyNJJDY",
    }
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        tag_logger.warning(f"Request '{url}' failed.")
        return search_result_list
    
    soup = BeautifulSoup(markup=response.text, features="html.parser")
    data = soup.select("#content_left")
    if len(data) <= 0:
        print(f"Found no search result panel.")
        return search_result_list
    
    items = data[0].select(".result.c-container.xpath-log.new-pmd")
    if common_utils.is_empty(items):
        print(f"Found no search result.")
        return search_result_list
    
    for i in range(len(items)):
        item = items[i].select(".title-box_4YBsj")
        if common_utils.is_empty(item):
            continue

        item = item[0].find("a")
        if item is None:
            continue

        item_title = item.text
        item_link = item.get("href")

        search_result_list.append((item_title, item_link))

        if len(search_result_list) >= max_count:
            break

    return search_result_list


def get_baidu_search_item_content(item_url):
    tag_logger.info("get_baidu_search_item_content")
    if common_utils.is_empty(item_url):
        tag_logger.warning("item_url is none or empty")
        return ""
    
    tag_logger.debug(f"Requesting {item_url}")
    
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
        "accept-language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "referer": "https://www.baidu.com/s?tn=baidu&wd=Langgraph%E6%95%99%E7%A8%8B",
        "sec-ch-ua": '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "cookie": "BDUSS_BFESS=WQ4OVJKfjV0ZzNaMnZuMmVPaVJEYXhzV0M0eW5UaDBIczhTTXcwdmxOWWcwR0ZnRVFBQUFBJCQAAAAAAAAAAAEAAAC89mEFdGdsdHQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACBDOmAgQzpge; MCITY=-%3A; PSTM=1771245228; BIDUPSID=3573D258A964C2AA4699A120C91C4644; BAIDUID=7757787F70013BCC4A51DA20CD1E32D0:FG=1; BD_UPN=12314753; H_WISE_SIDS_BFESS=60278_63147_67862_68057_68002_68143_68149_68147_68153_68139_68165_68229_68263_68296_68342_68370_68456_68437_68511_68540_68547_68555_68506_68515_68588_68618_68622_68611_68602_68695_68661_68734_68724_68776_68793_68822_68882_68903_68913; BAIDUID_BFESS=7757787F70013BCC4A51DA20CD1E32D0:FG=1; ZFY=jk:AU6YUkpedXpMI4HSZdBOhmUbMNWRZWQRo9eVIgb9s:C; delPer=0; BD_CK_SAM=1; BD_HOME=1; baikeVisitId=b28630e5-8c8c-4d86-9060-9c5e9b57ff3b; __bid_n=19a8ae8106723044222b0a; COOKIE_SESSION=150788_0_8_8_6_6_1_0_8_6_1_0_150774_0_13_0_1775813505_0_1775813492%7C9%238538561_306_1758632159%7C9; BDRCVFR[I1GM4qgEDat]=mk3SLVN4HKm; H_PS_PSSID=60278_63147_67862_68165_68229_68263_68296_68370_68456_68437_68540_68547_68506_68515_68622_68611_68695_68734_68724_68776_68882_68903_68913_68831_68928_68978_69002_69012_69018_69024_69016_69056_68553_69074_69035_69085_69095_69087; BA_HECTOR=8h2l2ka42gak8g0kah80a40180210l1ktm8j627; H_WISE_SIDS=60278_63147_67862_68165_68229_68263_68296_68370_68456_68437_68540_68547_68506_68515_68622_68611_68695_68734_68724_68776_68882_68903_68913_68831_68928_68978_69002_69012_69018_69024_69016_69056_68553_69074_69035_69085_69095_69087; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; PSINO=6; H_PS_645EC=0954IDkQWSYx%2BvAgJmBzRVsINENJ8VFYQfSYf3BR4ZvOo8rDy51PsyNJJDY",
    }
    response = requests.get(item_url, headers=headers)

    if response.status_code not in [200, 403]:
        tag_logger.warning(f"Request '{item_url}' failed.")
        return ""


    if response.status_code == 403:
        if "zhihu" in response.url:
            headers = {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
                "accept-language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                "referer": "https://www.zhihu.com/",
                "sec-ch-ua": '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "Windows",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "x-api-version": "3.0.53",
                "x-requested-with": "fetch",
                "x-zse-93": "101_3_3.0",
                "x-zse-96": "2.0_xtXcTRRNeGFL9YVQbk/tlu2IuSq3gH1UzkVnhQ3Zm3yQ8wnXcgrj64fBTef20=Co",
                "x-zst-81": "3_2.0aR_sn77yn6O92wOB8hPZnQr0EMYxc4f18wNBUgpTQ6nxERFZG_Y0-4Lm-h3_tufIwJS8gcxTgJS_AuPZNcXCTwxI78YxEM20s4PGDwN8gGcYAupMWufIeQuK7AFpS6O1vukyQ_R0rRnsyukMGvxBEqeCiRnxEL2ZZrxmDucmqhPXnXFMTAoTF6RhRuLPF_OyMG3GqcU_e03xiGOK87Lfeg3KNuCYw9xO8qCGFcHGwJXL0DNYnrOBcveTvXwpsBg_pho9CbLmfqSYrrSGHh2GeCp9EDNsJRYLireYsCXCzGoKBUO05wVCpqUqLCt9gcNOFDxKTbcLcgw1wce0JwCmceHYCGO1bcx97vNGQi9_fGN9CqfzFBYZ9bH0rwemybSCFcnMiwLy2X2xsqL1c9eVbJNLZDXOhqcfuGNOWbCCkhcfeGFC1qFBi9SmDwFsH9gMWhH9IUcCfGNOocXC1HNKDhVqQwVOQTLCfXFC",
                "cookie": "_zap=295fad40-e153-4479-a7a9-9815dfd83543; _xsrf=luIwKMPptVY1BOWJyhzdfPBNoiQL4EzU; d_c0=NHLUTe-v5huPTviTJbPCGBHzFndu7IkNK4Q=|1772117626; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1774099413,1775297234; HMACCOUNT=C96D5CABDFC36329; z_c0=2|1:0|10:1775297335|4:z_c0|92:Mi4xQlFBSU9nQUFBQUEwY3RSTjc2X21HeVlBQUFCZ0FsVk5BZXFyYWdCTEVzelZ4VkEzVDAwRlY3UmZ1eVVrYXFHQVJ3|e7dca10755a6f30fb2934d6b7a30031e5b7372bc7dabddfdc94c4fe1b07f88d9; q_c1=61199845c13e498fbe30a44fc265ec8c|1776070179000|1776070179000; SESSIONID=euelHNjLzKEvgcuSrXdEgPfzStIH2ygh0s4B7Mvwv9d; JOID=UVAWBU8sqJfgyiscMQhkQ2XLFhQtQtb3joVufXhR6NmTr09iaQsITIzGKxI2-jDgCflz0Nsjq-QZntMErWhS-aY=; osd=UlgRA00voJDmyCgUNg5mQG3MEBYuStHxjIZmen5T69GUqU1hYQwOTo_OLBQ0-TjnD_tw2NwlqecRmdUGrmBV_6Q=; __zse_ck=005_sXv9xG7CloQY6Qy3TZCT6lWEQykbna39VthjKBC7jDpaPRGRDmPi1T2ja8Kz5L=iJdqcWijPOo8RouUAc4bTqgdFq2n0162=vKdjsypop5=Vpn5BZRlLRBxwxGl0aXIu-B/BWq2b/Mee4gCSd2QMMJGSX9a03e/7jCxuduEPkRZKrQkcUiDgnlnfTONmehZWYX2zDOt9NBHvRWj8jlepeYdVdEOMLrch+hgLaLkMr8hhzE+zDX05Xi6TT1NrmIXhsZ1ua2rdPmUQMEO4vJHvebXyrUgX5hl+8WU2nxijYgR0=; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1776070262; BEC=81a05b8536c1b72d656b636a600357ff",
            }
            response = requests.get(response.url, headers=headers)
            if response.status_code != 200:
                tag_logger.warning(f"Request '{response.url}' failed.")
                return ""
            text = response.text
        else:
            tag_logger.warning(f"Request '{response.url}' failed.")
            return ""
    else:
        text = response.text
        if common_utils.is_empty(response.content) and len(response.history) > 0 and len(response.url) > 0:
            response = requests.get(response.url)

            if response.status_code != 200:
                print(f"Request '{response.url}' failed.")
                return ""

            if response.apparent_encoding:
                text = response.content.decode(response.apparent_encoding)
    
    soup = BeautifulSoup(markup=text, features="html.parser")
    return soup.text


# https://www.baidu.com/s?tn=baidu&wd=python%E9%85%8D%E7%BD%AE


# http://www.baidu.com/link?url=pvEBHy9IsSMeKJnrCqR-VFEj4VBUo_KQaaS0pA8MJyv8k6LHlb5_ze0XpAFWnQSse7u0X1iQUpcyX3fJMX1fya


# url = f"http://www.baidu.com/link?url=pvEBHy9IsSMeKJnrCqR-VFEj4VBUo_KQaaS0pA8MJyv8k6LHlb5_ze0XpAFWnQSse7u0X1iQUpcyX3fJMX1fya"
# url = "https://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sz301368.phtml"
# url = 'https://blog.csdn.net/nvd11/article/details/156135443'


import numpy as np

# keywords = ["Langgraph教程", "123", "今天天气", "汇编语方", "放假安排", "英语", "股票"]
# keyword_index = np.random.choice(len(keywords))
# keywords[keyword_index]

search_results = baidu_search(keyword="Langgraph教程", max_count=10)
print(search_results)
