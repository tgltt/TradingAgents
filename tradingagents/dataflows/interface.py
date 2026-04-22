from typing import Annotated, Dict
from collections import defaultdict

from .yfin_utils import *
from .stockstats_utils import *
from .googlenews_utils import *
from .sina_stock_utils import get_company_news, get_company_bulletins

# Import Chinese finance utilities if available
try:
    from .chinese_finance_utils import get_chinese_social_sentiment
except ImportError:
    def get_chinese_social_sentiment(*args, **kwargs):
        return "Chinese finance utilities not available"
from .finnhub_utils import get_data_in_range
from dateutil.relativedelta import relativedelta
from datetime import datetime
import json
import os
import pandas as pd
from tqdm import tqdm

from openai import OpenAI
from .config import get_config, set_config, DATA_DIR

import sxsc_tushare as sx
sx.set_token(os.getenv("TUSHARE_TOKEN"))
api = sx.get_api(env="prd")

import logging
from tradingagents.log.log import TRADING_AGENTS_GRAPH
tag_logger = logging.getLogger(TRADING_AGENTS_GRAPH)

from tradingagents.utils import common_utils

from datetime import datetime, timedelta


def get_google_news(
    query: Annotated[str, "Query to search with"],
    curr_date: Annotated[str, "Curr date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "how many days to look back"],
) -> str:
    query = query.replace(" ", "+")

    start_date = datetime.strptime(curr_date, "%Y-%m-%d")
    before = start_date - relativedelta(days=look_back_days)
    before = before.strftime("%Y-%m-%d")

    news_results = getNewsData(query, before, curr_date)

    news_str = ""

    for news in news_results:
        news_str += (
            f"### {news['title']} (source: {news['source']}) \n\n{news['snippet']}\n\n"
        )

    if len(news_results) == 0:
        return ""

    return f"## {query} Google News, from {before} to {curr_date}:\n\n{news_str}"


def get_reddit_global_news(
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "how many days to look back"],
    max_limit_per_day: Annotated[int, "Maximum number of news per day"],
) -> str:
    """
    Retrieve the latest top reddit news
    Args:
        start_date: Start date in yyyy-mm-dd format
        end_date: End date in yyyy-mm-dd format
    Returns:
        str: A formatted dataframe containing the latest news articles posts on reddit and meta information in these columns: "created_utc", "id", "title", "selftext", "score", "num_comments", "url"
    """

    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    before = start_date - relativedelta(days=look_back_days)
    before = before.strftime("%Y-%m-%d")

    posts = []
    # iterate from start_date to end_date
    curr_date = datetime.strptime(before, "%Y-%m-%d")

    total_iterations = (start_date - curr_date).days + 1
    pbar = tqdm(desc=f"Getting Global News on {start_date}", total=total_iterations)

    while curr_date <= start_date:
        curr_date_str = curr_date.strftime("%Y-%m-%d")
        fetch_result = fetch_top_from_category(
            "global_news",
            curr_date_str,
            max_limit_per_day,
            data_path=os.path.join(DATA_DIR, "reddit_data"),
        )
        posts.extend(fetch_result)
        curr_date += relativedelta(days=1)
        pbar.update(1)

    pbar.close()

    if len(posts) == 0:
        return ""

    news_str = ""
    for post in posts:
        if post["content"] == "":
            news_str += f"### {post['title']}\n\n"
        else:
            news_str += f"### {post['title']}\n\n{post['content']}\n\n"

    return f"## Global News Reddit, from {before} to {curr_date}:\n{news_str}"


