from crewai import Crew, Process
from agents.researcher import create_researcher
from agents.explainer import create_explainer
from tasks.research_task import create_research_task
from tasks.explanation_task import create_explanation_task
from utils.policy_validator import validate_policy, AVAILABLE_POLICIES


def run():
    policy_name = input("Enter Insurance Policy Name: ")

    # ✅ VALIDATION LAYER
    validated_policy = validate_policy(policy_name)

    if not validated_policy:
        print("\n❌ Invalid policy name.")
        print("Available policies:")
        for policy in AVAILABLE_POLICIES:
            print(f"- {policy}")
        return

    # Use validated and properly formatted name
    policy_name = validated_policy

    researcher = create_researcher()
    explainer = create_explainer()

    research_task = create_research_task(researcher, policy_name)
    explanation_task = create_explanation_task(explainer)

    crew = Crew(
        agents=[researcher, explainer],
        tasks=[research_task, explanation_task],
        process=Process.sequential,
        verbose=True
    )

    result = crew.kickoff()

    print("\n\nFINAL OUTPUT:\n")
    print(result)


if __name__ == "__main__":
    run()
