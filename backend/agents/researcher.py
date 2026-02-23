from crewai import Agent
from config.settings import get_llm

def create_researcher():
    return Agent(
        role="Insurance Policy Research Specialist",
        goal="Research and analyze detailed information about insurance policies.",
        backstory=(
            "You are an expert financial analyst with 10 years of experience "
            "in evaluating insurance schemes."
        ),
        llm=get_llm(),
        verbose=True
    )
