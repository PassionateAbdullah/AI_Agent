import re
import json
from typing import List, Literal
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
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
# System Prompt
# -----------------------

SYSTEM_PROMPT = """
                You are a recruitment sourcing assistant.

                Your job:
                - Refine ambiguous job roles
                - Infer seniority and domain
                - Generate core skills (strict or generative)
                - Produce deterministic Boolean search strings
                - Output JSON only (no explanations)

                ====================================================
                1. INPUT VALIDATION
                ====================================================
                Validate the user input for:
                - role/title (mandatory)
                - location (optional)
                - seniority (optional)
                - skills (optional)

                If role/title is missing → 
                {
                "status": "needs_clarification",
                "missing_info": ["role/title"],
                "refined_role": null,
                "boolean_search": null,
                "notes": "Role/title is required."
                }

                ====================================================
                2. SKILL ENGINE (Hybrid Logic)
                ====================================================

                CASE A — User provides skills:
                    STRICT MODE:
                    - Use ONLY the provided skills
                    - Do NOT generate extra skills
                    - Clean, normalize, deduplicate

                CASE B — User provides NO skills:
                    GENERATIVE MODE:
                    - Add Universal Skills (Layer 1)
                    - Detect role_family via reasoning
                    - Add role_family default skills (Layer 2)
                    - Detect domain/industry from user input
                        → Add domain-specific skills (Layer 3)
                    - Prioritize 5–7 core skills total
                    - Sort alphabetically
                    - Ensure skills align with seniority & location context

                Universal skills (for junior/mid):
                ["Communication", "Collaboration", "Problem Solving", "Documentation", "Time Management"]

                For senior roles:
                - Focus more on leadership, system-level skills, architecture, stakeholder mgmt.
                - Reduce generic soft skills unless critical.

                ====================================================
                3. SENIORITY INFERENCE
                ====================================================
                Infer seniority using patterns:

                Junior:
                - “intern”, “entry”, “junior”, “0-1 years”

                Mid:
                - “mid-level”, “2–5 years”

                Senior:
                - “senior”, “lead”, “principal”, “manager”, 
                “5+ years”, “7+ years”, “director”, “head”, “chief”

                If unclear → default to **mid-level**.

                ====================================================
                4. ROLE REFINEMENT
                ====================================================
                Produce:

                - main_title  
                    → Clean, standardized title (e.g., "HR Manager", "Senior Software Engineer")

                - related_titles  
                    → 3–6 titles from the same role_family  
                    (Must be realistic and non-hallucinated)

                - core_skills  
                    → 5–7 skills (strict if user-provided, generative if not)

                - nice_to_have  
                    → 3–5 supplementary skills tailored to:
                        • role_family  
                        • seniority  
                        • domain  
                        • location (if relevant)  

                Rules:
                - nice_to_have ≠ core_skills
                - senior roles → prioritize strategic & leadership-oriented nice_to_have

                ====================================================
                5. BOOLEAN GENERATION (Deterministic & Safe)
                ====================================================

                LinkedIn Boolean:
                - ("main_title" OR related_titles…)
                - AND (location if supplied)
                - AND (core skills)
                - Use quotes properly
                - Avoid hallucinated titles

                Job Board Boolean:
                - ("main_title" OR related_titles…)
                - AND (location if present)
                - AND (seniority keywords)
                - AND (core skills)
                - NOT (Assistant OR Coordinator OR Intern)

                Rules:
                - All parentheses balanced
                - No missing quotes
                - No nice_to_have in core skills
                - Must be job-board friendly (no special characters)

                ====================================================
                6. OUTPUT RULES
                ====================================================

                Return JSON ONLY in this exact format:

                {
                "status": "ok",
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

                NOTES:
                - “industry_focus” must be inferred only if user mentions it (e.g., tech, finance, healthcare)
                - If user input is unclear → add a short clarification request in “notes”

"""


# -----------------------
# Utility
# -----------------------

def stabilize(values):
    if not isinstance(values, list):
        return values
    return sorted(set(values), key=str.lower)

def clean_boolean_string(s):
    if not isinstance(s, str):
        return ""
    return s.replace("\\", "").strip()


# -----------------------
# MAIN FUNCTION (Final)
# -----------------------

def run_role_refinement(user_input: str) -> RoleRefinementOutput:
    model = genai.GenerativeModel("gemini-2.5-flash")

    # Build stable prompt
    final_prompt = f"{SYSTEM_PROMPT}\n\n### USER INPUT:\n{user_input}\n### END"

    response = model.generate_content(final_prompt)
    raw = response.text.strip()

    # Safe JSON extraction
    try:
        data = json.loads(raw)
    except:
        import re
        json_match = re.search(r"\{(?:[^{}]|(?:\{[^{}]*\}))*\}", raw, re.DOTALL)
        if not json_match:
            raise ValueError("AI output did not contain valid JSON.")
        data = json.loads(json_match.group(0))

    # Sort lists deterministically
    rr = data.get("refined_role", {})
    rr["related_titles"] = stabilize(rr.get("related_titles", []))
    rr["core_skills"] = stabilize(rr.get("core_skills", []))
    rr["nice_to_have"] = stabilize(rr.get("nice_to_have", []))

    # Standardize industry focus
    rr["industry_focus"] = rr.get("industry_focus", "").title() or "General"

    # Clean Boolean strings
    b = data.get("boolean_search", {})
    b["linkedin"] = clean_boolean_string(b.get("linkedin", ""))
    b["job_boards"] = clean_boolean_string(b.get("job_boards", ""))

    # Return validated output
    return RoleRefinementOutput(**data)


# -----------------------
# TEST
# -----------------------

if __name__ == "__main__":
    result = run_role_refinement("Software Engineer — New York")
    print(json.dumps(result.dict(), indent=2))
