from app.services.neverbounce_service import NeverBounceService
from app.services.hunter_service import HunterService
from app.services.gemini_service import GeminiService

from app.utils.email_utils import extract_domain


class VerificationAgent:

    def __init__(self):

        self.nb = NeverBounceService()

        self.hunter = HunterService()

        self.llm = GeminiService()

    def run(self, state):

        lead = state["lead"]

        email = lead["Email"]

        verification = self.nb.verify(email)

        verified = verification["result"] == "valid"

        domain = extract_domain(email)

        company_data = self.hunter.search_company(domain)

        prompt = f"""
You are a CRM enrichment assistant.

Lead:

{lead}

Hunter Result:

{company_data}

Return ONLY JSON.

{{
"company":"",
"industry":"",
"buyer_persona":"",
"confidence":95,
"notes":""
}}
"""

        enrichment = self.llm.generate_json(prompt)

        state["verification"] = {

            "verified": verified,

            **enrichment

        }

        return state