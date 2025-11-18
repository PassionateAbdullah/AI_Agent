"""
Role Refinement & Boolean Search Builder
Final Version: Deterministic, Stable, Compact Prompt, Pydantic v1, google-generativeai
"""

import json
from typing import List, Literal
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment
load_dotenv()

# Auto-configure Gemini using GEMINI_API_KEY from environment
genai.configure()


# -----------------------
# Pydantic Models
# -----------------------

class RefinedRole(BaseModel):
    main_title: str
    related_titles: List[str]
    core_skills: List[str]
    nice_to_have: List[str]
    seniority_level: str
    industry_focus: str


class BooleanSearch(BaseModel):
    linkedin: str
    job_boards: str


class RoleRefinementOutput(BaseModel):
    status: Literal["ok", "needs_clarification"]
    missing_info: List[str]
    refined_role: RefinedRole
    boolean_search: BooleanSearch
    notes: str


# -----------------------
# SYSTEM PROMPT
# -----------------------

SYSTEM_PROMPT = """
            You are a recruitment sourcing assistant.

            Your workflow must ALWAYS follow these stages:

            Stage 1 — Extract meaning from user input:
            - seniority_level (Junior, Mid, Senior, Lead, Principal)
            - role_family (Data Science, Software Engineering, ML Engineer, Analytics, etc.)
            - location
            - must_have_skills mentioned directly
            - nice_to_have mentioned directly
            - domain_focus (only if explicitly mentioned)

            Stage 2 — Apply seniority logic:
            Junior → fundamentals only, no deep specialization  
            Mid → solid technical skills, moderate depth  
            Senior → advanced specialization, system-level depth  
            Lead/Principal → architecture, leadership, cross-functional impact  

            Stage 3 — Generate:
            - related_titles appropriate to the SAME seniority and SAME role_family
            - core_skills appropriate to the seniority and role
            - nice_to_have appropriate to the seniority and role

            Stage 4 — Boolean creation rules:
            - Use ONLY related_titles + core_skills
            - Boolean must be deterministic (same input = same output)
            - Format: ("Title1" OR "Title2") AND (Skill1 OR Skill2) AND (Location)
            - No prefixes like TITLE:, SKILLS:, LOCATION:
            - No composite skills ("TensorFlow OR PyTorch")
            - No duplicates
            - Alphabetically sorted

            Stage 5 — Output JSON only:
            {
            "status": "ok | needs_clarification",
            "missing_info": [],
            "refined_role": {
                "main_title": "",
                "related_titles": [],
                "core_skills": [],
                "nice_to_have": [],
                "seniority_level": "",
                "industry_focus": ""
            },
            "boolean_search": {
                "linkedin": "",
                "job_boards": ""
            },
            "notes": ""
            }

            Return JSON only.
"""


# -----------------------
# Stabilizer (Ensures Deterministic Output)
# -----------------------

def stabilize(values):
    """Remove duplicates, sort alphabetically, ensure deterministic output."""
    if not isinstance(values, list):
        return values
    return sorted(set(values), key=str.lower)


# -----------------------
# Main Function
# -----------------------

def run_role_refinement(user_input: str) -> RoleRefinementOutput:

    model = genai.GenerativeModel("gemini-2.5-flash")

    response = model.generate_content(
        SYSTEM_PROMPT + "\nUser Input: " + user_input
    )

    text = response.text.strip()

    # Extract JSON safely
    try:
        data = json.loads(text)
    except:
        start = text.find("{")
        end = text.rfind("}")
        data = json.loads(text[start:end + 1])

    # Stabilize lists for determinism
    data["refined_role"]["related_titles"] = stabilize(data["refined_role"]["related_titles"])
    data["refined_role"]["core_skills"] = stabilize(data["refined_role"]["core_skills"])
    data["refined_role"]["nice_to_have"] = stabilize(data["refined_role"]["nice_to_have"])

    return RoleRefinementOutput(**data)


# -----------------------
# Manual Test
# -----------------------

if __name__ == "__main__":
    result = run_role_refinement("jr. Data Scientist — Melbourne, Python, NLP")
    print(json.dumps(result.dict(), indent=2))