def get_reddit_company_news(
    ticker: Annotated[str, "ticker symbol of the company"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "how many days to look back"],
    max_limit_per_day: Annotated[int, "Maximum number of news per day"],
) -> str:
    """
    Retrieve the latest top reddit news
    Args:
        ticker: ticker symbol of the company
        start_date: Start date in yyyy-mm-dd format
        end_date: End date in yyyy-mm-dd format
    Returns:
        str: A formatted dataframe containing the latest news articles posts on reddit and meta information in these columns: "created_utc", "id", "title", "selftext", "score", "num_comments", "url"
    """

    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    before = start_date - relativedelta(days=look_back_days)
    before = before.strftime("%Y-%m-%d")

    posts = []
    # iterate from start_date to end_date
    curr_date = datetime.strptime(before, "%Y-%m-%d")

    total_iterations = (start_date - curr_date).days + 1
    pbar = tqdm(
        desc=f"Getting Company News for {ticker} on {start_date}",
        total=total_iterations,
    )

    while curr_date <= start_date:
        curr_date_str = curr_date.strftime("%Y-%m-%d")
        fetch_result = fetch_top_from_category(
            "company_news",
            curr_date_str,
            max_limit_per_day,
            ticker,
            data_path=os.path.join(DATA_DIR, "reddit_data"),
        )
        posts.extend(fetch_result)
        curr_date += relativedelta(days=1)

        pbar.update(1)

    pbar.close()

    if len(posts) == 0:
        return ""

    news_str = ""
    for post in posts:
        if post["content"] == "":
            news_str += f"### {post['title']}\n\n"
        else:
            news_str += f"### {post['title']}\n\n{post['content']}\n\n"

    return f"##{ticker} News Reddit, from {before} to {curr_date}:\n\n{news_str}"


def get_stock_tech_data(
        symbol: Annotated[str, "公司代码"],
        start_date: Annotated[str, "Start date in yyyymmdd format"],
        end_date: Annotated[str, "End date in yyyymmdd format"],
    ) -> str:
        """
        检索指定上市公司的股价、成交量、技术指标等数据。
        参数:
            symbol (str): 公司代码, e.g. 600036.SH, 300119.SZ
            start_date (str): 开始日期，格式为yyyymmdd
            end_date (str): 结束日期，格式为yyyymmdd
        返回值:
            str: 一个格式化的dataframe，其中包含指定股票代码在指定日期范围内的股价、成交量、技术指标等数据。
        """
        tag_logger.info("get_stock_tech_data")

        # read in data
        cache_file = os.path.join(DATA_DIR, "tech_data", f"{symbol}-{start_date}-{end_date}.csv")

        tech_data = None
        if os.path.exists(cache_file):
            tech_data = pd.read_csv(cache_file)

        # Check if data is empty
        if common_utils.is_empty(tech_data):
            tag_logger.info(f"Load tech data for symbol {symbol} from {cache_file}")

            tech_data = _get_tushare_tech_data(symbol, start_date, end_date)
            # Check if data is empty
            if len(tech_data) <= 0:
                tag_logger.error(f"No data found for symbol '{symbol}' between {start_date} and {end_date}")

            tech_data = _get_stock_stats_indicators_window(tech_data)
            # Save tech data
            os.makedirs(cache_file[:cache_file.rindex(os.sep)], exist_ok=True)
            tech_data.to_csv(cache_file, index=False)

            tag_logger.info(f"Saved {cache_file}")
        
        tech_data_summary = _get_tushare_tech_data_summary(data=tech_data, symbol=symbol, start_date=start_date, end_date=end_date)
        
        return tech_data_summary


def _get_stock_stats_indicators_window (
    data: Annotated[DataFrame, "公司股价数据"]):
    tag_logger.info("_get_stock_stats_indicators_window")

    if common_utils.is_empty(data):
        tag_logger.info(f"Stock price data is none or empty")
        return data
        
    # data = data[["trade_date", "open", "high", "low", "close", "vol"]]
    data = data.rename(columns={"trade_date": "date", "vol": "volume"})

    date_column = data["date"]
    date_list = date_column.values.tolist()
    date_column.index = date_list

    data.index = date_list

    stats_data = wrap(data)
    # 计算指标
    # 均线
    data["close_5_sma"] = stats_data["close_5_sma"]
    data["close_10_sma"] = stats_data["close_10_sma"]
    data["close_20_sma"] = stats_data["close_20_sma"]
    data["close_60_sma"] = stats_data["close_60_sma"]
    data["close_240_sma"] = stats_data["close_240_sma"]

    # KD指标
    data["kdjk_18"] = stats_data["kdjk_18"]
    data["kdjd_18"] = stats_data["kdjd_18"]

    # MACD指标
    data["macd"] = stats_data["macd"]
    data["macds"] = stats_data["macds"]
    data["macdh"] = stats_data["macdh"]

    # BIAS指标
    data["bias_20"] = (stats_data["close"] - stats_data["close_20_sma"]) / stats_data["close_20_sma"] * 100

    # data.insert(0, "date", date_column.astype(str))

    return data
            

