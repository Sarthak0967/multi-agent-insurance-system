import os
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"
os.environ["LANGCHAIN_TRACING_V2"] = "false"

from crewai import Crew, Process
from agents.researcher import create_researcher
from agents.explainer import create_explainer
from agents.comparator import create_comparator
from tasks.research_task import create_research_task
from tasks.explanation_task import create_explanation_task
from tasks.comparison_task import create_comparison_task
from utils.policy_validator import validate_policy, get_all_policies


# ============================================
# CLI MENU SYSTEM
# ============================================

def show_menu():
    print("\n======================================")
    print("   🛡️  Multi-Agent Insurance System")
    print("======================================")
    print("1. Research & Explain Single Policy")
    print("2. Compare Two Policies")
    print("3. View Available Policies")
    print("4. Exit")
    print("======================================")


# ============================================
# SINGLE POLICY FLOW
# ============================================

def run_single_policy():
    policy_input = input("\nEnter Insurance Policy Name: ")

    validated_policy = validate_policy(policy_input)

    if not validated_policy:
        print("\n❌ Invalid policy name.")
        print("Available policies:")
        for policy in get_all_policies():
            print(f"- {policy}")
        return

    researcher = create_researcher()
    explainer = create_explainer()

    research_task = create_research_task(researcher, validated_policy)
    explanation_task = create_explanation_task(explainer)

    crew = Crew(
        agents=[researcher, explainer],
        tasks=[research_task, explanation_task],
        process=Process.sequential,
        verbose=False  # 🔥 Disable lag logs
    )

    result = crew.kickoff()

    print("\n======================================")
    print("📘 POLICY REPORT")
    print("======================================\n")
    print(result)


# ============================================
# COMPARISON FLOW
# ============================================

def run_comparison():
    print("\nEnter two policies to compare")

    policy_one_input = input("Policy 1: ")
    policy_two_input = input("Policy 2: ")

    policy_one = validate_policy(policy_one_input)
    policy_two = validate_policy(policy_two_input)

    if not policy_one or not policy_two:
        print("Available policies:")
        for policy in get_all_policies():
            print(f"- {policy}")
        return

    researcher = create_researcher()
    comparator = create_comparator()

    # -----------------------------
    # STEP 1: Research both policies separately
    # -----------------------------
    research_task_1 = create_research_task(researcher, policy_one)
    research_task_2 = create_research_task(researcher, policy_two)

    research_crew = Crew(
        agents=[researcher],
        tasks=[research_task_1, research_task_2],
        process=Process.sequential,
        verbose=False  # 🔥 disable logs
    )

    research_outputs = research_crew.kickoff()

    # -----------------------------
    # STEP 2: Compare structured outputs
    # -----------------------------
    comparison_task = create_comparison_task(
        comparator,
        policy_one,
        policy_two,
        research_outputs
    )

    comparison_crew = Crew(
        agents=[comparator],
        tasks=[comparison_task],
        process=Process.sequential,
        verbose=False  # 🔥 disable logs
    )

    comparison_result = comparison_crew.kickoff()

    print("\n======================================")
    print("📊 SHORT POLICY COMPARISON")
    print("======================================\n")
    print(comparison_result)


# ============================================
# MAIN LOOP
# ============================================

def main():
    while True:
        show_menu()
        choice = input("Select an option (1-4): ")

        if choice == "1":
            run_single_policy()

        elif choice == "2":
            run_comparison()

        elif choice == "3":
            print("\nAvailable Policies:")
            for policy in get_all_policies():
                print(f"- {policy}")

        elif choice == "4":
            print("\nExiting system...")
            break

        else:
            print("\n❌ Invalid choice. Please select 1-4.")


if __name__ == "__main__":
    main()
