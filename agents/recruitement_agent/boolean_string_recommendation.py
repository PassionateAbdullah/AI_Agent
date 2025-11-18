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

Tasks:
1. Validate user input (role, location, seniority, skills)
2. Infer related titles, core skills, nice-to-have skills
3. Generate Boolean for LinkedIn + job boards
4. Ask for clarification if needed
5. Return JSON only

OUTPUT FORMAT:
{
  "status": "ok | needs_clarification",
  "missing_info": [],
  "refined_role": {
    "main_title": "",
    "related_titles": [],
    "core_skills": [],
    "nice_to_have": []
  },
  "boolean_search": {
    "linkedin": "",
    "job_boards": ""
  },
  "notes": ""
}
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
