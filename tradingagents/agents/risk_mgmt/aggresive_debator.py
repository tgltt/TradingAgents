import time
import json


def create_risky_debator(llm):
    def risky_node(state) -> dict:
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        risky_history = risk_debate_state.get("risky_history", "")

        current_safe_response = risk_debate_state.get("current_safe_response", "")
        current_neutral_response = risk_debate_state.get("current_neutral_response", "")

        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        trader_decision = state["trader_investment_plan"]

#         prompt = f"""As the Risky Risk Analyst, your role is to actively champion high-reward, high-risk opportunities, emphasizing bold strategies and competitive advantages. When evaluating the trader's decision or plan, focus intently on the potential upside, growth potential, and innovative benefits—even when these come with elevated risk. Use the provided market data and sentiment analysis to strengthen your arguments and challenge the opposing views. Specifically, respond directly to each point made by the conservative and neutral analysts, countering with data-driven rebuttals and persuasive reasoning. Highlight where their caution might miss critical opportunities or where their assumptions may be overly conservative. Here is the trader's decision:

# {trader_decision}

# Your task is to create a compelling case for the trader's decision by questioning and critiquing the conservative and neutral stances to demonstrate why your high-reward perspective offers the best path forward. Incorporate insights from the following sources into your arguments:

# Market Research Report: {market_research_report}
# Social Media Sentiment Report: {sentiment_report}
# Latest World Affairs Report: {news_report}
# Company Fundamentals Report: {fundamentals_report}
# Here is the current conversation history: {history} Here are the last arguments from the conservative analyst: {current_safe_response} Here are the last arguments from the neutral analyst: {current_neutral_response}. If there are no responses from the other viewpoints, do not halluncinate and just present your point.

# Engage actively by addressing any specific concerns raised, refuting the weaknesses in their logic, and asserting the benefits of risk-taking to outpace market norms. Maintain a focus on debating and persuading, not just presenting data. Challenge each counterpoint to underscore why a high-risk approach is optimal. Output conversationally as if you are speaking without any special formatting."""


        prompt = f"""作为高风险偏好分析师，你的职责是积极倡导高回报、高风险的机会，着重强调大胆策略与竞争优势。在评估交易者的决策或计划时，应聚焦于潜在上行空间、增长潜力及创新价值——即使这些伴随着较高风险。运用所提供的市场数据与情绪分析来强化你的论点，并对对立观点提出挑战。具体而言，请直接回应保守派与中立派分析师的每一个观点，用数据驱动的反驳和具有说服力的推理予以回应。指出他们的谨慎态度可能错失关键机遇，或他们的假设可能过于保守。以下是该交易者的决策:
{trader_decision}

你的任务是通过质疑和剖析保守派与中立派的立场，为交易者的决策构建一个极具说服力的理由，以此证明为何你这种追求高回报的视角才是最佳前进路径。请将以下来源的见解融入你的论证之中:

市场研究报告: {market_research_report}
社交媒体情绪报告: {sentiment_report}
最新国际时事新闻:  {news_report}
公司基本面分析报告: {fundamentals_report}
当前对话历史: {history}

保守派分析师的最新论点: {current_safe_response} 
中立派分析师的最新论点: {current_neutral_response} 

如果其他观点没有回应，请勿凭空捏造，只需阐述你自己的观点即可。

主动回应对方提出的具体疑虑，驳斥其逻辑中的薄弱环节，并阐明承担风险以超越市场常态的收益。重点在于辩论与说服，而非仅仅呈现数据。针对每一个反驳点提出质疑，以强调为何高风险策略是最优选择。请以对话形式输出，如同日常交流，无需使用特殊格式。
"""



        response = llm.invoke(prompt)

        argument = f"Risky Analyst: {response.content}"

        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "risky_history": risky_history + "\n" + argument,
            "safe_history": risk_debate_state.get("safe_history", ""),
            "neutral_history": risk_debate_state.get("neutral_history", ""),
            "latest_speaker": "Risky",
            "current_risky_response": argument,
            "current_safe_response": risk_debate_state.get("current_safe_response", ""),
            "current_neutral_response": risk_debate_state.get(
                "current_neutral_response", ""
            ),
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return risky_node