def _download_tushare_stock_price_data(
    symbol: Annotated[str, "Ticker symbol of the company"],
    start_date: Annotated[str, "Start date in yyyymmdd format"],
    end_date: Annotated[str, "End date in yyyymmdd format"],
    look_back_days: Annotated[int, "Look back days"] = 0) -> DataFrame:
    
    q_start_date = start_date
    if look_back_days > 0:
        q_start_date = datetime.strptime(start_date, "%Y%m%d")
        q_start_date = q_start_date - relativedelta(days=look_back_days)
        q_start_date = datetime.strftime(q_start_date, "%Y%m%d")
    
    data = api.daily(ts_code=symbol, start_date=q_start_date, end_date=end_date)
    
    return data


def _get_tushare_tech_data(
    symbol: Annotated[str, "Ticker symbol of the company"],
    start_date: Annotated[str, "Start date in yyyymmdd format"],
    end_date: Annotated[str, "End date in yyyymmdd format"]
):
    # Fetch historical data for the specified date range
    data = _download_tushare_stock_price_data(symbol=symbol, start_date=start_date, end_date=end_date)
    return data


def _get_tech_index_desc():
    tech_index_params = {
        # Moving Averages
        "close_5_sma": (
            "close_5_sma: 即5 MA, 一条反应灵敏的短期均线。"
            "用途：捕捉动能的快速变化及潜在的入场点。"
            "提示：在震荡市场中容易产生噪音；建议结合较长周期的均线使用，以过滤虚假信号。"
        ),
        "close_10_sma": (
            "close_10_sma: 即10 MA， 一条反应灵敏的中短期均线。"
            "用途：捕捉动能的快速变化及潜在的入场点。"
            "提示：在震荡市场中容易产生噪音；建议结合较长周期的均线使用，以过滤虚假信号。"
        ),
        "close_20_sma": (
            "close_20_sma: 即20 MA， 一条反应灵敏的中短期均线。"
            "用途：捕捉动能的快速变化及潜在的入场点。"
            "提示：在震荡市场中容易产生噪音；建议结合较长周期的均线使用，以过滤虚假信号。"
        ),
        "close_60_sma": (
            "close_60_sma: 即60 MA， 中期趋势指标。"
            "用途：识别趋势方向，并充当动态支撑/阻力位。"
            "提示：该指标滞后于价格，建议结合更灵敏的指标使用，以获取及时信号。"
        ),
        "close_240_sma": (
            "close_240_sma: 即240 MA， 长期趋势基准。 "
            "用途：确认整体市场趋势，并识别金叉/死叉形态。 "
            "提示：该指标反应较慢，最适合用于战略性趋势确认，而非频繁的交易入场。"
        ),
        # MACD Related
        "macd": (
            "MACD: 通过计算指数移动平均线（EMA）之间的差值来衡量动能。 "
            "用途：观察均线交叉与价格背离，作为趋势变化的信号。 "
            "提示：在低波动或横盘市场中，需结合其他指标进行确认。"
        ),
        "macds": (
            "MACD信号线：对MACD线进行平滑处理得到的指数移动平均线。 "
            "用途：利用其与MACD线的交叉来触发交易信号。 "
            "提示：应作为更广泛交易策略的一部分，以避免虚假信号。"
        ),
        "macdh": (
            "MACD柱状图：显示MACD线与其信号线之间的差值（缺口）。 "
            "用途：直观展示动能强度，并及早发现背离现象。 "
            "提示：该指标可能波动较大；在快速变化的市场中，建议配合其他过滤器使用。"
        ),
        # KDJ Related
        "kdj": (
            "kdj: 即随机指标，它的核心是研究股票收盘价在某个周期内的相对位置。kdj的数值范围通常在0到100之间，尤其适用于震荡行情，在趋势明确的单边市里，它很容易失灵。kdj由三条线组成：K线、D线和J线，K线反应相对迅速，可以看作是价格波动的快跑者；D线是K线的平滑，算是稳健派；J线则更为灵敏，波动更大，像是活跃分子。K线、D线、J线在一起，共同描绘出价格动能的强弱变化。"
            "用途: 有两个信号值得重点关注。一个是金叉和死叉。当K线从下往上穿过D线，形成金叉，通常被视作一个可能向上的信号；反之，K线从上往下穿过D线，形成死叉，则可能是一个向下的警示。另一个是背离。比如，股价创新高了，但KDJ指标的高点却没有跟上，反而在降低，这就叫顶背离，暗示上涨动能可能在衰减。反过来，股价创新低，指标低点却抬高，形成底背离，可能预示着下跌动力不足了。"
            "提示: 一般来说，当指标运行到80以上的区域，市场会认为进入了超买状态，即短期内买的人太多了，股价可能有点过热，有回调的可能。相反，当指标跌到20以下的区域，就进入了超买状态，意味着卖盘可能过度释放，股价有反弹的潜力。不要把超买超卖区域当作绝对的买卖指令，比如一看指标到了80以上就急着卖出，结果股价反而继续上涨，错过了后面一大段行情。在强势的上涨趋势里，KDJ可能会长时间停留在超买区，这叫高位钝化；在下跌趋势里，它也可能会在超卖区徘徊很久。所以，不要单独看kdj一个信号，需要结合其他指标联动分析，比如，看看股价的整体趋势是向上还是向下，这能帮我们判断那个金叉或死叉的效力有多强。再比如，结合成交量，如果金叉时伴随着放量，那这个信号的可靠性就会高很多。"
        ),
        "kdjk_18": (
            "kdjk: 为KDJ指标的K，即快线，反应短期价格走势，需要与kdjd联动分析。KDJ即随机指标，它的核心是研究股票收盘价在某个周期内的相对位置。kdj的数值范围通常在0到100之间，尤其适用于震荡行情，在趋势明确的单边市里，它很容易失灵。kdj由三条线组成：K线、D线和J线，K线反应相对迅速，可以看作是价格波动的快跑者；D线是K线的平滑，算是稳健派；J线则更为灵敏，波动更大，像是活跃分子。K线、D线、J线在一起，共同描绘出价格动能的强弱变化。"
            "用途: 有两个信号值得重点关注。一个是金叉和死叉。当K线从下往上穿过D线，形成金叉，通常被视作一个可能向上的信号；反之，K线从上往下穿过D线，形成死叉，则可能是一个向下的警示。另一个是背离。比如，股价创新高了，但KDJ指标的高点却没有跟上，反而在降低，这就叫顶背离，暗示上涨动能可能在衰减。反过来，股价创新低，指标低点却抬高，形成底背离，可能预示着下跌动力不足了。"
            "提示: 一般来说，当指标运行到80以上的区域，市场会认为进入了超买状态，即短期内买的人太多了，股价可能有点过热，有回调的可能。相反，当指标跌到20以下的区域，就进入了超买状态，意味着卖盘可能过度释放，股价有反弹的潜力。不要把超买超卖区域当作绝对的买卖指令，比如一看指标到了80以上就急着卖出，结果股价反而继续上涨，错过了后面一大段行情。在强势的上涨趋势里，KDJ可能会长时间停留在超买区，这叫高位钝化；在下跌趋势里，它也可能会在超卖区徘徊很久。所以，不要单独看kdj一个信号，需要结合其他指标联动分析，比如，看看股价的整体趋势是向上还是向下，这能帮我们判断那个金叉或死叉的效力有多强。再比如，结合成交量，如果金叉时伴随着放量，那这个信号的可靠性就会高很多。"
        ),
        "kdjd_18": (
            "kdjd: 为KDJ指标的D，即慢线，D为慢速指标，需要与kdjk联动分析。KDJ即随机指标，它的核心是研究股票收盘价在某个周期内的相对位置。kdj的数值范围通常在0到100之间，尤其适用于震荡行情，在趋势明确的单边市里，它很容易失灵。kdj由三条线组成：K线、D线和J线，K线反应相对迅速，可以看作是价格波动的快跑者；D线是K线的平滑，算是稳健派；J线则更为灵敏，波动更大，像是活跃分子。K线、D线、J线在一起，共同描绘出价格动能的强弱变化。"
            "用途: 有两个信号值得重点关注。一个是金叉和死叉。当K线从下往上穿过D线，形成金叉，通常被视作一个可能向上的信号；反之，K线从上往下穿过D线，形成死叉，则可能是一个向下的警示。另一个是背离。比如，股价创新高了，但KDJ指标的高点却没有跟上，反而在降低，这就叫顶背离，暗示上涨动能可能在衰减。反过来，股价创新低，指标低点却抬高，形成底背离，可能预示着下跌动力不足了。"
            "提示: 一般来说，当指标运行到80以上的区域，市场会认为进入了超买状态，即短期内买的人太多了，股价可能有点过热，有回调的可能。相反，当指标跌到20以下的区域，就进入了超买状态，意味着卖盘可能过度释放，股价有反弹的潜力。不要把超买超卖区域当作绝对的买卖指令，比如一看指标到了80以上就急着卖出，结果股价反而继续上涨，错过了后面一大段行情。在强势的上涨趋势里，KDJ可能会长时间停留在超买区，这叫高位钝化；在下跌趋势里，它也可能会在超卖区徘徊很久。所以，不要单独看kdj一个信号，需要结合其他指标联动分析，比如，看看股价的整体趋势是向上还是向下，这能帮我们判断那个金叉或死叉的效力有多强。再比如，结合成交量，如果金叉时伴随着放量，那这个信号的可靠性就会高很多。"
        ),
        # BIAS Related
        "bias_20": (
            "BIAS : 通过计算市场指数或收盘价与某条移动平均线之间的差距百分比，以反映一定时期内价格与其MA偏离程度的指标，从而得出价格在剧烈波动时因偏离移动平均趋势而造成回档或反弹的可能性，以及价格在正常波动范围内移动而形成继续原有势的可信度。"
            "用途: 应该结合不同情况灵活运用才能提高盈利机会。第一，对于风险不同的股票应区别对待。有业绩保证且估值水平合理的个股，在下跌情况下乖离率通常较低时就开始反弹。这是由于持有人心态稳定不愿低价抛售，同时空仓投资者担心错过时机而及时买入的结果。反之，对绩差股而言，其乖离率通常在跌至绝对值较大时，才开始反弹。第二，要考虑流通市值的影响。流通市值较大的股票，不容易被操纵，走势符合一般的市场规律，适宜用乖离率进行分析。而流通市值较小的个股或庄股由于容易被控盘，因此在使用该指标时应谨慎。第三，在股价的低位密集成交区，由于筹码分散，运用乖离率指导操作时成功率较高，而在股价经过大幅攀升后，在机构的操纵下容易暴涨暴跌，此时成功率则相对较低。"
            "提示: 当乖离率接近历史最大值时，预示着多方发威已接近极限，行情随时都可能向下，投资者应减仓，而不能盲目追高。当乖离率接近历史最小值时，预示着空方发威接近极限，行情随时都可能掉头向上，投资者不应再割肉出局而应逢低吸纳。"
        ),
    }

    return tech_index_params


