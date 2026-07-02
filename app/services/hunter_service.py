import requests

from app.config import settings


class HunterService:

    BASE_URL = "https://api.hunter.io/v2/domain-search"

    def search_company(self, domain):

        params = {
            "domain": domain,
            "api_key": settings.HUNTER_API_KEY
        }

        response = requests.get(
            self.BASE_URL,
            params=params,
            timeout=30
        )

        if response.status_code == 200:
            return response.json()

        return None