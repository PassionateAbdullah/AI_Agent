"""
Role Refinement & Boolean Search Builder
Using google-generativeai (stable Gemini SDK)
"""

import json
from typing import List, Literal
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env
load_dotenv()

# Configure Gemini (auto-loads GEMINI_API_KEY from env)
genai.configure()

# -----------------------
# Pydantic Models
# -----------------------

class RefinedRole(BaseModel):
    main_title: str
    related_titles: List[str]
    core_skills: List[str]
    nice_to_have: List[str]
    


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
# System Prompt
# -----------------------

SYSTEM_PROMPT = """
        You are a recruitment sourcing assistant.

        Your job:
        Refine role inputs and generate consistent Boolean search strings.

        Inputs you receive:
        - role_title
        - location
        - seniority (optional)
        - must_have_skills (optional)
        - nice_to_have_skills (optional)

        Tasks:
        1. Validate the input.
        2. Infer and expand:
        - related_titles
        - core_skills (must-have)
        - nice_to_have (adjacent skills)
        - seniority_level
        - industry_focus
        3. Generate deterministic Boolean strings for:
        - LinkedIn
        - job boards
        4. Ask for clarification if required.
        5. Return JSON only.

        Deterministic Rules:
        - Same role title + same location must ALWAYS return the same output.
        - Use global hiring norms, not creativity.
        - Do not vary synonyms between calls.
        - Sort all lists alphabetically.
        - Boolean uses ONLY related_titles + core_skills.
        - No unnecessary variation.

        Boolean Construction:
        - Title cluster: ("A" OR "B" OR ...)
        - Skill cluster: (Skill1 OR Skill2 OR "Multi Word Skill")
        - Location only if clearly intended.
        - AND connects clusters.
        - No NOT/exclusions unless user requests.

        Clarification triggers:
        vague title, missing key skills, unclear seniority, missing location when necessary.

        OUTPUT FORMAT (JSON only):
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

    return RoleRefinementOutput.model_validate(data)


# -----------------------
# Manual Test
# -----------------------

if __name__ == "__main__":
    result = run_role_refinement("Data Scientist — Melbourne, Python, NLP")
    print(json.dumps(result.dict(), indent=2))