def _get_tushare_tech_data_summary (
    data: Annotated[DataFrame, "Stock ticker data"],
    symbol: Annotated[str, "Ticker symbol of the company"],
    start_date: Annotated[str, "Start date in yyyymmdd format"],
    end_date: Annotated[str, "End date in yyyymmdd format"]
):
    # Add header information
    header = f"# {start_date}至{end_date} {symbol.upper()}股价数据：\n"
    header += f"# 总记录数: {0 if data is None else len(data)}\n"
    header += f"# 检索时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    header += f"# 检索到的股价数据: \n\n"

    if common_utils.is_empty(data):
        return header + " 无数据"

    selected_columns = ["date", "open", "high", "low", "close", "volume", "amount", 
                        "close_5_sma", "close_10_sma", "close_20_sma", "close_60_sma", "close_240_sma", 
                        "macd", "macds", "macdh", "kdjk_18", "kdjd_18", "bias_20"]
    data = data[selected_columns]
        
    # Convert DataFrame to CSV string, including trade_date、open、high、low、close、vol and amount
    price_data_string = data.iloc[:, :7].to_csv(index=False)

    data = data.astype({"date": str})

    tech_index_string = ""
    tech_index_params = _get_tech_index_desc()
    for i in range(7, len(selected_columns)):
        sub_data = data.iloc[:, [0, i]]
        indicator_value = ""
        for _, value in sub_data.iterrows():
            indicator_value += f"{value[0]}: {value[1]:.2f}\n"  
                
        tech_index_string += (
            "\n\n"
            + f"## {start_date}至{end_date} {selected_columns[i]} 取值如下 :\n\n"
            + f"{indicator_value}"
            + "\n\n"
            + tech_index_params.get(selected_columns[i], "无可用描述。")
        )

    return header + price_data_string + tech_index_string
    

