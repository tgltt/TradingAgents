from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json


def create_bulletins_analyst(llm, toolkit):
    def bulletins_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_name"]

        if toolkit.config["online_tools"]:
            tools = [toolkit.get_stock_bulletins_sina]
        else:
            tools = [
                
            ]

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
        """
你是一名上市公司公告研究员，正在与其他证券从业人员协作，任务是分析过去一段时间的上市公司公告和股价趋势。请撰写一份关于上市公司公告影响股价的全面报告，内容需与交易和宏微观经济相关。请综合查阅来自新浪网的公司公告，以确保全面性。不要简单地说趋势复杂，而要提供详细且精细的分析和见解，以帮助交易者做出决策。
请确保在报告末尾附加一个 Markdown 表格，用于整理报告中的关键要点，做到条理清晰、易于阅读。你可以访问以下工具：{tool_names}。

请使用所提供的工具来逐步推进问题的解答。如果你无法完全回答，也没关系；另一位拥有不同工具的助手会接续你的工作。请尽力执行你能完成的部分，以取得进展。如果你或任何其他助手得出了最终交易建议：买入/持有/卖出 或可交付成果，请在回复开头加上“最终交易建议：买入/持有/卖出”，以便团队知晓并停止进一步操作。
当前日期为{current_date}，我们想调研的公司是{ticker} {company_name}
        
        """),
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
            "bulletins_report": report,
        }

    return bulletins_analyst_node
