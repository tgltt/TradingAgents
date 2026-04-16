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

DEFAULT_MAX_COUNT = 10


def _get_baidu_header():
    header = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
        "accept": "*/*",
        "accept-encoding": "gzip",
        "accept-language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "connection": "keep-alive",
        "host": "www.baidu.com",
        "is_referer": "https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&tn=baidu&wd=Langgraph%E6%95%99%E7%A8%8B&oq=Langgraph%E6%95%99%E7%A8%8B&rsv_pq=b25ee9530012de88&rsv_t=6273NxaL7z54SECd6b5M5g%2Ffwc26WJxzmILiQHmxaindwIRMhsJ71rt7RvI&rqlang=cn",
        "referer": "https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&tn=baidu&wd=Langgraph%E6%95%99%E7%A8%8B&oq=Langgraph%25E6%2595%2599%25E7%25A8%258B&rsv_pq=b25ee9530012de88&rsv_t=0954IDkQWSYx%2BvAgJmBzRVsINENJ8VFYQfSYf3BR4ZvOo8rDy51PsyNJJDY&rqlang=cn&rsv_enter=1&rsv_dl=tb_enter&rsv_sug3=3&rsv_sug1=1&rsv_sug7=100&rsv_btype=t&rsv_sug=1",
        "sec-ch-ua": '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "cookie": "BDUSS_BFESS=WQ4OVJKfjV0ZzNaMnZuMmVPaVJEYXhzV0M0eW5UaDBIczhTTXcwdmxOWWcwR0ZnRVFBQUFBJCQAAAAAAAAAAAEAAAC89mEFdGdsdHQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACBDOmAgQzpge; MCITY=-%3A; PSTM=1771245228; BIDUPSID=3573D258A964C2AA4699A120C91C4644; BAIDUID=7757787F70013BCC4A51DA20CD1E32D0:FG=1; BD_UPN=12314753; H_WISE_SIDS_BFESS=60278_63147_67862_68057_68002_68143_68149_68147_68153_68139_68165_68229_68263_68296_68342_68370_68456_68437_68511_68540_68547_68555_68506_68515_68588_68618_68622_68611_68602_68695_68661_68734_68724_68776_68793_68822_68882_68903_68913; BAIDUID_BFESS=7757787F70013BCC4A51DA20CD1E32D0:FG=1; ZFY=jk:AU6YUkpedXpMI4HSZdBOhmUbMNWRZWQRo9eVIgb9s:C; delPer=0; BD_CK_SAM=1; BD_HOME=1; baikeVisitId=b28630e5-8c8c-4d86-9060-9c5e9b57ff3b; __bid_n=19a8ae8106723044222b0a; COOKIE_SESSION=150788_0_8_8_6_6_1_0_8_6_1_0_150774_0_13_0_1775813505_0_1775813492%7C9%238538561_306_1758632159%7C9; BDRCVFR[I1GM4qgEDat]=mk3SLVN4HKm; H_PS_PSSID=60278_63147_67862_68165_68229_68263_68296_68370_68456_68437_68540_68547_68506_68515_68622_68611_68695_68734_68724_68776_68882_68903_68913_68831_68928_68978_69002_69012_69018_69024_69016_69056_68553_69074_69035_69085_69095_69087; BA_HECTOR=8h2l2ka42gak8g0kah80a40180210l1ktm8j627; H_WISE_SIDS=60278_63147_67862_68165_68229_68263_68296_68370_68456_68437_68540_68547_68506_68515_68622_68611_68695_68734_68724_68776_68882_68903_68913_68831_68928_68978_69002_69012_69018_69024_69016_69056_68553_69074_69035_69085_69095_69087; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; PSINO=6; H_PS_645EC=0954IDkQWSYx%2BvAgJmBzRVsINENJ8VFYQfSYf3BR4ZvOo8rDy51PsyNJJDY",
    }
    return header


def _get_zhihu_header():
    header = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
        "accept": "*/*",
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
    return header


