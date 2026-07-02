import logging
from pathlib import Path

from app.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)


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

        if not result:
            logger.warning(f"Response classification failed. Using neutral default.")
            result = {
                "category": "Request More Info",
                "sentiment": "Neutral",
                "summary": "Failed to classify reply (LLM rate limit or error)."
            }

        state["classification"] = result

        return state