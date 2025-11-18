"""
prompt_templates.py

This module contains prompt templates for the different functions
provided by the Scout recruitment agent.  Each template is designed
to be deterministic so that the functions can be unit-tested without
requiring any external services.  When integrating a large language
model, these templates can be formatted with concrete parameters
before being sent to the model.

All templates use Python's `str.format` syntax for parameter
injection.  See the documentation in `handlers.py` for information
on each function's parameters.

"""

from typing import Dict

# Templates for role refinement and Boolean search building.  The
# template takes the role title, location, seniority and optional
# must_have and nice_to_have skills.  The output should be a
# Boolean string that can be used on sourcing platforms like
# LinkedIn or job boards.
ROLE_REFINEMENT_TEMPLATE: str = (
    "You are a recruitment assistant. Your job is to refine the role "
    "definition and produce inclusive Boolean search strings to find "
    "candidates.\n"
    "Role title: {role_title}\n"
    "Location: {location}\n"
    "Seniority: {seniority}\n"
    "Must‑have skills: {must_have}\n"
    "Nice‑to‑have skills: {nice_to_have}\n\n"
    "Suggest alternate titles and generate a Boolean search string "
    "covering the role and key skills."
)

# Template for drafting an inclusive job description.  The template
# takes role details and generates a structured JD including
# responsibilities, requirements, benefits and an inclusion statement.
INCLUSIVE_JD_TEMPLATE: str = (
    "You are drafting a bias‑free, inclusive job ad.  Use clear, neutral "
    "language and avoid gender coded terms.  Reflect the company's brand "
    "tone when provided.\n"
    "Role: {role_title}\n"
    "Location: {location}\n"
    "Seniority: {seniority}\n"
    "Responsibilities: {responsibilities}\n"
    "Requirements: {requirements}\n"
    "Benefits: {benefits}\n"
    "Brand tone: {brand_tone}\n\n"
    "Produce a job advertisement with sections for Summary, "
    "Responsibilities, Requirements, Benefits and an Inclusion Statement."
)

# Template for personalised outreach messages.  This template uses the
# candidate's name (optional), the role and top skills, a value
# proposition and a link to the JD.  It should generate one or two
# succinct outreach messages.
OUTREACH_MESSAGE_TEMPLATE: str = (
    "You are writing a recruitment outreach message.  Keep it short, "
    "specific and respectful.  If a candidate name is provided, use it.\n"
    "Candidate name: {candidate_name}\n"
    "Role: {role_title}\n"
    "Top skills: {top_skills}\n"
    "Value proposition: {value_proposition}\n"
    "Job description link: {jd_link}\n"
    "Tone: {tone}\n\n"
    "Generate two outreach message variants with subject lines and "
    "calls to action.  Include an opt‑out sentence if emailing."
)

# Template for sourcing and talent mapping.  This template outlines a
# light-weight sourcing plan based on the role, location, industry
# domain and must-have skills.
SOURCING_PLAN_TEMPLATE: str = (
    "You are creating a sourcing plan and market map outline.\n"
    "Role: {role_title}\n"
    "Location: {location}\n"
    "Industry/domain: {industry}\n"
    "Must‑have skills: {must_have}\n\n"
    "Suggest relevant channels (e.g., LinkedIn, communities, meetups), "
    "synonyms for titles, and key employers.  Provide the output as a "
    "bullet list or simple table ready for a spreadsheet."
)

# Template for interview guides and scorecards.  The template takes
# role context and desired competencies and produces structured
# questions and rubrics.
INTERVIEW_GUIDE_TEMPLATE: str = (
    "You are generating an interview guide and scorecard.\n"
    "Role: {role_title}\n"
    "Seniority: {seniority}\n"
    "Competencies to assess: {competencies}\n"
    "Interview stages: {stages}\n\n"
    "Suggest a balanced mix of technical and behavioural questions "
    "mapped to the competencies.  Provide a rubric for scoring (1–5) "
    "with space for evidence.  Ensure fairness and accessibility."
)

# Template for task triage and daily digest.  This template summarises
# open roles, candidate stages, pending feedback and upcoming
# interviews.
TASK_TRIAGE_TEMPLATE: str = (
    "You are summarising the recruiting tasks and next actions for the day.\n"
    "Open roles: {open_roles}\n"
    "Candidate stages: {candidate_stages}\n"
    "Pending feedback: {pending_feedback}\n"
    "Upcoming interviews: {upcoming_interviews}\n\n"
    "Provide a prioritised task list and quick reminders.  Ask the user "
    "before scheduling or sending messages."
)

# Template for offer and onboarding handover.  This template takes
# candidate and role details and outputs a concise checklist of steps
# required to complete the offer and onboarding process.
OFFER_HANDOVER_TEMPLATE: str = (
    "You are preparing an offer and onboarding handover.\n"
    "Role: {role_title}\n"
    "Candidate: {candidate_name}\n"
    "Start date: {start_date}\n"
    "Location: {location}\n"
    "Onboarding SOPs: {onboarding_sops}\n\n"
    "Generate a checklist of tasks: offer approval, letter sending, "
    "background checks, equipment and account setup, and day‑one agenda.  "
    "Keep automation light and ensure human approval where required."
)

# Template for candidate profile summarisation.  This template takes
# candidate CV text and role requirements and produces a concise,
# bias‑reduced summary highlighting key skills and fit.
CANDIDATE_SUMMARY_TEMPLATE: str = (
    "You are summarising candidate profiles into bias‑reduced briefs.\n"
    "Candidate CV: {candidate_cv}\n"
    "Role requirements: {role_requirements}\n\n"
    "Extract key achievements, skills and role fit notes.  Remove names, "
    "age and gender.  Present the summary in a consistent format."
)

# Template for labor market insights and salary benchmarks.  This
# template is used once the knowledge base or an external dataset is
# integrated.  It expects the role, location and seniority, and
# outputs typical salary ranges and market demand signals.
MARKET_INSIGHTS_TEMPLATE: str = (
    "You are providing labor market insights and salary benchmarks.\n"
    "Role: {role_title}\n"
    "Location: {location}\n"
    "Seniority: {seniority}\n\n"
    "Retrieve typical salary ranges, demand signals and assumptions.  "
    "State the data source and the recency of the information."
)

def get_templates() -> Dict[str, str]:
    """Return a mapping of function names to their templates.

    This helper is useful for loading all templates at once.  The keys
    correspond to the handler names in `handlers.py`.
    """
    return {
        "role_refinement": ROLE_REFINEMENT_TEMPLATE,
        "inclusive_jd": INCLUSIVE_JD_TEMPLATE,
        "outreach_message": OUTREACH_MESSAGE_TEMPLATE,
        "sourcing_plan": SOURCING_PLAN_TEMPLATE,
        "interview_guide": INTERVIEW_GUIDE_TEMPLATE,
        "task_triage": TASK_TRIAGE_TEMPLATE,
        "offer_handover": OFFER_HANDOVER_TEMPLATE,
        "candidate_summary": CANDIDATE_SUMMARY_TEMPLATE,
        "market_insights": MARKET_INSIGHTS_TEMPLATE,
    }
