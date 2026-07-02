from pathlib import Path

from app.services.gemini_service import GeminiService


class ResponseClassifier:

    def __init__(self):

        self.llm = GeminiService()

        self.prompt = Path(
            "app/prompts/response_classifier.txt"
        ).read_text()

    def run(self, state):

        response = state["response"]

        prompt = self.prompt.format(
            response=response
        )

        result = self.llm.generate_json(
            prompt
        )

        state["classification"] = result

        return state