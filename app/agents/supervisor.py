import json

from app.services.gemini_service import GeminiService
from app.services.google_sheet_service import GoogleSheetService


class SupervisorAgent:

    def __init__(self):

        self.llm = GeminiService()

        self.sheet = GoogleSheetService()

    def run(self, state):

        lead = state["lead"]

        prompt = f"""

You are an expert CRM sales analyst.

Score this lead from 1-100.

Return ONLY JSON.

{{
"priority":95,

"reason":"Short reason"
}}

Lead

Name:
{lead["Lead Name"]}

Company:
{lead["Company"]}

Industry:
{lead["Industry"]}

"""

        response = self.llm.generate_json(prompt)

        if not response or "priority" not in response:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to score lead priority using Gemini for lead {state['lead_id']}. Defaulting to 50.")
            priority = 50
        else:
            priority = response["priority"]

        self.sheet.update_by_lead_id(

            state["lead_id"],

            "Lead Priority",

            priority

        )

        state["priority"] = priority

        return state