import neverbounce_sdk

from app.config import settings


class NeverBounceService:

    def __init__(self):

        self.client = neverbounce_sdk.client(
            api_key=settings.NEVERBOUNCE_API_KEY
        )

    def verify(self, email):

        result = self.client.single_check(
            email=email,
            address_info=True,
            credits_info=True,
            timeout=10
        )

        return result