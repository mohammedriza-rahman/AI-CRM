from pathlib import Path

from app.services.gemini_service import GeminiService


class ReportGenerator:

    def __init__(self):

        self.llm = GeminiService()

        self.prompt = Path(
            "app/prompts/report.txt"
        ).read_text()

    def run(self, state):

        prompt = self.prompt.format(

            lead=state["lead"],

            verification=state["verification"],

            classification=state["classification"]

        )

        report = self.llm.generate(
            prompt
        )

        state["report"] = report

        return state