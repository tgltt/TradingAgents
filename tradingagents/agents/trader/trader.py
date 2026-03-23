import functools
import time
import json


def create_trader(llm, memory):
    def trader_node(state, name):
        company_name = state["company_of_interest"]
        investment_plan = state["investment_plan"]
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        # past_memory_str = ""
        # if past_memories:
        #     for i, rec in enumerate(past_memories, 1):
        #         past_memory_str += rec["recommendation"] + "\n\n"
        # else:
        #     past_memory_str = "No past memories found."

        # context = {
        #     "role": "user",
        #     "content": f"Based on a comprehensive analysis by a team of analysts, here is an investment plan tailored for {company_name}. This plan incorporates insights from current technical market trends, macroeconomic indicators, and social media sentiment. Use this plan as a foundation for evaluating your next trading decision.\n\nProposed Investment Plan: {investment_plan}\n\nLeverage these insights to make an informed and strategic decision.",
        # }

        # messages = [
        #     {
        #         "role": "system",
        #         "content": f"""You are a trading agent analyzing market data to make investment decisions. Based on your analysis, provide a specific recommendation to buy, sell, or hold. End with a firm decision and always conclude your response with 'FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL**' to confirm your recommendation. Do not forget to utilize lessons from past decisions to learn from your mistakes. Here is some reflections from similar situatiosn you traded in and the lessons learned: {past_memory_str}""",
        #     },
        #     context,
        # ]
        
        past_memory_str = ""
        if past_memories:
            for i, rec in enumerate(past_memories, 1):
                past_memory_str += rec["recommendation"] + "\n\n"
        else:
            past_memory_str = "No past memories found."

        context = {
            "role": "user",
            "content": f"基于分析师团队的全面分析, 以下是为{company_name}量身定制的投资计划. 本计划融合了当前技术市场趋势、宏观经济指标及社交媒体情绪的综合洞察。请以此计划为基础，评估您的下一步交易决策。\n\n推荐的投资计划: {investment_plan}\n\n利用这些见解做出明智且具有战略性的决策。",
        }

        messages = [
            {
                "role": "system",
                "content": f"""你是一名交易智能体，通过分析市场数据来做出投资决策。请基于你的分析，提供买入、卖出或持有的具体建议。最终需给出明确决策，并在回复结尾注明“最终交易建议：**买入/持有/卖出**”以确认你的推荐。请务必借鉴过往决策中的经验教训，避免重蹈覆辙。 以下是你曾交易过的类似情境的反思以及从中汲取的经验教训: {past_memory_str}""",
            },
            context,
        ]

        result = llm.invoke(messages)

        return {
            "messages": [result],
            "trader_investment_plan": result.content,
            "sender": name,
        }

    return functools.partial(trader_node, name="Trader")
