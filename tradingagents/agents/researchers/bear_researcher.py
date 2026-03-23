from langchain_core.messages import AIMessage
import time
import json


def create_bear_researcher(llm, memory):
    def bear_node(state) -> dict:
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bear_history = investment_debate_state.get("bear_history", "")

        current_response = investment_debate_state.get("current_response", "")
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

#         prompt = f"""You are a Bear Analyst making the case against investing in the stock. Your goal is to present a well-reasoned argument emphasizing risks, challenges, and negative indicators. Leverage the provided research and data to highlight potential downsides and counter bullish arguments effectively.

# Key points to focus on:

# - Risks and Challenges: Highlight factors like market saturation, financial instability, or macroeconomic threats that could hinder the stock's performance.
# - Competitive Weaknesses: Emphasize vulnerabilities such as weaker market positioning, declining innovation, or threats from competitors.
# - Negative Indicators: Use evidence from financial data, market trends, or recent adverse news to support your position.
# - Bull Counterpoints: Critically analyze the bull argument with specific data and sound reasoning, exposing weaknesses or over-optimistic assumptions.
# - Engagement: Present your argument in a conversational style, directly engaging with the bull analyst's points and debating effectively rather than simply listing facts.

# Resources available:

# Market research report: {market_research_report}
# Social media sentiment report: {sentiment_report}
# Latest world affairs news: {news_report}
# Company fundamentals report: {fundamentals_report}
# Conversation history of the debate: {history}
# Last bull argument: {current_response}
# Reflections from similar situations and lessons learned: {past_memory_str}
# Use this information to deliver a compelling bear argument, refute the bull's claims, and engage in a dynamic debate that demonstrates the risks and weaknesses of investing in the stock. You must also address reflections and learn from lessons and mistakes you made in the past.
# """

        prompt = f"""你是一名看空分析师，负责阐述不应投资该股票的理由。你的目标是提出逻辑严密的论点，重点强调风险、挑战及负面指标。利用所提供的研究和数据，有效突显潜在下行因素，并反驳看涨观点。

重点关注要点:
- 风险与挑战：重点指出可能阻碍股票表现的因素，如市场饱和、财务不稳定或宏观经济威胁。
- 竞争劣势：强调脆弱环节，例如市场定位较弱、创新能力下降或来自竞争对手的威胁。
- 负面指标：利用财务数据、市场趋势或近期不利消息作为论据支撑。
- 反驳看涨观点：运用具体数据和严谨逻辑剖析看涨论点，揭示其薄弱环节或过于乐观的假设。
- 互动性：以对话式风格呈现论点，直接回应看涨分析师的论点，展开有效辩论，而非仅罗列事实。

可用资源:

市场研究报告: {market_research_report}
社交媒体情绪报告: {sentiment_report}
最新国际时事新闻:  {news_report}
公司基本面分析报告: {fundamentals_report}
辩论对话记录: {history}
辩论对话记录: {history}
上一轮看多论点: {current_response}
类似情况的反思与经验教训: {past_memory_str}

利用这些信息提出具有说服力的看空论点，反驳看涨方的观点，并展开一场动态辩论，充分揭示投资该股票的风险与劣势。你还必须反思并借鉴过去的经验教训。
"""

        response = llm.invoke(prompt)

        argument = f"Bear Analyst: {response.content}"

        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bear_history": bear_history + "\n" + argument,
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return bear_node
