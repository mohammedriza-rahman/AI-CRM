from pathlib import Path

from app.services.gemini_service import GeminiService
from app.services.smtp_service import SMTPService


class OutreachAgent:

    def __init__(self):

        self.llm = GeminiService()

        self.smtp = SMTPService()

        self.prompt = Path(
            "app/prompts/outreach.txt"
        ).read_text()

    def run(self, state):

        lead = state["lead"]

        prompt = self.prompt.format(

            lead_name=lead["Lead Name"],

            company=lead["Company"],

            industry=lead["Industry"],

            buyer_persona=state["verification"]["buyer_persona"]

        )

        email_body = self.llm.generate(prompt)

        success = self.smtp.send_email(

            recipient=lead["Email"],

            subject="Let's Discuss AI Solutions",

            body=email_body

        )

        state["outreach_message"] = email_body

        state["email_sent"] = success

        return state