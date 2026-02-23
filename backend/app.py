import os
import json
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from crewai import Crew, Process
from fastapi.middleware.cors import CORSMiddleware

# Disable telemetry
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"
os.environ["LANGCHAIN_TRACING_V2"] = "false"

# Import your modules
from agents.researcher import create_researcher
from agents.explainer import create_explainer
from agents.comparator import create_comparator
from tasks.research_task import create_research_task
from tasks.explanation_task import create_explanation_task
from tasks.comparison_task import create_comparison_task
from utils.policy_validator import validate_policy, get_all_policies




app = FastAPI(title="Multi-Agent Insurance System API")




# ==========================================
# Request Models
# ==========================================

class ResearchRequest(BaseModel):
    policy_name: str


class CompareRequest(BaseModel):
    policy_a: str
    policy_b: str


# ==========================================
# Utility: Clean LLM JSON
# ==========================================

def clean_llm_json(raw_output: str):
    """
    Removes markdown ```json blocks if present
    and returns parsed JSON safely.
    """
    cleaned = re.sub(r"```json|```", "", raw_output).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON returned by LLM")


# ==========================================
# Health Check
# ==========================================

@app.get("/api/system/health")
def health_check():
    return {
        "researcher_agent": "active",
        "explainer_agent": "active",
        "comparator_agent": "active",
        "llm_status": "connected"
    }


# ==========================================
# Get All Policies
# ==========================================

@app.get("/api/policies")
def get_policies():
    policies = get_all_policies()
    return policies


# ==========================================
# Research Single Policy
# ==========================================

@app.post("/api/research")
def research_policy(request: ResearchRequest):

    validated_policy = validate_policy(request.policy_name)

    if not validated_policy:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid policy name",
                "available_policies": get_all_policies()
            }
        )

    researcher = create_researcher()
    explainer = create_explainer()

    research_task = create_research_task(researcher, validated_policy)
    explanation_task = create_explanation_task(explainer)

    crew = Crew(
        agents=[researcher, explainer],
        tasks=[research_task, explanation_task],
        process=Process.sequential,
        verbose=False
    )

    result = crew.kickoff()

    return clean_llm_json(str(result))


# ==========================================
# Compare Two Policies
# ==========================================

@app.post("/api/compare")
def compare_policies(request: CompareRequest):

    policy_a = validate_policy(request.policy_a)
    policy_b = validate_policy(request.policy_b)

    if not policy_a or not policy_b:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid policy name(s)",
                "available_policies": get_all_policies()
            }
        )

    researcher = create_researcher()
    comparator = create_comparator()

    # Step 1: Research both
    research_task_1 = create_research_task(researcher, policy_a)
    research_task_2 = create_research_task(researcher, policy_b)

    research_crew = Crew(
        agents=[researcher],
        tasks=[research_task_1, research_task_2],
        process=Process.sequential,
        verbose=False
    )

    research_outputs = research_crew.kickoff()

    # Step 2: Compare structured research
    comparison_task = create_comparison_task(
        comparator,
        policy_a,
        policy_b,
        research_outputs
    )

    comparison_crew = Crew(
        agents=[comparator],
        tasks=[comparison_task],
        process=Process.sequential,
        verbose=False
    )

    comparison_result = comparison_crew.kickoff()

    return clean_llm_json(str(comparison_result))