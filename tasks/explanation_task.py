from crewai import Task

def create_explanation_task(agent):
    return Task(
        description="""
        Using the research report provided,
        explain the policy in very simple language.

        Provide:
        - Simple explanation
        - Who should buy it
        - Who should avoid it
        - 5 key takeaways

        Use bullet points.
        """,
        expected_output="""
        A simplified explanation including:
        - Clear summary
        - Target audience
        - Avoid audience
        - 5 bullet takeaways
        """,
        agent=agent
    )
