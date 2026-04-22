from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage, AIMessage
from typing import List
from typing import Annotated
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import RemoveMessage
from langchain_core.tools import tool
from datetime import date, timedelta, datetime
import functools
import pandas as pd
import os
from dateutil.relativedelta import relativedelta
from langchain_openai import ChatOpenAI
import tradingagents.dataflows.interface as interface
from tradingagents.default_config import DEFAULT_CONFIG
from langchain_core.messages import HumanMessage

import asyncio
from tradingagents.mcp.client.mcp_client import baidu_search 

import logging
from tradingagents.utils import common_utils


def create_msg_delete():
    def delete_messages(state):
        """Clear messages and add placeholder for Anthropic compatibility"""
        messages = state["messages"]
        
        # Remove all messages
        removal_operations = [RemoveMessage(id=m.id) for m in messages]
        
        # Add a minimal placeholder message
        placeholder = HumanMessage(content="Continue")
        
        return {"messages": removal_operations + [placeholder]}
    
    return delete_messages


class Toolkit:
    _config = DEFAULT_CONFIG.copy()


    @classmethod
    def update_config(cls, config):
        """Update the class-level configuration."""
        cls._config.update(config)


    @property
    def config(self):
        """Access the configuration."""
        return self._config


    def __init__(self, config=None):
        if config:
            self.update_config(config)


    @staticmethod
    @tool
    def get_stock_tech_data(
        symbol: Annotated[str, "公司代码"],
        # start_date: Annotated[str, "开始日期，格式为yyyymmdd"], start_date (str): 开始日期，格式为yyyymmdd
        end_date: Annotated[str, "结束日期，格式为yyyymmdd"]
    ) -> str:
        """
        获取公司的股价、成交量、技术指标等数据。
        参数:
            symbol (str): 公司代码, e.g. 600036.SH, 300119.SZ
            end_date (str): 结束日期，格式为yyyymmdd
        返回值:
            str: 一个格式化的dataframe，其中包含指定股票代码在指定日期范围内的股价、成交量、技术指标等数据。
        """

        start_date = datetime.strptime(end_date, "%Y%m%d") - timedelta(days=365)
        start_date = datetime.strftime(start_date, "%Y%m%d")
        result_data = interface.get_stock_tech_data(symbol, start_date, end_date)

        common_utils.pretty_log(f"result_data={result_data}", logging.INFO)

        return result_data
    

    @staticmethod
    @tool
    def get_google_news(
        query: Annotated[str, "Query to search with"],
        curr_date: Annotated[str, "Curr date in yyyy-mm-dd format"],
    ):
        """
        Retrieve the latest news from Google News based on a query and date range.
        Args:
            query (str): Query to search with
            curr_date (str): Current date in yyyy-mm-dd format
            look_back_days (int): How many days to look back
        Returns:
            str: A formatted string containing the latest news from Google News based on the query and date range.
        """

        google_news_results = interface.get_google_news(query, curr_date, 7)

        return google_news_results
    

    @staticmethod
    @tool
    def get_baidu_news(
        query: Annotated[str, "搜索使用的查询关键字"],
        max_count: Annotated[int, "最多返回几个新闻"]=3,
    ):
        """
        从百度搜索，基于查询关键词和最大返回个数，检索最新的新闻，
        Args:
            query (str): 搜索使用的查询关键字
            max_count (int): 最多返回几个新闻
        Returns:
            str: 从百度搜索返回的，与查询关键词相关的搜索结果。
        """
        common_utils.log("get_baidu_news", logging.INFO)
        if common_utils.is_empty(query):
            common_utils.log("query is none or empty", logging.WARNING)
            return ""
    
        return asyncio.run(baidu_search(query, max_count))
    

    @staticmethod
    @tool
    def get_stock_bulletins_sina(
        ticker: Annotated[str, "the company's ticker"],
        curr_date: Annotated[str, "Current date in yyyymmdd format"],
    ):
        """
        Retrieve the latest bulletins about a given stock by visiting sina financial website.
        Args:
            ticker (str): Ticker of a company. e.g. 600036.SH, 300119.SZ 
            curr_date (str): Current date in yyyymmdd format
        Returns:
            str: A formatted string containing the latest bulletins about the company on the given date.
        """

        bulletins_results = interface.get_stock_bulletins_sina(ticker, curr_date)

        return bulletins_results
    

    @staticmethod
    @tool
    def get_stock_news_sina(
        ticker: Annotated[str, "the company's ticker"],
        curr_date: Annotated[str, "Current date in yyyymmdd format"],
    ):
        """
        Retrieve the latest news about a given stock by visiting sina financial website.
        Args:
            ticker (str): Ticker of a company. e.g. 600036.SH, 300119.SZ 
            curr_date (str): Current date in yyyymmdd format
        Returns:
            str: A formatted string containing the latest news about the company on the given date.
        """

        news_results = interface.get_stock_news_sina(ticker, curr_date)

        return news_results


    @staticmethod
    @tool
    def get_stock_news_zhipu(
        ticker: Annotated[str, "the company's ticker"],
        curr_date: Annotated[str, "Current date in yyyymmdd format"],
    ):
        """
        Retrieve the latest news about a given stock by using Zhipu AI's news API.
        Args:
            ticker (str): Ticker of a company. e.g. 600036.SH, 300119.SZ 
            curr_date (str): Current date in yyyymmdd format
        Returns:
            str: A formatted string containing the latest news about the company on the given date.
        """

        news_results = interface.get_stock_news_zhipu(ticker, curr_date)

        return news_results


    @staticmethod
    @tool
    def get_global_news_zhipu(
        curr_date: Annotated[str, "Current date in yyyymmdd format"],
    ):
        """
        Retrieve the latest macroeconomics news on a given date using Zhipu AI's macroeconomics news API.
        Args:
            curr_date (str): Current date in yyyymmdd format
        Returns:
            str: A formatted string containing the latest macroeconomic news on the given date.
        """

        news_results = interface.get_global_news_zhipu(curr_date)

        return news_results


    @staticmethod
    @tool
    def get_fundamentals_tushare(
        ticker: Annotated[str, "公司代码"],
        curr_date: Annotated[str, "当前日期，格式为yyyymmdd"],
        look_back_years: Annotated[int, "向前回溯的年份数"] = 5):
        """
        使用Tushare接口获取指定股票在特定日期的最新基本面信息，包括公司概况、基本财务数据等。

        参数:
            ticker (str): 公司代码， e.g. 600036.SH, 300119.SZ 
            curr_date (str): 当前日期，格式为yyyymmdd
            look_back_years (int): 向前回溯的年份数
        返回值:
            str: 一个格式化的字符串，包含该公司在指定日期的最新基本面信息。
        """

        openai_fundamentals_results = interface.get_fundamentals_tushare(
            ticker, curr_date, look_back_years=look_back_years
        )

        return openai_fundamentals_results
