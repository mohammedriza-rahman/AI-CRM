import google.generativeai as genai
import json
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class GeminiService:

    def __init__(self):

        genai.configure(api_key=settings.GEMINI_API_KEY)

        self.model = genai.GenerativeModel(
            "gemini-2.5-flash"
        )

    def generate(self, prompt):

        try:

            response = self.model.generate_content(prompt)

            return response.text

        except Exception as e:

            logger.error(e)

            return None

    def generate_json(self, prompt):

        try:

            response = self.model.generate_content(prompt)

            text = response.text.replace("```json", "").replace("```", "").strip()

            return json.loads(text)

        except Exception as e:

            logger.error(e)

            return None