def get_stock_news_sina(ticker, curr_date):
    ticker = ticker[7:] + ticker[:6]

    start_date = datetime.strptime(curr_date, "%Y%m%d") - timedelta(days=14)
    start_date = datetime.strftime(start_date, "%Y%m%d")

    news_list = get_company_news(stock_code=ticker, 
                                 start_date=start_date,
                                 end_date=curr_date,
                                 max_count=10)

    return "\n\n".join([news["info_title"] + "\n" + news["info_date"] + "\n" + news["info_content"] for news in news_list])


def get_stock_bulletins_sina(ticker, curr_date):
    start_date = datetime.strptime(curr_date, "%Y%m%d") - timedelta(days=90)
    start_date = datetime.strftime(start_date, "%Y%m%d")

    bulletins_list = get_company_bulletins(stock_code=ticker[:6], 
                                           start_date=start_date,
                                           end_date=curr_date,
                                           max_count=30)

    return "\n\n".join([bulletin["info_title"] + "\n" + bulletin["info_date"] + "\n" + bulletin["info_content"] for bulletin in bulletins_list])


def get_stock_news_zhipu(ticker, curr_date):
    config = get_config()
    client = OpenAI(base_url=config["backend_url"], api_key=os.getenv('ZHIPU_API_KEY'))

    response = client.responses.create(
        model=config["quick_think_llm"],
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"Can you search Social Media for {ticker} from 7 days before {curr_date} to {curr_date}? Make sure you only get the data posted during that period.",
                    }
                ],
            }
        ],
        text={"format": {"type": "text"}},
        reasoning={},
        tools=[{
                    "type": "web_search",
                    "web_search": {
                        "enable": "True",
                        "search_engine": "search_pro",
                        "count": "10"
                    }
               }],
        temperature=1,
        max_output_tokens=4096,
        top_p=1,
        store=True,
    )

    return response.output[1].content[0].text


