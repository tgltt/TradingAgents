import time
import json


def create_research_manager(llm, memory):
    def research_manager_node(state) -> dict:
        history = state["investment_debate_state"].get("history", "")
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        investment_debate_state = state["investment_debate_state"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

#         prompt = f"""As the portfolio manager and debate facilitator, your role is to critically evaluate this round of debate and make a definitive decision: align with the bear analyst, the bull analyst, or choose Hold only if it is strongly justified based on the arguments presented.

# Summarize the key points from both sides concisely, focusing on the most compelling evidence or reasoning. Your recommendation—Buy, Sell, or Hold—must be clear and actionable. Avoid defaulting to Hold simply because both sides have valid points; commit to a stance grounded in the debate's strongest arguments.

# Additionally, develop a detailed investment plan for the trader. This should include:

# Your Recommendation: A decisive stance supported by the most convincing arguments.
# Rationale: An explanation of why these arguments lead to your conclusion.
# Strategic Actions: Concrete steps for implementing the recommendation.
# Take into account your past mistakes on similar situations. Use these insights to refine your decision-making and ensure you are learning and improving. Present your analysis conversationally, as if speaking naturally, without special formatting. 

# Here are your past reflections on mistakes:
# \"{past_memory_str}\"

# Here is the debate:
# Debate History:
# {history}"""

        prompt = f"""作为投资组合经理兼辩论主持人，你的职责是严格评估本轮辩论，并做出明确决策：支持看空分析师、看涨分析师，或仅在论点充分论证的前提下选择持有。
简要总结双方的核心论点，聚焦于最具说服力的证据或推理。你的建议——买入、卖出或持有——必须明确且具有可操作性。请勿因双方论点均有道理就默认选择持有，而应基于辩论中最有力的论据做出坚定判断。

此外，为交易者制定一份详细的投资计划，内容应包括：
你的建议：基于最具说服力的论据所做出的明确立场。
理由：解释为何这些论据会导向你的结论。
策略行动：落实建议的具体步骤。

请结合你在类似情境中过往的失误，运用这些经验教训优化决策，确保在不断反思中精进。以自然对话的方式呈现分析，无需特殊格式。
这是你对过往失误的反思：
\"{past_memory_str}\"

这是辩论相关的信息:
辩论历史:
{history}"""

        response = llm.invoke(prompt)

        new_investment_debate_state = {
            "judge_decision": response.content,
            "history": investment_debate_state.get("history", ""),
            "bear_history": investment_debate_state.get("bear_history", ""),
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": response.content,
            "count": investment_debate_state["count"],
        }

        return {
            "investment_debate_state": new_investment_debate_state,
            "investment_plan": response.content,
        }

    return research_manager_node
