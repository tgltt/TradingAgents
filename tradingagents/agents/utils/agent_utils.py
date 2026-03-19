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
    def get_reddit_news(
        curr_date: Annotated[str, "Date you want to get news for in yyyy-mm-dd format"],
    ) -> str:
        """
        Retrieve global news from Reddit within a specified time frame.
        Args:
            curr_date (str): Date you want to get news for in yyyy-mm-dd format
        Returns:
            str: A formatted dataframe containing the latest global news from Reddit in the specified time frame.
        """
        
        global_news_result = interface.get_reddit_global_news(curr_date, 7, 5)

        return global_news_result

    @staticmethod
    @tool
    def get_finnhub_news(
        ticker: Annotated[
            str,
            "Search query of a company, e.g. 'AAPL, TSM, etc.",
        ],
        start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
        end_date: Annotated[str, "End date in yyyy-mm-dd format"],
    ):
        """
        Retrieve the latest news about a given stock from Finnhub within a date range
        Args:
            ticker (str): Ticker of a company. e.g. AAPL, TSM
            start_date (str): Start date in yyyy-mm-dd format
            end_date (str): End date in yyyy-mm-dd format
        Returns:
            str: A formatted dataframe containing news about the company within the date range from start_date to end_date
        """

        end_date_str = end_date

        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        look_back_days = (end_date - start_date).days

        finnhub_news_result = interface.get_finnhub_news(
            ticker, end_date_str, look_back_days
        )

        return finnhub_news_result

    @staticmethod
    @tool
    def get_reddit_stock_info(
        ticker: Annotated[
            str,
            "Ticker of a company. e.g. AAPL, TSM",
        ],
        curr_date: Annotated[str, "Current date you want to get news for"],
    ) -> str:
        """
        Retrieve the latest news about a given stock from Reddit, given the current date.
        Args:
            ticker (str): Ticker of a company. e.g. AAPL, TSM
            curr_date (str): current date in yyyy-mm-dd format to get news for
        Returns:
            str: A formatted dataframe containing the latest news about the company on the given date
        """

        stock_news_results = interface.get_reddit_company_news(ticker, curr_date, 7, 5)

        return stock_news_results

    @staticmethod
    @tool
    def get_tushare_tech_data_offline(
        symbol: Annotated[str, "公司代码"],
        start_date: Annotated[str, "Start date in yyyymmdd format"],
        end_date: Annotated[str, "End date in yyyymmdd format"],
    ) -> str:
        """
        从本地缓存，检索指定上市公司的股价数据.
        参数:
            symbol (str): 公司代码, e.g. 600036.SH, 300119.SZ
            start_date (str): 开始日期，格式为yyyymmdd
            end_date (str): 结束日期，格式为yyyymmdd
        返回值:
            str: 一个格式化的dataframe，其中包含指定股票代码在指定日期范围内的股价数据。
        """

        result_data = interface.get_tushare_tech_data_offline(symbol, start_date, end_date)

        return result_data

    @staticmethod
    @tool
    def get_tushare_tech_data_online(
        symbol: Annotated[str, "公司代码"],
        start_date: Annotated[str, "Start date in yyyymmdd format"],
        end_date: Annotated[str, "End date in yyyymmdd format"],
    ) -> str:
        """
        调用TuShare接口，检索指定上市公司的股价数据.
        参数:
            symbol (str): 公司代码, e.g. 600036.SH, 300119.SZ
            start_date (str): 开始日期，格式为yyyymmdd
            end_date (str): 结束日期，格式为yyyymmdd
        返回值:
            str: 一个格式化的dataframe，其中包含指定股票代码在指定日期范围内的股价数据。
        """

        result_data = interface.get_tushare_tech_data_online(symbol, start_date, end_date)

        return result_data


    @staticmethod
    @tool
    def get_stockstats_indicators_report_offline(
        symbol: Annotated[str, "公司代码"],
        indicator: Annotated[
            str, "待分析的技术指标"
        ],
        curr_date: Annotated[
            str, "当前交易日期, 格式为YYYYmmdd"
        ],
        look_back_days: Annotated[int, "向前回溯的天数"] = 30,
    ) -> str:
        """
        根据给定的公司代码和技术指标，离线获取本地缓存的股价数据，并计算出相应的技术指标数值。
        参数:
            symbol (str): 公司代码, e.g. 600036.SH, 300119.SZ 
            indicator (str): 将要计算和分析的技术指标
            curr_date (str): 当前交易日期, 格式为YYYYmmdd
            look_back_days (int): 向前回溯的天数
        返回值:
            str: 一个格式化的dataframe，其中包含指定股票代码和指标的相关统计数据。
        """

        result_stockstats = interface.get_stock_stats_indicators_window(
            symbol, indicator, curr_date, look_back_days, False
        )

        return result_stockstats

    @staticmethod
    @tool
    def get_stockstats_indicators_report_online(
        symbol: Annotated[str, "公司代码"],
        indicator: Annotated[
            str, "待分析的技术指标"
        ],
        curr_date: Annotated[
            str, "当前交易日期, 格式为YYYYmmdd"
        ],
        look_back_days: Annotated[int, "向前回溯的天数"] = 30,
    ) -> str:
        """
        根据给定的公司代码和技术指标，在线获取股价数据并计算出相应的技术指标数值。
        参数:
            symbol (str): 公司代码, e.g. 600036.SH, 300119.SZ 
            indicator (str): 将要计算和分析的技术指标
            curr_date (str): 当前交易日期, 格式为YYYYmmdd
            look_back_days (int): 向前回溯的天数
        返回值:
            str: 一个格式化的dataframe，其中包含指定股票代码和指标的相关统计数据。
        """

        result_stockstats = interface.get_stock_stats_indicators_window(
            symbol, indicator, curr_date, look_back_days, True
        )

        return result_stockstats

    @staticmethod
    @tool
    def get_finnhub_company_insider_sentiment(
        ticker: Annotated[str, "ticker symbol for the company"],
        curr_date: Annotated[
            str,
            "current date of you are trading at, yyyy-mm-dd",
        ],
    ):
        """
        Retrieve insider sentiment information about a company (retrieved from public SEC information) for the past 30 days
        Args:
            ticker (str): ticker symbol of the company
            curr_date (str): current date you are trading at, yyyy-mm-dd
        Returns:
            str: a report of the sentiment in the past 30 days starting at curr_date
        """

        data_sentiment = interface.get_finnhub_company_insider_sentiment(
            ticker, curr_date, 30
        )

        return data_sentiment


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