def _get_csdn_header():
    header = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
        "accept": "*/*",
        "accept-language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "referer": "https://blog.csdn.net/",
        "origin": "https://blog.csdn.net",
        "sec-ch-ua": '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "cookie": "fid=20_60982597682-1766829231712-530005; uuid_tt_dd=10_20286915190-1774081716997-508667; c_segment=11; dc_sid=8c287a0f06c1a87ca8d5fc2d38236b42; Hm_lvt_6bcd52f51e9b3dce32bec4a3997715ac=1774081720,1775311566; Hm_ct_6bcd52f51e9b3dce32bec4a3997715ac=6525*1*10_20286915190-1774081716997-508667; hide_login=1; c_ref=https%3A//www.baidu.com/link; c_first_ref=www.baidu.com; SESSION=b8e610ca-65e2-41c9-b480-63be80856d9b; dc_session_id=10_1776149049899.216498; c_pref=https%3A//www.baidu.com/link; c_first_page=https%3A//blog.csdn.net/weixin_43820813/article/details/131801451; loginbox_strategy=%7B%22blog-threeH-dialog-exp11tipShowTimes%22%3A1%2C%22blog-threeH-dialog-exp11%22%3A%22%22%7D; creative_btn_mp=3; popPageViewTimes=3; Hm_lpvt_6bcd52f51e9b3dce32bec4a3997715ac=1776149056; _clck=8br3q%5E2%5Eg57%5E0%5E1556; __gads=ID=d0ac5dc35bfab1f4:T=1774081720:RT=1776149055:S=ALNI_MZ0XnlwP0dohfCXYbWGNA3xbED3rg; __gpi=UID=0000119103e4b94b:T=1757174872:RT=1776149055:S=ALNI_MaC-3sBl5FkeUydz_BI52vKTtmGVw; __eoi=ID=d599fa963cef7b91:T=1774081720:RT=1776149055:S=AA-Afjbbo5AkcXhSrOvb0PkO_imT; _clsk=s70by%5E1776149057991%5E1%5E0%5Ez.clarity.ms%2Fcollect; c_dsid=11_1776149085498.752790; c_page_id=default; dc_tos=tdh1el; log_Id_pv=2; log_Id_view=34",
    }
    return header


def _get_cnblog_header():
    header = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
        "accept": "text/plain, */*; q=0.01",
        "accept-language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "referer": "https://www.cnblogs.com/",
        "origin": "https://www.cnblogs.com",
        "priority": "u=1, i",
        "sec-ch-ua": '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "cookie": "_ga=GA1.1.2070797587.1606908271; .AspNetCore.Antiforgery.b8-pDmTq1XM=CfDJ8E2WNf1AXE5GolAm9rsxlHCVPbW2EB4hAOCoVWRBdw1ydJRI2Lz-w9LBoiaPgvSvLBGaxk5llRvg6_O-eliFvRnROlygk2sNrAusMoOkxQtgbsJE5Qt0hDHZbymSNa3Opb_YWc0dWC8DlmmnwGyoelo; Hm_lvt_866c9be12d4a814454792b1fd0fed295=1774101604,1775296525; HMACCOUNT=C96D5CABDFC36329; _c_WBKFRo=Uyq8P2eX5bw2XqLRZY5aPSo1H8ls7Bt8uL19YrLC; _nb_ioWEgULi=; .Cnblogs.AspNetCore.Cookies=CfDJ8E2WNf1AXE5GolAm9rsxlHB7UHMWpzJUY6SEjMCTmX-ksL0Dgsm5KDUX_qfJOozneUto_hEysc6wgcIlCTows_xSYXTvS8wLWx4UHX2nhn0DMGKOyDVzMS2NyP4ka4yf9PrYBWLVrYfkkqzme2urBydKJRWcZWi113w5IcXbswQuA0y3NUNTcNder_fDJmt41W7AHRQc3NA8SMNtNa5LuDfqJmi3v0bwIYITDK1xoR7AeTEvEmAcUhNikjgA2KGwri1sVl5x4f7W2Y7-ZnyBuMJhjMeBZjYZlqb8OtbLN63XaTGNUSdO825mzA3KVB6vfTw8p8elhcQyBI7mdzhPg2J47EypIALZpo9soa9zcIQozN8gZFFbhRuEat3-kLBLGWukSj_TcNoseI_lNg62Bc0flcgT9guVV3dJMevvbK42rH3hNP4FJmqP-pEx64exK5Uwuf8DDd0xT0Kcsqij0Wbs0-s8o8sPy8XLgRmNSRBVixPuaTNYhwQngmICNA9rQKtFDerNpaJQd6pneUHXgukPRLTynhNqT-sw9UBUEd4OzPidj7E-E6iMgTSdBUJoYXev5-MPTRcaUewtD11Y6TQ; .CNBlogsCookie=33A3EC19A9E725D3EDB88B56333EC4AE53294CFDBED018F623E66C6C496830CCF1653BB1821EE708B141E9BE1533A63649D403B959E362DB411681E284A4B9BAF7576478ADEE2E449136DBA9CA9FE7746CD1CB98; _ga_3Q0DVSGN10=GS2.1.s1775296544$o3$g1$t1775296564$j40$l0$h0; theme=light; __tins__21054727=%7B%22sid%22%3A%201775806965122%2C%20%22vd%22%3A%201%2C%20%22expires%22%3A%201775808765122%7D; __51cke__=; __51laig__=1; Hm_lpvt_866c9be12d4a814454792b1fd0fed295=1776150150; _ga_M95P3TTWJZ=GS2.1.s1776150149$o97$g0$t1776150155$j54$l0$h0",
    }
    return header


