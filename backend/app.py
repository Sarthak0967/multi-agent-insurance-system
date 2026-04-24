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
from visualizer.text_generator import generate_text
from visualizer.prompts import build_text_prompt
from visualizer.prompts import parse_visual_meta
from visualizer.image_generator import generate_image
from visualizer.prompts import build_image_prompt
from visualizer.overlay_text import overlay_text




app = FastAPI(title="Multi-Agent Insurance System API")




# ==========================================
# Request Models
# ==========================================

class ResearchRequest(BaseModel):
    policy_name: str
    
class ConceptRequest(BaseModel):
    concept: str


class CompareRequest(BaseModel):
    policy_a: str
    policy_b: str
    
class RecommendationRequest(BaseModel):
    age: int
    income: int
    budget: int
    dependents: int
    coverage_required: int
    risk_level: str   # low / medium / high


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


@app.post("/api/generate")
def generate_content(request: ConceptRequest):
    concept = request.concept.strip()

    if not concept:
        raise HTTPException(
            status_code=400,
            detail="Concept cannot be empty."
        )

    try:
        # Step 1 — Generate explanation + visual brief
        structured_text = generate_text(concept)

        # Step 2 — Parse visual metadata
        visual_meta = parse_visual_meta(structured_text)

        # Step 3 — Generate base image
        raw_image = generate_image(concept, structured_text)

        # Step 4 — Overlay explanation text onto image
        image_base64 = raw_image.split(",")[1]

        final_image = overlay_text(
            image_base64,
            structured_text
        )

        image = f"data:image/png;base64,{final_image}"

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    return {
        "concept": concept,
        "explanation": structured_text,
        "visual_meta": visual_meta,
        "image": image,
    }