def get_global_news_zhipu(curr_date):
    config = get_config()
    client = OpenAI(base_url=config["backend_url"], api_key=os.getenv('ZHIPU_API_KEY'))
    
    response = client.responses.create(
        model=config["quick_think_llm"],
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"Can you search global or macroeconomics news from 7 days before {curr_date} to {curr_date} that would be informative for trading purposes? Make sure you only get the data posted during that period.",
                    }
                ],
            }
        ],
        text={"format": {"type": "text"}},
        reasoning={},
        tools=[{
                    "type": "web_search",
                    "web_search": {
                        "enable": "True",
                        "search_engine": "search_pro",
                        "count": "10"
                    }
               }],
        temperature=1,
        max_output_tokens=4096,
        top_p=1,
        store=True,
    )

    return response.output[1].content[0].text


def _get_company_profile(ticker):
    company_profile = defaultdict(str)
    
    stock_basic = api.stock_basic(ts_code=ticker, fields=["name", "industry"])
    stock_company = api.stock_company(ts_code=ticker, fields=["reg_capital"])
    
    company_profile["CompanyName"] = stock_basic["name"]
    company_profile["Industry"] = stock_basic["industry"]
    company_profile["RegCapital"] = str(stock_company["reg_capital"].astype(int))
    company_profile["Currency"] = "RMB"
    company_profile["Country"] = "China"
    
    return company_profile
    

