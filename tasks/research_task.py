from crewai import Task

def create_research_task(agent, policy_name):
    return Task(
        description=f"""
        Research the insurance policy: {policy_name}

        Provide:
        - Policy Overview
        - Premium Details
        - Benefits
        - Eligibility
        - Exclusions
        - Pros and Cons

        Output in a structured format.
        """,
        expected_output="""
        A structured insurance research report containing:
        - Overview
        - Premium
        - Benefits
        - Eligibility
        - Exclusions
        - Pros & Cons
        """,
        agent=agent
    )
