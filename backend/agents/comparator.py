from crewai import Agent
from config.settings import get_llm

def create_comparator():
    return Agent(
        role="Insurance Policy Comparison Specialist",
        goal="Compare two insurance policies in a structured and analytical manner.",
        backstory=(
            "You are an expert financial analyst specializing in comparing "
            "insurance policies based on premiums, benefits, eligibility, "
            "exclusions, and overall value."
        ),
        llm=get_llm(),
        verbose=True
    )
