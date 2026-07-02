from pydantic import BaseModel


class VerificationResult(BaseModel):

    email_verified: bool

    confidence: float

    company: str

    industry: str

    buyer_persona: str

    notes: str