# from crewai import Task

# def create_explanation_task(agent):
#     return Task(
#         description="""
#         Using the research report provided,
#         explain the policy in very simple language.

#         Provide:
#         - Simple explanation
#         - Who should buy it
#         - Who should avoid it
#         - 5 key takeaways

#         Use bullet points.
#         """,
#         expected_output="""
#         A simplified explanation including:
#         - Clear summary
#         - Target audience
#         - Avoid audience
#         - 5 bullet takeaways
#         """,
#         agent=agent
#     )

from crewai import Task


def create_explanation_task(agent):
    return Task(
        description="""
        Using the research JSON provided,

        Return ONLY valid JSON.
        Do NOT add explanations.
        Do NOT use markdown.
        Do NOT use bullet points.

        Format EXACTLY like this:

        {
            "simple_explanation": "string",
            "who_should_buy": ["point1", "point2"],
            "who_should_avoid": ["point1", "point2"],
            "key_takeaways": ["point1", "point2", "point3", "point4", "point5"]
        }
        """,
        agent=agent,
        expected_output="Strict structured JSON explanation"
    )