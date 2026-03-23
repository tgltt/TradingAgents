from langchain_core.messages import AIMessage
import time
import json


def create_safe_debator(llm):
    def safe_node(state) -> dict:
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        safe_history = risk_debate_state.get("safe_history", "")

        current_risky_response = risk_debate_state.get("current_risky_response", "")
        current_neutral_response = risk_debate_state.get("current_neutral_response", "")

        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        trader_decision = state["trader_investment_plan"]

#         prompt = f"""As the Safe/Conservative Risk Analyst, your primary objective is to protect assets, minimize volatility, and ensure steady, reliable growth. You prioritize stability, security, and risk mitigation, carefully assessing potential losses, economic downturns, and market volatility. When evaluating the trader's decision or plan, critically examine high-risk elements, pointing out where the decision may expose the firm to undue risk and where more cautious alternatives could secure long-term gains. Here is the trader's decision:

# {trader_decision}

# Your task is to actively counter the arguments of the Risky and Neutral Analysts, highlighting where their views may overlook potential threats or fail to prioritize sustainability. Respond directly to their points, drawing from the following data sources to build a convincing case for a low-risk approach adjustment to the trader's decision:

# Market Research Report: {market_research_report}
# Social Media Sentiment Report: {sentiment_report}
# Latest World Affairs Report: {news_report}
# Company Fundamentals Report: {fundamentals_report}
# Here is the current conversation history: {history} Here is the last response from the risky analyst: {current_risky_response} Here is the last response from the neutral analyst: {current_neutral_response}. If there are no responses from the other viewpoints, do not halluncinate and just present your point.

# Engage by questioning their optimism and emphasizing the potential downsides they may have overlooked. Address each of their counterpoints to showcase why a conservative stance is ultimately the safest path for the firm's assets. Focus on debating and critiquing their arguments to demonstrate the strength of a low-risk strategy over their approaches. Output conversationally as if you are speaking without any special formatting."""


        prompt = f"""作为稳健/保守型风险分析师，你的首要目标是保护资产、降低波动性，并确保稳定、可靠的增长。你优先考虑稳定性、安全性与风险缓释，审慎评估潜在损失、经济下行风险及市场波动。在评估交易者的决策或计划时，需严格审视其中的高风险要素，指出决策中可能使公司面临不必要风险之处，并说明更为谨慎的替代方案如何能保障长期收益。以下是该交易者的决策:

{trader_decision}

你的任务是积极反驳高风险偏好分析师与中立派分析师的论点，指出他们的观点可能忽视了潜在威胁，或未能将可持续性置于优先位置。请直接回应他们的观点，并利用以下数据来源，构建具有说服力的论据，主张对交易者的决策采取低风险方向的调整。:

市场研究报告: {market_research_report}
社交媒体情绪报告: {sentiment_report}
最新国际时事新闻:  {news_report}
公司基本面分析报告: {fundamentals_report}
当前对话历史: {history}
高风险偏好分析师的上一轮回应: {current_risky_response} 
中立派分析师的上一轮回应: {current_neutral_response}. 

如果其他观点没有回应，请勿凭空捏造，只需阐述你自己的观点即可。

通过质疑他们的乐观情绪、强调他们可能忽略的潜在下行风险来展开互动。针对他们的每一个反驳点进行回应，阐明为何保守立场最终是公司资产最安全的保障。聚焦于辩论并剖析他们的论点，以展现低风险策略相较于其方案的稳健性。请以对话形式输出，如同日常交流，无需使用特殊格式。"""

        response = llm.invoke(prompt)

        argument = f"Safe Analyst: {response.content}"

        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "risky_history": risk_debate_state.get("risky_history", ""),
            "safe_history": safe_history + "\n" + argument,
            "neutral_history": risk_debate_state.get("neutral_history", ""),
            "latest_speaker": "Safe",
            "current_risky_response": risk_debate_state.get(
                "current_risky_response", ""
            ),
            "current_safe_response": argument,
            "current_neutral_response": risk_debate_state.get(
                "current_neutral_response", ""
            ),
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return safe_node
