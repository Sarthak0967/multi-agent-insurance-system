from crewai import Crew, Process
from agents.researcher import create_researcher
from agents.explainer import create_explainer
from tasks.research_task import create_research_task
from tasks.explanation_task import create_explanation_task

def run():
    policy_name = input("Enter Insurance Policy Name: ")

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
