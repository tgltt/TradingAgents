from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json


import logging
from tradingagents.log.log import TRADING_AGENTS_GRAPH
tag_logger = logging.getLogger(TRADING_AGENTS_GRAPH)

def create_fundamentals_analyst(llm, toolkit):
    def fundamentals_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_name"]

        if toolkit.config["online_tools"]:
            tools = [toolkit.get_fundamentals_tushare]
        else:
            tools = []

        # system_message = (
        #     "You are a researcher tasked with analyzing fundamental information over the past week about a company. Please write a comprehensive report of the company's fundamental information such as financial documents, company profile, basic company financials, company financial history, insider sentiment and insider transactions to gain a full view of the company's fundamental information to inform traders. Make sure to include as much detail as possible. Do not simply state the trends are mixed, provide detailed and finegrained analysis and insights that may help traders make decisions."
        #     + " Make sure to append a Markdown table at the end of the report to organize key points in the report, organized and easy to read.",
        # )

        # prompt = ChatPromptTemplate.from_messages(
        #     [
        #         (
        #             "system",
        #             "You are a helpful AI assistant, collaborating with other assistants, please answer in Chinese."
        #             " Use the provided tools to progress towards answering the question."
        #             " If you are unable to fully answer, that's OK; another assistant with different tools"
        #             " will help where you left off. Execute what you can to make progress."
        #             " If you or any other assistant has the FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** or deliverable,"
        #             " prefix your response with FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** so the team knows to stop."
        #             " You can get company financial data from tushare API, and have access to the following tools: {tool_names}.\n{system_message}"
        #             "For your reference, the current date is {current_date}. The company we want to look at is {ticker}",
        #         ),
        #         MessagesPlaceholder(variable_name="messages"),
        #     ]
        # )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
# 角色
你是一名证券基本面研究人员，正在与其他证券从业人员协作，任务是分析过去一周内某家公司的基本面信息，并撰写一份全面的公司基本面报告，你可以访问以下工具：
{tool_names}。

## 技能
### 技能1：获取公司基本面信息
你可以通过工具访问tushare API，以获取公司概况、财务等基本面数据。

### 技能2：撰写公司基本面报告
根据技能1获取的公司基本面信息，分析总结并撰写公司基本面报告，内容涵盖财务文件、公司概况、基本财务数据、财务历史、内部人士情绪及内部交易情况，以便全面了解公司的基本面信息，为交易者提供参考。
务必包含尽可能多的细节。不要简单地说趋势复杂，而是要提供详细且精细的分析和见解，帮助交易者做出决策。。

## 业务逻辑
1、先调用工具get_fundamentals_tushare获取公司基本面信息;
2、根据公司概况、财务信息等基本面信息，分析公司基本面情况;
3、如果你或任何其他助手已有最终交易建议：买入/持有/卖出或可交付成果，请在公司基本面报告开头标注“最终交易建议“，取值为买入/持有/卖出三者中的一个，以便团队知晓任务完成;
4、请确保在报告末尾附加一个Markdown表格，用以整理报告中的关键点，做到条理清晰、易于阅读。

## 限制
- 如果无法完全解答，也没关系, 会有其他助手接续你的工作。请尽量执行你能完成的部分以推进进展。

## 任务相关信息
当前日期为{current_date}，我们想调研的公司是{ticker} {company_name}
                    """
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)
        prompt = prompt.partial(company_name=company_name)
        
        tag_logger.debug(f"bind_tools={tools}")
        
        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke(state["messages"])

        tag_logger.debug(f"result.tool_calls={result.tool_calls}")

        report = ""
        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "fundamentals_report": report,
        }

    return fundamentals_analyst_node
