"""
handlers.py

This module defines the `ScoutAgent` class, which acts as the core
conversation handler and orchestrator for the Scout recruitment agent.
The agent maintains a chat history, determines the user's intent and
routes requests to the appropriate handler function.  Each handler
uses a prompt template defined in `prompt_templates.py` and returns
the final formatted prompt.  In a production setting these
handlers would invoke a language model with the template and
parameters, but here they simply return the templated string for
testing and demonstration purposes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Callable, Optional
import re

from .prompt_templates import get_templates


@dataclass
class Message:
    """A single chat message with a role and content."""

    role: str  # 'user' or 'assistant'
    content: str


class ScoutAgent:
    """Core conversation handler for the Scout recruitment agent.

    The agent maintains a history of messages and routes incoming
    user requests to the appropriate function handler.  Each handler
    accepts a parameter dictionary and returns a string that
    represents the prompt that would be sent to a language model.  In
    future iterations these handlers could call an LLM API with
    optional tool usage.
    """

    def __init__(self) -> None:
        self.history: List[Message] = []
        self.templates: Dict[str, str] = get_templates()
        # Mapping from intent names to handler methods
        self.handlers: Dict[str, Callable[[Dict[str, str]], str]] = {
            "role_refinement": self.handle_role_refinement,
            "inclusive_jd": self.handle_inclusive_jd,
            "outreach_message": self.handle_outreach_message,
            "sourcing_plan": self.handle_sourcing_plan,
            "interview_guide": self.handle_interview_guide,
            "task_triage": self.handle_task_triage,
            "offer_handover": self.handle_offer_handover,
            "candidate_summary": self.handle_candidate_summary,
            "market_insights": self.handle_market_insights,
        }

    def add_message(self, role: str, content: str) -> None:
        """Append a message to the chat history."""
        self.history.append(Message(role=role, content=content))

    def get_intent(self, message: str) -> Optional[str]:
        """Determine user intent based on simple keyword matching.

        This function returns the name of the handler function to call.
        It uses heuristic rules for demonstration purposes.  In a
        production system, intent detection would be replaced with
        classification via an LLM or rule engine.
        """
        msg_lower = message.lower()
        # Keyword to handler mapping; order matters for specificity
        patterns = [
            (r"\b(boolean|search|role refinement)\b", "role_refinement"),
            (r"\b(job description|draft jd|write jd|inclusive jd)\b", "inclusive_jd"),
            (r"\boutreach|message\b", "outreach_message"),
            (r"\bsourcing|market map|channels\b", "sourcing_plan"),
            (r"\binterview guide|scorecard\b", "interview_guide"),
            (r"\btask triage|daily digest\b", "task_triage"),
            (r"\boffer|onboarding\b", "offer_handover"),
            (r"\bsummary|summarise candidate|candidate profile\b", "candidate_summary"),
            (r"\bsalary benchmark|market insight|labor market\b", "market_insights"),
        ]
        for pattern, intent in patterns:
            if re.search(pattern, msg_lower):
                return intent
        return None

    def route_message(self, message: str) -> str:
        """Route the message to the appropriate handler.

        If no intent is matched, the agent responds with a default
        message asking for clarification.  Otherwise, the handler is
        called with parsed parameters.
        """
        intent = self.get_intent(message)
        if not intent:
            return "Sorry, I didn't understand your request. Could you please clarify?"
        # For this skeleton, we expect parameters to be provided in the message
        # in a simple comma-separated list of key=value pairs after a colon.
        # Example: "role refinement: role_title=Data Scientist, location=Melbourne, seniority=Mid"
        params = self.parse_params_from_message(message)
        handler = self.handlers[intent]
        return handler(params)

    def parse_params_from_message(self, message: str) -> Dict[str, str]:
        """Parse key=value pairs from the message into a dictionary.

        This helper looks for the first colon and splits the remainder by
        commas.  It then splits each piece at the equals sign.  Keys and
        values are stripped of whitespace.  If no colon is present, an
        empty dict is returned.  This is a simple parser and does not
        handle quoted values or complex syntax.
        """
        params: Dict[str, str] = {}
        if ":" not in message:
            return params
        _, tail = message.split(":", 1)
        parts = tail.split(",")
        for part in parts:
            if "=" in part:
                key, value = part.split("=", 1)
                params[key.strip()] = value.strip()
        return params

    # Handler implementations.  Each handler fills in the template with
    # provided parameters or sensible defaults.  If required parameters
    # are missing, the handler will use placeholder values and prompt
    # the user to provide the missing information in a real system.

    def handle_role_refinement(self, params: Dict[str, str]) -> str:
        template = self.templates["role_refinement"]
        role_title = params.get("role_title", "[role title]")
        location = params.get("location", "[location]")
        seniority = params.get("seniority", "[seniority]")
        must_have = params.get("must_have", "[must‑have skills]")
        nice_to_have = params.get("nice_to_have", "[nice‑to‑have skills]")
        return template.format(
            role_title=role_title,
            location=location,
            seniority=seniority,
            must_have=must_have,
            nice_to_have=nice_to_have,
        )

    def handle_inclusive_jd(self, params: Dict[str, str]) -> str:
        template = self.templates["inclusive_jd"]
        role_title = params.get("role_title", "[role title]")
        location = params.get("location", "[location]")
        seniority = params.get("seniority", "[seniority]")
        responsibilities = params.get("responsibilities", "[responsibilities]")
        requirements = params.get("requirements", "[requirements]")
        benefits = params.get("benefits", "[benefits]")
        brand_tone = params.get("brand_tone", "neutral")
        return template.format(
            role_title=role_title,
            location=location,
            seniority=seniority,
            responsibilities=responsibilities,
            requirements=requirements,
            benefits=benefits,
            brand_tone=brand_tone,
        )

    def handle_outreach_message(self, params: Dict[str, str]) -> str:
        template = self.templates["outreach_message"]
        candidate_name = params.get("candidate_name", "[candidate]")
        role_title = params.get("role_title", "[role title]")
        top_skills = params.get("top_skills", "[top skills]")
        value_proposition = params.get("value_proposition", "[value proposition]")
        jd_link = params.get("jd_link", "[JD link]")
        tone = params.get("tone", "professional")
        return template.format(
            candidate_name=candidate_name,
            role_title=role_title,
            top_skills=top_skills,
            value_proposition=value_proposition,
            jd_link=jd_link,
            tone=tone,
        )

    def handle_sourcing_plan(self, params: Dict[str, str]) -> str:
        template = self.templates["sourcing_plan"]
        role_title = params.get("role_title", "[role title]")
        location = params.get("location", "[location]")
        industry = params.get("industry", "[industry/domain]")
        must_have = params.get("must_have", "[must‑have skills]")
        return template.format(
            role_title=role_title,
            location=location,
            industry=industry,
            must_have=must_have,
        )

    def handle_interview_guide(self, params: Dict[str, str]) -> str:
        template = self.templates["interview_guide"]
        role_title = params.get("role_title", "[role title]")
        seniority = params.get("seniority", "[seniority]")
        competencies = params.get("competencies", "[competencies]")
        stages = params.get("stages", "phone, technical, panel")
        return template.format(
            role_title=role_title,
            seniority=seniority,
            competencies=competencies,
            stages=stages,
        )

    def handle_task_triage(self, params: Dict[str, str]) -> str:
        template = self.templates["task_triage"]
        open_roles = params.get("open_roles", "[open roles]")
        candidate_stages = params.get("candidate_stages", "[candidate stages]")
        pending_feedback = params.get("pending_feedback", "[pending feedback]")
        upcoming_interviews = params.get("upcoming_interviews", "[upcoming interviews]")
        return template.format(
            open_roles=open_roles,
            candidate_stages=candidate_stages,
            pending_feedback=pending_feedback,
            upcoming_interviews=upcoming_interviews,
        )

    def handle_offer_handover(self, params: Dict[str, str]) -> str:
        template = self.templates["offer_handover"]
        role_title = params.get("role_title", "[role title]")
        candidate_name = params.get("candidate_name", "[candidate]")
        start_date = params.get("start_date", "[start date]")
        location = params.get("location", "[location]")
        onboarding_sops = params.get("onboarding_sops", "[onboarding SOPs]")
        return template.format(
            role_title=role_title,
            candidate_name=candidate_name,
            start_date=start_date,
            location=location,
            onboarding_sops=onboarding_sops,
        )

    def handle_candidate_summary(self, params: Dict[str, str]) -> str:
        template = self.templates["candidate_summary"]
        candidate_cv = params.get("candidate_cv", "[candidate CV text]")
        role_requirements = params.get("role_requirements", "[role requirements]")
        return template.format(
            candidate_cv=candidate_cv,
            role_requirements=role_requirements,
        )

    def handle_market_insights(self, params: Dict[str, str]) -> str:
        template = self.templates["market_insights"]
        role_title = params.get("role_title", "[role title]")
        location = params.get("location", "[location]")
        seniority = params.get("seniority", "[seniority]")
        return template.format(
            role_title=role_title,
            location=location,
            seniority=seniority,
        )