def get_fundamentals_tushare(symbol: Annotated[str, "Ticker symbol of the company"],
                             cur_date: Annotated[str, "Current date in yyyymmdd format"],
                             look_back_years: Annotated[int, "How many years to look back"]):
    def safe_get_fund_item(data, item_name, index=0):
        if len(data) <= 0:
            return "N/A"
        
        if item_name not in data:
            return "N/A"
        
        if index < len(data):
            return "N/A"
        
        return data[item_name][index]
        
    dt = pd.to_datetime(cur_date)
    start_date = dt - pd.DateOffset(years=look_back_years)
    start_date = start_date.strftime("%Y%m%d")

    data = api.fina_indicator(ts_code=symbol, start_date=start_date, end_date=cur_date)
    data = data[["eps", "bps", "retainedps", "cfps", "profit_dedt", "gross_margin", "roe", "debt_to_assets", "or_yoy", "op_yoy", "fixed_assets"]]

    # Convert DataFrame to CSV string
    csv_string = data.to_csv(index=False)

    # Format report
    report = f"# {symbol.upper()} Fundamental Analysis Report (Tushare Data Source)\n\n"
    report += f"**Data Retrieved**: {cur_date}\n"
    report += f"**Data Source**: Tushare API\n\n"

    # Company profile section
    company_profile = _get_company_profile(ticker=symbol)
    if company_profile:
        report += "## Company Profile\n"
        report += f"- **Company Name**: {company_profile.get('name', 'N/A')}\n"
        report += f"- **Industry**: {company_profile.get('industry', 'N/A')}\n"
        report += f"- **Country**: {company_profile.get('Country', 'N/A')}\n"
        report += f"- **Currency**: {company_profile.get('Currency', 'N/A')}\n"
        report += f"- **Reg Capital**: {company_profile.get('reg_capital', 'N/A')} million RMB\n"

    # Basic financial metrics
    report += "## Key Financial Metrics\n"

    # Assets and Debt metrics 
    report += "### Assets and Debt Metrics\n"
    report += f"- **Fixed Assets**: {safe_get_fund_item(data, 'fixed_assets')}\n"
    report += f"- **Cash Flow Per Stock**: {safe_get_fund_item(data, 'cfps')}\n"
    report += f"- **Debt to Assets**: {safe_get_fund_item(data, 'debt_to_assets')}\n"

    # Profitability metrics
    report += "### Profitability Metrics\n"
    report += f"- **EPS**: {safe_get_fund_item(data, 'eps')}\n"
    report += f"- **BPS**: {safe_get_fund_item(data, 'bps')}\n"
    report += f"- **Gross Margin**: {data['gross_margin']}%\n"
    report += f"- **Retained PS**: {safe_get_fund_item(data, 'retainedps')}\n"
    # report += f"- **Return on Equity‌**: {data['roa']}%\n"
    report += f"- **Operating Income-on-year Growth rate**: {data['or_yoy']}%\n"
    report += f"- **Year-on-year Growth Rate of Operating Profit**: {data['op_yoy']}%\n\n"

    # Fundamental data of latest N years
    report += f"## Fundamental data of latest {look_back_years} years\n"
    report += f"{csv_string}"

    return report


def get_fundamentals_openai(ticker, curr_date):
    config = get_config()
    client = OpenAI(base_url=config["backend_url"])

    response = client.responses.create(
        model=config["quick_think_llm"],
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"Can you search Fundamental for discussions on {ticker} during of the month before {curr_date} to the month of {curr_date}. Make sure you only get the data posted during that period. List as a table, with PE/PS/Cash flow/ etc",
                    }
                ],
            }
        ],
        text={"format": {"type": "text"}},
        reasoning={},
        tools=[
            {
                "type": "web_search_preview",
                "user_location": {"type": "approximate"},
                "search_context_size": "low",
            }
        ],
        temperature=1,
        max_output_tokens=4096,
        top_p=1,
        store=True,
    )

    return response.output[1].content[0].text


