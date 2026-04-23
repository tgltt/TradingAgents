from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json


def create_market_analyst(llm, toolkit):

    def market_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_name"]

        tools = [
                toolkit.get_stock_tech_data
            ]

#         system_message = (
#             """You are a trading assistant tasked with analyzing financial markets. Your role is to select the **most relevant indicators** for a given market condition or trading strategy from the following list. The goal is to choose up to **8 indicators** that provide complementary insights without redundancy. Categories and each category's indicators are:

# Moving Averages:
# - close_50_sma: 50 SMA: A medium-term trend indicator. Usage: Identify trend direction and serve as dynamic support/resistance. Tips: It lags price; combine with faster indicators for timely signals.
# - close_200_sma: 200 SMA: A long-term trend benchmark. Usage: Confirm overall market trend and identify golden/death cross setups. Tips: It reacts slowly; best for strategic trend confirmation rather than frequent trading entries.
# - close_10_ema: 10 EMA: A responsive short-term average. Usage: Capture quick shifts in momentum and potential entry points. Tips: Prone to noise in choppy markets; use alongside longer averages for filtering false signals.

# MACD Related:
# - macd: MACD: Computes momentum via differences of EMAs. Usage: Look for crossovers and divergence as signals of trend changes. Tips: Confirm with other indicators in low-volatility or sideways markets.
# - macds: MACD Signal: An EMA smoothing of the MACD line. Usage: Use crossovers with the MACD line to trigger trades. Tips: Should be part of a broader strategy to avoid false positives.
# - macdh: MACD Histogram: Shows the gap between the MACD line and its signal. Usage: Visualize momentum strength and spot divergence early. Tips: Can be volatile; complement with additional filters in fast-moving markets.

# Momentum Indicators:
# - rsi: RSI: Measures momentum to flag overbought/oversold conditions. Usage: Apply 70/30 thresholds and watch for divergence to signal reversals. Tips: In strong trends, RSI may remain extreme; always cross-check with trend analysis.

# Volatility Indicators:
# - boll: Bollinger Middle: A 20 SMA serving as the basis for Bollinger Bands. Usage: Acts as a dynamic benchmark for price movement. Tips: Combine with the upper and lower bands to effectively spot breakouts or reversals.
# - boll_ub: Bollinger Upper Band: Typically 2 standard deviations above the middle line. Usage: Signals potential overbought conditions and breakout zones. Tips: Confirm signals with other tools; prices may ride the band in strong trends.
# - boll_lb: Bollinger Lower Band: Typically 2 standard deviations below the middle line. Usage: Indicates potential oversold conditions. Tips: Use additional analysis to avoid false reversal signals.
# - atr: ATR: Averages true range to measure volatility. Usage: Set stop-loss levels and adjust position sizes based on current market volatility. Tips: It's a reactive measure, so use it as part of a broader risk management strategy.

# Volume-Based Indicators:
# - vwma: VWMA: A moving average weighted by volume. Usage: Confirm trends by integrating price action with volume data. Tips: Watch for skewed results from volume spikes; use in combination with other volume analyses.

# - Select indicators that provide diverse and complementary information. Avoid redundancy (e.g., do not select both rsi and stochrsi). Also briefly explain why they are suitable for the given market context. When you tool call, please use the exact name of the indicators provided above as they are defined parameters, otherwise your call will fail. Please make sure to call get_YFin_data first to retrieve the CSV that is needed to generate indicators. Write a very detailed and nuanced report of the trends you observe. Do not simply state the trends are mixed, provide detailed and finegrained analysis and insights that may help traders make decisions."""
#             + """ Make sure to append a Markdown table at the end of the report to organize key points in the report, organized and easy to read."""
#         )

#         prompt = ChatPromptTemplate.from_messages(
#             [
#                 (
#                     "system",
#                     "You are a helpful AI assistant, collaborating with other assistants,  please use chinese to answer question."
#                     " Use the provided tools to progress towards answering the question."
#                     " If you are unable to fully answer, that's OK; another assistant with different tools"
#                     " will help where you left off. Execute what you can to make progress."
#                     " If you or any other assistant has the FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** or deliverable,"
#                     " prefix your response with FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** so the team knows to stop."
#                     " You have access to the following tools: {tool_names}.\n{system_message}"
#                     "For your reference, the current date is {current_date}. The company we want to look at is {ticker} {company_name}.",
#                 ),
#                 MessagesPlaceholder(variable_name="messages"),
#             ]
#         )

        
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
# 角色
你是一名证券技术分析人员，正在与其他证券从业人员协作，任务是从股价、成交量、技术指标等角度，根据{ticker} {company_name}过去某个时点到{current_date}的股价行情走势，去分析股价未来的走势，并撰写一份全面的公司技术面分析报告，你可以访问以下工具：
{tool_names}。


## 技术面分析逻辑
1、调用工具get_stock_tech_data获取公司股价、技术指标等数据，包括但不限于开盘价、最高价、最低价、收盘价、成交量、均线、MACD、KD、BIAS等;
2、结合收盘价和成交量，研判公司股价未来趋势，收盘价与成交量的关系如下：
   - 缩量上涨还会上涨：成交量减少，股价继续上涨，暗示上涨趋势可能持续
   - 缩量下跌还会下跌：成交量减少，股价继续下跌，暗示下跌趋势可能持续
   - 高位放巨量上涨：股价处于高位时，成交量激增，股价上涨，这通常预示着即将到来的下跌
   - 低位放巨量上涨：股价处于低位时，成交量激增，股价上涨，这通常预示着后市可能会有所回调
   - 低位放巨量下跌：股价处于低位时，成交量激增，股价下跌，这通常预示着后市可能会有反弹
   - 放量滞涨：成交量增加，但股价未能相应上涨，这通常预示着市场可能达到顶部
   - 缩量不跌：成交量减少，股价停止下跌，这可能意味着市场底部已经形成
   - 量大成顶部，量小成底部：成交量大时，市场容易形成顶部；成交量小时，市场容易形成底部
   - 顶部无量下跌：股价在高位时，成交量减少，股价下跌，这可能意味着市场后市还有创新高的可能
   - 顶部放量下跌：股价在高位时，成交量增加，股价下跌，这通常意味着市场后市很难再创新高。

3、结合收盘价和均线系统，研判公司股价未来趋势；
4、结合收盘价和技术指标，研判公司股价未来趋势；
5、综合步骤2~4的结论，得出最终的分析结论;
6、如果你或任何其他助手已有最终交易建议：买入/持有/卖出或可交付成果，请在公司基本面报告开头标注“最终交易建议“，取值为买入/持有/卖出三者中的一个，以便团队知晓任务完成;
7、请确保在报告末尾附加一个Markdown表格，用以整理报告中的关键点，做到条理清晰、易于阅读。


## 限制
- 如果无法完全解答，也没关系, 会有其他助手接续你的工作。请尽量执行你能完成的部分以推进进展。
                    """
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)
        prompt = prompt.partial(company_name=company_name)
        
        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke(state["messages"])

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content
       
        return {
            "messages": [result],
            "market_report": report,
        }

    return market_analyst_node
