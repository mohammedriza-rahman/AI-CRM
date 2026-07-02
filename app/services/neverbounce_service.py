import neverbounce_sdk
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class NeverBounceService:

    def __init__(self):

        self.client = neverbounce_sdk.client(
            api_key=settings.NEVERBOUNCE_API_KEY
        )

    def verify(self, email):

        try:
            result = self.client.single_check(
                email=email,
                address_info=True,
                credits_info=True,
                timeout=10
            )
            return result
        except Exception as e:
            logger.warning(f"NeverBounce single_check failed for {email}: {e}")
            return {"result": "unknown", "error": str(e)}