def get_fundamentals_finnhub(ticker, curr_date):
    """
    Use Finnhub API to get stock fundamental data as an alternative to OpenAI
    Args:
        ticker (str): Stock symbol
        curr_date (str): Current date in yyyy-mm-dd format
    Returns:
        str: Formatted fundamental data report
    """
    try:
        import finnhub
        import os

        # Try to import cache manager
        try:
            from .cache_manager import get_cache
            cache = get_cache()

            # Check cache first
            cached_key = cache.find_cached_stock_data(ticker, curr_date, curr_date, "finnhub_fundamentals")
            if cached_key and cache.is_cache_valid(cached_key, ticker):
                cached_data = cache.load_stock_data(cached_key)
                if cached_data:
                    print(f"💾 [DEBUG] Loading Finnhub fundamental data from cache: {ticker}")
                    return cached_data
        except ImportError:
            cache = None
            print("⚠️ Cache manager not available, proceeding without cache")

        # Get Finnhub API key
        api_key = os.getenv('FINNHUB_API_KEY')
        if not api_key:
            return "Error: FINNHUB_API_KEY environment variable not configured"

        # Initialize Finnhub client
        finnhub_client = finnhub.Client(api_key=api_key)

        print(f"📊 [DEBUG] Using Finnhub API to get fundamental data for {ticker}...")

        # Get basic financial data
        try:
            basic_financials = finnhub_client.company_basic_financials(ticker, 'all')
        except Exception as e:
            print(f"❌ [DEBUG] Failed to get Finnhub basic financials: {str(e)}")
            basic_financials = None

        # Get company profile
        try:
            company_profile = finnhub_client.company_profile2(symbol=ticker)
        except Exception as e:
            print(f"❌ [DEBUG] Failed to get Finnhub company profile: {str(e)}")
            company_profile = None

        # Get earnings data
        try:
            earnings = finnhub_client.company_earnings(ticker, limit=4)
        except Exception as e:
            print(f"❌ [DEBUG] Failed to get Finnhub earnings data: {str(e)}")
            earnings = None

        # Format report
        report = f"# {ticker} Fundamental Analysis Report (Finnhub Data Source)\n\n"
        report += f"**Data Retrieved**: {curr_date}\n"
        report += f"**Data Source**: Finnhub API\n\n"

        # Company profile section
        if company_profile:
            report += "## Company Profile\n"
            report += f"- **Company Name**: {company_profile.get('name', 'N/A')}\n"
            report += f"- **Industry**: {company_profile.get('finnhubIndustry', 'N/A')}\n"
            report += f"- **Country**: {company_profile.get('country', 'N/A')}\n"
            report += f"- **Currency**: {company_profile.get('currency', 'N/A')}\n"
            report += f"- **Market Cap**: {company_profile.get('marketCapitalization', 'N/A')} million USD\n"
            report += f"- **Shares Outstanding**: {company_profile.get('shareOutstanding', 'N/A')} million shares\n\n"

        # Basic financial metrics
        if basic_financials and 'metric' in basic_financials:
            metrics = basic_financials['metric']
            report += "## Key Financial Metrics\n"

            # Valuation metrics
            report += "### Valuation Metrics\n"
            report += f"- **P/E Ratio (TTM)**: {metrics.get('peBasicExclExtraTTM', 'N/A')}\n"
            report += f"- **P/B Ratio**: {metrics.get('pbAnnual', 'N/A')}\n"
            report += f"- **P/S Ratio (TTM)**: {metrics.get('psAnnual', 'N/A')}\n"
            report += f"- **EV/EBITDA (TTM)**: {metrics.get('evEbitdaTTM', 'N/A')}\n\n"

            # Profitability metrics
            report += "### Profitability Metrics\n"
            report += f"- **ROE (TTM)**: {metrics.get('roeTTM', 'N/A')}%\n"
            report += f"- **ROA (TTM)**: {metrics.get('roaTTM', 'N/A')}%\n"
            report += f"- **Gross Margin (TTM)**: {metrics.get('grossMarginTTM', 'N/A')}%\n"
            report += f"- **Net Margin (TTM)**: {metrics.get('netProfitMarginTTM', 'N/A')}%\n\n"

            # Growth metrics
            report += "### Growth Metrics\n"
            report += f"- **Revenue Growth (5Y)**: {metrics.get('revenueGrowthTTMYoy', 'N/A')}%\n"
            report += f"- **EPS Growth (5Y)**: {metrics.get('epsGrowthTTMYoy', 'N/A')}%\n\n"

        # Earnings data
        if earnings and len(earnings) > 0:
            report += "## Recent Earnings\n"
            for i, earning in enumerate(earnings[:4]):  # Show last 4 quarters
                report += f"### Q{i+1} (Period: {earning.get('period', 'N/A')})\n"
                report += f"- **Actual EPS**: ${earning.get('actual', 'N/A')}\n"
                report += f"- **Estimated EPS**: ${earning.get('estimate', 'N/A')}\n"
                if earning.get('actual') and earning.get('estimate'):
                    surprise = earning['actual'] - earning['estimate']
                    report += f"- **Surprise**: ${surprise:.2f}\n"
                report += "\n"

        # Cache the result if cache is available
        if cache:
            try:
                cache.save_stock_data(ticker, report, curr_date, curr_date, "finnhub_fundamentals")
                print(f"💾 [DEBUG] Cached Finnhub fundamental data for {ticker}")
            except Exception as e:
                print(f"⚠️ [DEBUG] Failed to cache data: {e}")

        print(f"✅ [DEBUG] Successfully retrieved Finnhub fundamental data for {ticker}")
        return report

    except ImportError:
        return "Error: finnhub-python package not installed. Please install with: pip install finnhub-python"
    except Exception as e:
        error_msg = f"Error retrieving Finnhub fundamental data for {ticker}: {str(e)}"
        print(f"❌ [DEBUG] {error_msg}")
        return error_msg

