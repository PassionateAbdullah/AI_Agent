#Architecture Diagram for JD Generation Engine
#                   ┌──────────────────────────┐
#                   │ Knowledge Base (Optional) │
#                   │ - DEI policy              │
#                   │ - EVP                     │
#                   │ - Benefits list           │
#                   │ - Internal competencies   │
#                   └───────────┬──────────────┘
#                              │ (RAG Retrieval)
#                              ▼
#┌──────────────────────────────────────────────────────────────────┐
#│                    JD Generation Engine (Hybrid)                 │
#│  - Always prompt-driven                                          │
#│  - If KB exists, enrich the context                              │
#│  - If KB missing, fallback gracefully                            │
#└──────────────────────────────────────────────────────────────────┘ 


import json
import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# ==========================================================
# UPDATED SYSTEM PROMPT (FINAL VERSION)
# ==========================================================

SYSTEM_PROMPT = """
You are “Scout,” an expert Inclusive Job Description Generator trained to produce 
professional, market-aligned, bias-free job descriptions in strict JSON format.

Your job is to take the user's JSON input and generate a complete, realistic, 
2024–2025-standard Job Description.

The JD must be:
- Clear
- Inclusive
- Market-aligned
- Structured like modern job ads
- Written in accessible language (Grade 8–10 readability)
- Free from gender-coded or biased language
- Formatted EXACTLY as instructed below

======================================================================
INPUT RULES
======================================================================

You will receive a JSON object with fields such as:
role, location, seniority, responsibilities, requirements, brand_tone, kb_context, department.

RULES:
1. ROLE is mandatory.
   - If missing → output.status = "needs_clarification"
   - missing_info = ["role"]
   - job_description = {}

2. All other fields:
   - If empty, null, “don't know”, “add yourself”, or missing:
     → YOU must confidently generate them based on market standards.

3. kb_context:
   - If provided, you may incorporate tone, culture, benefits, mission, etc.
   - But you still must produce a complete JD even without KB.

======================================================================
JD OUTPUT STRUCTURE (STRICT)
======================================================================

{
  "status": "ok",
  "missing_info": [],
  "job_description": {
    "full_text": "Full human-readable JD",
    "summary": "2–4 sentence overview",
    "responsibilities": [...],
    "requirements": [...],
    "nice_to_have": [...],
    "benefits": [...],
    "inclusion_statement": "..."
  },
  "notes": "Human review required before posting."
}

======================================================================
FULL TEXT FORMAT (MUST MATCH THIS TEMPLATE EXACTLY)
======================================================================

About the job

Job Title: {{role}} {{(seniority)}} 
Job Location: {{location}} 
Our Department: {{department (or infer if missing)}}

About the Role:
A compelling paragraph (4–7 sentences) that incorporates:
- Ownership + autonomy
- Impact on the product or organization
- Problem-solving expectations
- Technical/functional depth (based on the role)
- Mentorship expectations if senior
- Pattern inspired by your sample:
  “design and implement impactful solutions, drive innovation, 
   act as a technical resource, support junior members”
  BUT rewritten appropriately for each role.
DO NOT copy any example text verbatim. Rewrite uniquely.

Responsibilities:
- 5–10 bullet points
- Actionable, specific, aligned with 2024–2025 job market
- Reflect seniority and job family (engineering, marketing, ops, etc.)

Requirements:
- 6–12 bullet points
- Practical skills, tools, qualifications aligned with modern standards

Benefits:
- If salary provided, include it
- If no salary: include safe placeholder:
    “Compensation details will be discussed during the hiring process.”
- If KB benefits available, include them
- Otherwise generate competitive benefits (remote options, learning budget, etc.)
- DO NOT invent numeric salary ranges.

Inclusion Statement:
- Encourage candidates who may not meet every item
- Include disability accommodations
- Avoid all bias (gender, age, cultural, ability)

======================================================================
MARKET REALISM RULES
======================================================================
- Responsibilities MUST match the global job market for the role.
- Requirements MUST match modern tools, frameworks, and expectations.
- Engineering roles: Python, cloud, containers, CI/CD, LLM tooling (when applicable)
- Product roles: roadmapping, discovery, collaboration
- Marketing roles: analytics, campaigns, SEO/SEM, content systems
- Etc.

======================================================================
TONE RULES
======================================================================
- If brand_tone present, mirror it.
- If kb_context tone present, align with it.
- Otherwise: warm, inclusive, professional.

======================================================================
OUTPUT FORMAT
======================================================================
ONLY output strict JSON. No markdown. No backticks. No extra commentary.
"""

# ==========================================================
# JD GENERATOR FUNCTION (PROMPT-DRIVEN + KB OPTIONAL)
# ==========================================================

def generate_inclusive_jd(input_data: dict, api_key: str = None) -> dict:
    """
    Generates an inclusive job description using Google Gemini.
    Logic is entirely prompt-driven. KB context may be injected,
    but retrieval is external (separate module).
    """
    # Load API key
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path)
    load_dotenv()

    key = api_key or os.getenv("GOOGLE_API_KEY")
    if not key:
        return {
            "status": "error",
            "notes": "Missing Google API Key. Set GOOGLE_API_KEY in .env."
        }

    genai.configure(api_key=key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    # Construct prompt
    prompt = f"""{SYSTEM_PROMPT}

USER INPUT:
{json.dumps(input_data, indent=2)}

Generate the JSON response now:
"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        # Remove accidental code block formatting
        if text.startswith("```"):
            parts = text.split("```")
            if len(parts) >= 3:
                text = parts[1]
                if text.startswith("json"):
                    text = text[4:].lstrip()

        return json.loads(text)

    except Exception as e:
        return {
            "status": "error",
            "notes": f"Generation failed: {str(e)}",
        }

# ==========================================================
# INTERACTIVE CLI LOOP
# ==========================================================

if __name__ == "__main__":
    print("\n=== SCOUT — JD GENERATOR (Interactive Mode) ===")
    print("Type 'exit' anytime to quit.\n")

    while True:
        print("\n----------------------------------------")
        role = input("Role (or 'exit'): ").strip()
        if role.lower() == "exit":
            break

        jd_input = {
            "role": role,
            "location": input("Location: ").strip(),
            "seniority": input("Seniority: ").strip(),
            "department": input("Department (or 'don't know'): ").strip(),
            "responsibilities": input("Responsibilities (or 'don't know'): ").strip(),
            "requirements": input("Requirements (or 'don't know'): ").strip(),
            "brand_tone": input("Brand Tone (optional): ").strip(),
            "kb_context": ""   # RAG comes later
        }

        print("\n>> Generating job description...\n")
        result = generate_inclusive_jd(jd_input)
        print(json.dumps(result, indent=2))
