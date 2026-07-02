"""
workflow.py

LangGraph workflow for AI Sales CRM.

Current Flow:

START
    │
    ▼
Supervisor Agent
    │
    ▼
Verification Agent
    │
    ▼
Outreach Agent
    │
    ▼
END
"""

import logging

from langgraph.graph import StateGraph, START, END

from app.graph.state import CRMState

from app.agents.supervisor import SupervisorAgent
from app.agents.verifier import VerificationAgent
from app.agents.outreach import OutreachAgent

logger = logging.getLogger(__name__)


# -------------------------------------------------------
# Initialize Agents
# -------------------------------------------------------

supervisor_agent = SupervisorAgent()
verification_agent = VerificationAgent()
outreach_agent = OutreachAgent()


# -------------------------------------------------------
# Wrapper Functions
# -------------------------------------------------------

def supervisor_node(state: CRMState) -> CRMState:
    logger.info("Running Supervisor Agent...")
    return supervisor_agent.run(state)


def verification_node(state: CRMState) -> CRMState:
    logger.info("Running Verification Agent...")
    return verification_agent.run(state)


def outreach_node(state: CRMState) -> CRMState:
    logger.info("Running Outreach Agent...")
    return outreach_agent.run(state)


# -------------------------------------------------------
# Build Workflow
# -------------------------------------------------------

builder = StateGraph(CRMState)

# Nodes
builder.add_node("supervisor", supervisor_node)
builder.add_node("verification", verification_node)
builder.add_node("outreach", outreach_node)

# Flow
builder.add_edge(START, "supervisor")
builder.add_edge("supervisor", "verification")
builder.add_edge("verification", "outreach")
builder.add_edge("outreach", END)

# Compile
crm_workflow = builder.compile()


# -------------------------------------------------------
# Helper Function
# -------------------------------------------------------

def run_workflow(lead: dict):
    """
    Execute the LangGraph workflow for a single lead.
    """

    state: CRMState = {
        "lead_id": lead["Lead ID"],
        "lead": lead,

        "priority": None,
        "verification": None,
        "enrichment": None,

        "outreach_message": None,
        "email_sent": False,

        "response": None,
        "classification": None,

        "report": None,

        "status": "Pending"
    }

    return crm_workflow.invoke(state)