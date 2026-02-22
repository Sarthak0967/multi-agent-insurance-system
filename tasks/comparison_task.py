# from crewai import Task


# def create_comparison_task(agent, policy_one, policy_two, research_data):
#     return Task(
#         description=f"""
#         Compare the following two insurance policies:

#         POLICY 1: {policy_one}
#         POLICY 2: {policy_two}

#         Use the research data below:

#         {research_data}

#         Provide a SHORT executive comparison only.

#         Structure:
#         1. Key Differences (bullet points)
#         2. Which policy is better for:
#            - Risk-averse users
#            - High return seekers
#            - Long-term protection
#         3. Final Recommendation (max 4 lines)

#         Keep output concise.
#         Do NOT repeat full research details.
#         """,
#         expected_output="Short executive comparison summary.",
#         agent=agent
#     )

from crewai import Task

def create_comparison_task(agent, policy_a, policy_b, research_outputs):
    return Task(
        description=f"""
        Compare the following two researched insurance policies.

        Policy A: {policy_a}
        Policy B: {policy_b}

        Research Data:
        {research_outputs}

        You MUST return structured JSON only.

        Format:
        {{
            "comparison": {{
                "premium_difference": "...",
                "coverage_difference": "...",
                "pros_comparison": "...",
                "cons_comparison": "...",
                "better_for_low_budget": "...",
                "better_for_high_coverage": "..."
            }},
            "recommendation": "Final recommendation in 4-5 lines"
        }}

        Return ONLY valid JSON.
        """,
        agent=agent,
        expected_output="Structured JSON with policy comparison and recommendation."
    )