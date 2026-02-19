from crewai import Task


def create_comparison_task(agent, policy_one, policy_two, research_data):
    return Task(
        description=f"""
        Compare the following two insurance policies:

        POLICY 1: {policy_one}
        POLICY 2: {policy_two}

        Use the research data below:

        {research_data}

        Provide a SHORT executive comparison only.

        Structure:
        1. Key Differences (bullet points)
        2. Which policy is better for:
           - Risk-averse users
           - High return seekers
           - Long-term protection
        3. Final Recommendation (max 4 lines)

        Keep output concise.
        Do NOT repeat full research details.
        """,
        expected_output="Short executive comparison summary.",
        agent=agent
    )
