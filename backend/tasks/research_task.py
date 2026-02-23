# from crewai import Task

# def create_research_task(agent, policy_name):
#     return Task(
#         description=f"""
#         Research the insurance policy: {policy_name}

#         Provide:
#         - Policy Overview
#         - Premium Details
#         - Benefits
#         - Eligibility
#         - Exclusions
#         - Pros and Cons

#         Output in a structured format.
        
#         Provide information in concise structured bullet points.
#         Avoid long explanations.
#         Maximum 300–400 words.

#         """,
#         expected_output="""
#         A structured insurance research report containing:
#         - Overview
#         - Premium
#         - Benefits
#         - Eligibility
#         - Exclusions
#         - Pros & Cons
#         """,
#         agent=agent
#     )

from crewai import Task

def create_research_task(agent, policy_name):
    return Task(
        description=f"""
        Research the insurance policy: {policy_name}

        You MUST return output strictly in JSON format.

        JSON structure:
        {{
            "policy_name": "{policy_name}",
            "summary": "Brief 4-5 line summary",
            "coverage": "Coverage details",
            "premium": "Premium details",
            "pros": ["point1", "point2"],
            "cons": ["point1", "point2"],
            "best_for": "Type of customer this is ideal for"
        }}

        Do NOT return explanation.
        Do NOT return markdown.
        Return ONLY valid JSON.
        """,
        agent=agent,
        expected_output="Structured JSON with policy research details."
    )
