import logging
from app.services.neverbounce_service import NeverBounceService
from app.services.hunter_service import HunterService
from app.services.gemini_service import GeminiService
from app.services.google_sheet_service import GoogleSheetService

from app.utils.email_utils import extract_domain

logger = logging.getLogger(__name__)


class VerificationAgent:

    def __init__(self):

        self.nb = NeverBounceService()

        self.hunter = HunterService()

        self.llm = GeminiService()

        self.sheet = GoogleSheetService()

    def run(self, state):

        lead = state["lead"]

        email = lead["Email"]

        verification = self.nb.verify(email)

        verified = verification.get("result") == "valid"

        # Fallback check if NeverBounce returned unknown or failed
        if verification.get("result") == "unknown":
            try:
                from email_validator import validate_email, EmailNotValidError
                validate_email(email, check_deliverability=True)
                verified = True
            except EmailNotValidError:
                verified = False
            except Exception:
                import re
                verified = bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

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

        if not enrichment:
            logger.warning(f"Data enrichment failed for lead {state['lead_id']}. Using defaults.")
            enrichment = {
                "company": lead.get("Company", ""),
                "industry": lead.get("Industry", ""),
                "buyer_persona": "General Buyer",
                "confidence": 0,
                "notes": "Data enrichment failed (API error or rate limit)."
            }

        state["verification"] = {

            "verified": verified,

            **enrichment

        }

        # Update Google Sheets
        self.sheet.update_by_lead_id(state["lead_id"], "Email Verified", "Y" if verified else "N")
        
        company = lead.get("Company", "")
        if not company:
            company = enrichment.get("company", "")
            if company:
                self.sheet.update_by_lead_id(state["lead_id"], "Company", company)
                state["lead"]["Company"] = company

        industry = lead.get("Industry", "")
        if not industry:
            industry = enrichment.get("industry", "")
            if industry:
                self.sheet.update_by_lead_id(state["lead_id"], "Industry", industry)
                state["lead"]["Industry"] = industry

        buyer_persona = enrichment.get("buyer_persona", "")
        if buyer_persona:
            self.sheet.update_by_lead_id(state["lead_id"], "Buyer Persona", buyer_persona)
            
        notes = f"Confidence: {enrichment.get('confidence')}. {enrichment.get('notes', '')}"
        self.sheet.update_by_lead_id(state["lead_id"], "Notes", notes)

        return state