import logging
import re

from apscheduler.schedulers.background import BackgroundScheduler

from app.services.google_sheet_service import GoogleSheetService
from app.graph.workflow import run_workflow

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def process_pending():

    logger.info("Checking Google Sheets for pending leads...")

    service = GoogleSheetService()

    leads = service.get_pending_leads()

    logger.info(f"Found {len(leads)} pending leads.")

    for lead in leads:

        try:
            lead_id = lead.get("Lead ID")
            logger.info(
                f"Processing Lead: {lead.get('Lead Name')} (ID: {lead_id})"
            )

            # Mark as Processing immediately to avoid double execution
            service.update_by_lead_id(lead_id, "Processing Status", "Processing")

            run_workflow(lead)

            logger.info(
                f"Completed Lead: {lead.get('Lead Name')}"
            )

        except Exception as e:

            logger.exception(e)


def check_responses():
    logger.info("Checking Google Sheets and email inbox for new responses...")
    try:
        from app.services.imap_service import IMAPService
        from app.agents.response_classifier import ResponseClassifier
        from app.services.google_sheet_service import GoogleSheetService
        
        imap = IMAPService()
        emails = imap.get_unread_emails()
        if not emails:
            logger.info("No new email responses found.")
            return
            
        logger.info(f"Found {len(emails)} unread emails. Checking matches...")
        sheet_service = GoogleSheetService()
        leads = sheet_service.get_all_leads()
        classifier = ResponseClassifier()
        
        for email_msg in emails:
            sender = email_msg.get("sender", "")
            email_match = re.search(r'[\w\.-]+@[\w\.-]+', sender)
            if not email_match:
                continue
            sender_email = email_match.group(0).lower().strip()
            
            # Find matching lead
            matched_lead = None
            for lead in leads:
                lead_email = str(lead.get("Email", "")).lower().strip()
                if lead_email == sender_email:
                    matched_lead = lead
                    break
                    
            if matched_lead:
                lead_id = matched_lead.get("Lead ID")
                logger.info(f"Processing reply for lead: {matched_lead.get('Lead Name')} ({sender_email})")
                
                # Classify reply body
                state = {
                    "response": email_msg.get("body", ""),
                    "classification": None
                }
                classified_state = classifier.run(state)
                result = classified_state["classification"]
                
                if result:
                    category = result.get("category", "No Response")
                    sentiment = result.get("sentiment", "Neutral")
                    summary = result.get("summary", "")
                    
                    # Update lead record
                    sheet_service.update_by_lead_id(lead_id, "Response Status", category)
                    sheet_service.update_by_lead_id(lead_id, "Sentiment", sentiment)
                    current_notes = matched_lead.get("Notes", "")
                    new_notes = f"{current_notes} | Response: {summary}" if current_notes else f"Response: {summary}"
                    sheet_service.update_by_lead_id(lead_id, "Notes", new_notes)
                    
                    logger.info(f"Classified lead {lead_id} response as {category} ({sentiment})")
    except Exception as e:
        logger.error(f"Error checking responses: {e}", exc_info=True)


scheduler.add_job(
    process_pending,
    trigger="interval",
    minutes=1,
    id="lead_scheduler",
    replace_existing=True
)

scheduler.add_job(
    check_responses,
    trigger="interval",
    minutes=1,
    id="response_scheduler",
    replace_existing=True
)