def _get_sohu_header():
    header = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
        "accept": "text/plain, */*; q=0.01",
        "accept-language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "referer": "https://www.sohu.com/",
        "origin": "https://www.sohu.com",
        "priority": "i",
        "sec-ch-ua": '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "cookie": "SUV=201202170612HX6K; gidinf=x099980109ee1a7b2d1d250220004d57cbd1106e66c5; t=1776150172515; cityIpLocation=112.97.65.14; IPLOC=CN4419; reqtype=pc; _dfp=XD4f7py2zm62ChfYI5ZJ1TDeVkixt82RZgEZz91b9D8=; clt=1776150173; cld=20260414150253; hideAddDesktop=true",
    }
    return header


def _get_sina_header():
    header = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
        "accept": "text/plain, */*; q=0.01",
        "accept-language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "referer": "https://www.sina.com.cn/",
        "origin": "https://www.sina.com.cn",
        "priority": "i",
        "sec-ch-ua": '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "cookie": "BDUSS_BFESS=WQ4OVJKfjV0ZzNaMnZuMmVPaVJEYXhzV0M0eW5UaDBIczhTTXcwdmxOWWcwR0ZnRVFBQUFBJCQAAAAAAAAAAAEAAAC89mEFdGdsdHQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACBDOmAgQzpge; H_WISE_SIDS_BFESS=60278_63147_67862_68057_68002_68143_68149_68147_68153_68139_68165_68229_68263_68296_68342_68370_68456_68437_68511_68540_68547_68555_68506_68515_68588_68618_68622_68611_68602_68695_68661_68734_68724_68776_68793_68822_68882_68903_68913; BAIDUID_BFESS=7757787F70013BCC4A51DA20CD1E32D0:FG=1; ZFY=jk:AU6YUkpedXpMI4HSZdBOhmUbMNWRZWQRo9eVIgb9s:C",
    }
    return header


def _get_eastmoney_header():
    header = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
        "accept": "text/plain, */*; q=0.01",
        "accept-language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "referer": "https://www.eastmoney.com/",
        "origin": "https://www.eastmoney.com",
        "priority": "i",
        "sec-ch-ua": '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "cookie": "qgqp_b_id=be99d7e33ce0dbbf01b6aade325ea316; st_nvi=6Q6Ty_LWRZuCSBdfrAniRb53c; nid18=038d6354e2e2fbddd04f1aae63abaad3; nid18_create_time=1775296983995; gviem=sWUqKCoSfSjLq_UABKIhVd879; gviem_create_time=1775296983996; st_si=30755909565651; st_pvi=54554663332121; st_sp=2026-04-04%2018%3A03%3A02; st_inirUrl=https%3A%2F%2Fwww.baidu.com%2Flink; st_sn=1; st_psi=20260414150419713-111000300841-5214059233; st_asi=delete; fullscreengg=1; fullscreengg2=1",
    }
    return header


def _get_51cto_header():
    header = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
        "accept": "text/plain, */*; q=0.01",
        "accept-language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "referer": "https://www.51cto.com/",
        "origin": "https://www.51cto.com",
        "priority": "i",
        "sec-ch-ua": '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "cookie": "sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2218391b88f448c-056c7e66001c44-26021c51-1382400-18391b88f4532c%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E8%87%AA%E7%84%B6%E6%90%9C%E7%B4%A2%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fwww.baidu.com%2Flink%22%7D%2C%22%24device_id%22%3A%2218391b88f448c-056c7e66001c44-26021c51-1382400-18391b88f4532c%22%7D; www51cto=507FD8EEB4DF1A6E463E465B7540542DxIvD; Hm_lvt_110fc9b2e1cae4d110b7959ee4f27e3b=1776151995; Hm_lpvt_110fc9b2e1cae4d110b7959ee4f27e3b=1776151995; HMACCOUNT=C96D5CABDFC36329",
    }
    return header


def _get_other_website_header(url):
    url_component = urlparse(url)
    url_host = url_component.scheme + "://" + url_component.netloc

    header = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
        "accept": "*/*",
        "accept-language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "referer": url_host,
        "origin": url_host,
        "priority": "i",
        "sec-ch-ua": '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
    }
    return header

