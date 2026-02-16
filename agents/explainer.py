from crewai import Agent
from config.settings import get_llm

def create_explainer():
    return Agent(
        role="Insurance Advisor",
        goal="Explain complex insurance policies in simple language.",
        backstory=(
            "You are a customer-focused insurance advisor who simplifies "
            "technical policies into clear explanations."
        ),
        llm=get_llm(),
        verbose=True
    )
