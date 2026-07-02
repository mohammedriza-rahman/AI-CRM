from typing import TypedDict, Optional


class CRMState(TypedDict):

    lead_id: str

    lead: dict

    priority: Optional[int]

    verification: Optional[dict]

    enrichment: Optional[dict]

    outreach_message: Optional[str]

    email_sent: Optional[bool]

    response: Optional[str]

    classification: Optional[dict]

    report: Optional[str]

    status: str