def get_response_text(response):
    return response.content.decode(response.apparent_encoding) if response.apparent_encoding else response.text
    
def has_redirect(response):
    return common_utils.is_empty(response.content) and len(response.history) > 0 and len(response.url) > 0


def baidu_search(keyword, max_count=DEFAULT_MAX_COUNT):
    tag_logger.info("baidu_search")
    if common_utils.is_empty(keyword):
        return ""

    if max_count <= 0:
        max_count = DEFAULT_MAX_COUNT

    search_result_list = []
    try:
        search_result_list = get_search_result_list(keyword=keyword, max_count=max_count)
    except Exception as ex:
        tag_logger.error(f"Get query: {keyword} result failed, reason: {ex}")

    if common_utils.is_empty(search_result_list):
        tag_logger.warning("search_result_list is none or empty")
        return ""
    
    search_results = []
    for item_title, item_link in search_result_list:
        try:
            item_content = get_baidu_search_item_content(item_url=item_link)
            search_results.append(item_title + "\n" + item_content)
        except Exception as ex:
            tag_logger.error(f"Get {item_title}  {item_link} failed, reason: {ex}")

    return "\n\n".join(search_results)
    

def get_search_result_list(keyword, max_count=DEFAULT_MAX_COUNT):
    tag_logger.info("get_search_result_list")

    search_result_list = []
    if common_utils.is_empty(keyword):
        tag_logger.warning("keyword is none or empty")
        return search_result_list
    
    url = f"https://www.baidu.com/s?ie=utf-8&bsst=1&rsv_dl=news_t_sk&tn=news&cl=2&medium=0&rtt=1&wd={keyword}"
    headers = _get_baidu_header()
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        tag_logger.warning(f"Request '{url}' failed.")
        return search_result_list
    
    data = get_response_text(response)
        

    soup = BeautifulSoup(markup=data, features="html.parser")
    data = soup.select("#content_left")
    if len(data) <= 0:
        print(f"Found no search result panel.")
        return search_result_list
    
    items = data[0].select(".result-op.c-container.xpath-log.new-pmd")
    if common_utils.is_empty(items):
        print(f"Found no search result.")
        return search_result_list
    
    for i in range(len(items)):
        item = items[i].select(".news-title_1YtI1")
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
    def retry(last_response):
        tag_logger.info(f"Retry {last_response.url}")

        if "zhihu.com" in last_response.url:
            headers = _get_zhihu_header()
        elif "csdn.net" in last_response.url:
            headers = _get_csdn_header()
        elif "cnblogs.com" in last_response.url:
            headers = _get_cnblog_header()
        elif "sohu.com" in last_response.url:
            headers = _get_sohu_header()
        elif "sina.com" in last_response.url:
            headers = _get_sina_header()
        elif "eastmoney.com" in last_response.url:
            headers = _get_eastmoney_header()
        elif "baidu.com" in last_response.url:
            headers = _get_baidu_header()
        elif "51cto.com" in last_response.url:
            headers = _get_51cto_header()
        else:
            headers = _get_other_website_header(last_response.url)
        
        response = requests.get(last_response.url, headers=headers)

        if response.status_code != 200:
            tag_logger.warning(f"Retry {last_response.url} failed, http code: {response.status_code}")
            return ""
        
        return get_response_text(response)
        

    tag_logger.info("get_baidu_search_item_content")
    if common_utils.is_empty(item_url):
        tag_logger.warning("item_url is none or empty")
        return ""
    
    tag_logger.debug(f"Requesting {item_url}")
    
    headers = _get_baidu_header()
    try:
        response = requests.get(item_url, headers=headers)
    except Exception as ex:
        tag_logger.error(f"Get {item_url} failed, ex={ex}")
        return ""

    if response.status_code != 200:
        tag_logger.warning(f"Request '{item_url}' failed, http code: {response.status_code}, url: {response.url}.")
        text = retry(response)
    else:
        text = get_response_text(response)
        if has_redirect(response):
            response = requests.get(response.url)

            if response.status_code != 200:
                print(f"Request '{response.url}' failed.")
                return ""

            text = get_response_text(response)
    
    if common_utils.is_empty(text):
        return ""
    
    soup = BeautifulSoup(markup=text, features="html.parser")
    body = soup.find("body")
    text = body.text if body is not None else soup.text

    return text.strip().replace("\n", "").replace("\t", "")


# search_results = baidu_search(keyword="301368.SZ 丰立智能", max_count=3)
# print(search_results)