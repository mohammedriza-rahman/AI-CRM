import datetime
import logging
from pathlib import Path

from app.services.gemini_service import GeminiService
from app.services.smtp_service import SMTPService
from app.services.google_sheet_service import GoogleSheetService

logger = logging.getLogger(__name__)


class OutreachAgent:

    def __init__(self):

        self.llm = GeminiService()

        self.smtp = SMTPService()

        self.prompt = Path(
            "app/prompts/outreach.txt"
        ).read_text()

        self.sheet = GoogleSheetService()

    def run(self, state):

        lead = state["lead"]

        prompt = self.prompt.format(

            lead_name=lead["Lead Name"],

            company=lead["Company"],

            industry=lead["Industry"],

            buyer_persona=state["verification"]["buyer_persona"]

        )

        email_body = self.llm.generate(prompt)

        # Only send email if the email is verified and email body is successfully generated
        is_verified = state.get("verification", {}).get("verified", False)
        if is_verified and email_body:
            success = self.smtp.send_email(

                recipient=lead["Email"],

                subject="Let's Discuss AI Solutions",

                body=email_body

            )
        else:
            success = False
            if not email_body:
                logger.error(f"Skipping email outreach to {lead['Email']} because outreach message generation failed (possibly due to API rate limit).")
            else:
                logger.info(f"Skipping email outreach to {lead['Email']} as verification failed.")

        state["outreach_message"] = email_body

        state["email_sent"] = success

        # Update Google Sheet
        self.sheet.update_by_lead_id(state["lead_id"], "AI Suggested Outreach Message", email_body)
        self.sheet.update_by_lead_id(state["lead_id"], "Email Sent", "Y" if success else "N")
        self.sheet.update_by_lead_id(state["lead_id"], "Processing Status", "Completed")
        self.sheet.update_by_lead_id(
            state["lead_id"], 
            "Last Updated", 
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        return state