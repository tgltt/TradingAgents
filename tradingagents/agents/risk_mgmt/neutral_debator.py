import time
import json


def create_neutral_debator(llm):
    def neutral_node(state) -> dict:
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        neutral_history = risk_debate_state.get("neutral_history", "")

        current_risky_response = risk_debate_state.get("current_risky_response", "")
        current_safe_response = risk_debate_state.get("current_safe_response", "")

        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        trader_decision = state["trader_investment_plan"]

#         prompt = f"""As the Neutral Risk Analyst, your role is to provide a balanced perspective, weighing both the potential benefits and risks of the trader's decision or plan. You prioritize a well-rounded approach, evaluating the upsides and downsides while factoring in broader market trends, potential economic shifts, and diversification strategies.Here is the trader's decision:

# {trader_decision}

# Your task is to challenge both the Risky and Safe Analysts, pointing out where each perspective may be overly optimistic or overly cautious. Use insights from the following data sources to support a moderate, sustainable strategy to adjust the trader's decision:

# Market Research Report: {market_research_report}
# Social Media Sentiment Report: {sentiment_report}
# Latest World Affairs Report: {news_report}
# Company Fundamentals Report: {fundamentals_report}
# Here is the current conversation history: {history} Here is the last response from the risky analyst: {current_risky_response} Here is the last response from the safe analyst: {current_safe_response}. If there are no responses from the other viewpoints, do not halluncinate and just present your point.

# Engage actively by analyzing both sides critically, addressing weaknesses in the risky and conservative arguments to advocate for a more balanced approach. Challenge each of their points to illustrate why a moderate risk strategy might offer the best of both worlds, providing growth potential while safeguarding against extreme volatility. Focus on debating rather than simply presenting data, aiming to show that a balanced view can lead to the most reliable outcomes. Output conversationally as if you are speaking without any special formatting."""

        prompt = f"""作为中立风险分析师，你的职责是为交易者的决策或计划提供平衡的视角，权衡其潜在收益与风险。你注重全面分析，评估利弊得失，同时将更广泛的市场趋势、潜在的经济变化及多元化策略纳入考量。以下是该交易者的决策:

{trader_decision}

你的任务是同时向高风险偏好分析师与稳健型分析师提出挑战，指出各自视角中可能存在的过度乐观或过度谨慎之处。请利用以下数据来源中的见解，支持一种适度、可持续的策略，以对交易者的决策进行调整:

市场研究报告: {market_research_report}
社交媒体情绪报告: {sentiment_report}
最新国际时事新闻:  {news_report}
公司基本面分析报告: {fundamentals_report}
当前对话历史: {history}
 
高风险偏好分析师的最新论点: {current_risky_response} 
保守派分析师的最新论点: {current_safe_response}

如果其他观点没有回应，请勿凭空捏造，只需阐述你自己的观点即可。

通过批判性地分析双方观点，针对高风险与保守派论点中的薄弱之处进行回应，倡导一种更为平衡的策略。逐一挑战他们的观点，阐明为何适度的风险策略或许能兼顾两者之长——既提供增长潜力，又防范极端波动。聚焦于辩论而非单纯罗列数据，旨在说明平衡的视角才能带来最可靠的结果。请以对话形式输出，如同日常交流，无需使用特殊格式。"""


        response = llm.invoke(prompt)

        argument = f"Neutral Analyst: {response.content}"

        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "risky_history": risk_debate_state.get("risky_history", ""),
            "safe_history": risk_debate_state.get("safe_history", ""),
            "neutral_history": neutral_history + "\n" + argument,
            "latest_speaker": "Neutral",
            "current_risky_response": risk_debate_state.get(
                "current_risky_response", ""
            ),
            "current_safe_response": risk_debate_state.get("current_safe_response", ""),
            "current_neutral_response": argument,
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return neutral_node
