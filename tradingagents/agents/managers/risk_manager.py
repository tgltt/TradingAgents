import time
import json


def create_risk_manager(llm, memory):
    def risk_manager_node(state) -> dict:

        company_name = state["company_of_interest"]

        history = state["risk_debate_state"]["history"]
        risk_debate_state = state["risk_debate_state"]
        market_research_report = state["market_report"]
        news_report = state["news_report"]
        fundamentals_report = state["news_report"]
        sentiment_report = state["sentiment_report"]
        trader_plan = state["investment_plan"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

#         prompt = f"""As the Risk Management Judge and Debate Facilitator, your goal is to evaluate the debate between three risk analysts—Risky, Neutral, and Safe/Conservative—and determine the best course of action for the trader. Your decision must result in a clear recommendation: Buy, Sell, or Hold. Choose Hold only if strongly justified by specific arguments, not as a fallback when all sides seem valid. Strive for clarity and decisiveness.

# Guidelines for Decision-Making:
# 1. **Summarize Key Arguments**: Extract the strongest points from each analyst, focusing on relevance to the context.
# 2. **Provide Rationale**: Support your recommendation with direct quotes and counterarguments from the debate.
# 3. **Refine the Trader's Plan**: Start with the trader's original plan, **{trader_plan}**, and adjust it based on the analysts' insights.
# 4. **Learn from Past Mistakes**: Use lessons from **{past_memory_str}** to address prior misjudgments and improve the decision you are making now to make sure you don't make a wrong BUY/SELL/HOLD call that loses money.

# Deliverables:
# - A clear and actionable recommendation: Buy, Sell, or Hold.
# - Detailed reasoning anchored in the debate and past reflections.

# ---

# **Analysts Debate History:**  
# {history}

# ---

# Focus on actionable insights and continuous improvement. Build on past lessons, critically evaluate all perspectives, and ensure each decision advances better outcomes."""


        prompt = f"""作为风险管理裁判兼辩论主持人，你的目标是评估三位风险分析师——高风险偏好型、中立型与稳健/保守型——之间的辩论，并为交易者确定最佳行动方案。你的决策必须得出明确的建议：买入、卖出或持有。只有在具体论点充分论证的情况下才选择持有，切勿将其作为各方观点看似均有道理时的折中选项。务必做到清晰且果断。

决策准则：

1. **总结核心论点**：提炼每位分析师最具说服力的观点，聚焦于与当前情境相关的要点。
2. **阐述理由**：通过引用辩论中的原文及反驳论据来支撑你的建议。
3. **优化交易者的计划**：从交易者的原始计划入手, **{trader_plan}**, 并根据分析师的见解对其进行调整。
4. **从过往错误中学习**: 借鉴**{past_memory_str}**的经验教训, 用以纠正先前的判断失误，优化当前决策，确保不会因错误的买入/卖出/持有指令而导致资金亏损。

交付成果：
- 明确且可执行的建议：买入、卖出或持有。
- 基于辩论内容及过往反思的详细论证。

---

**分析师辩论历史:**  
{history}

---

聚焦于可落地的见解与持续改进。在过往经验教训的基础上，批判性审视各方观点，确保每一项决策都能推动更优成果的实现。"""

        response = llm.invoke(prompt)

        new_risk_debate_state = {
            "judge_decision": response.content,
            "history": risk_debate_state["history"],
            "risky_history": risk_debate_state["risky_history"],
            "safe_history": risk_debate_state["safe_history"],
            "neutral_history": risk_debate_state["neutral_history"],
            "latest_speaker": "Judge",
            "current_risky_response": risk_debate_state["current_risky_response"],
            "current_safe_response": risk_debate_state["current_safe_response"],
            "current_neutral_response": risk_debate_state["current_neutral_response"],
            "count": risk_debate_state["count"],
        }

        return {
            "risk_debate_state": new_risk_debate_state,
            "final_trade_decision": response.content,
        }

    return risk_manager_node
