import logging

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

            logger.info(
                f"Processing Lead: {lead.get('Lead Name')}"
            )

            run_workflow(lead)

            logger.info(
                f"Completed Lead: {lead.get('Lead Name')}"
            )

        except Exception as e:

            logger.exception(e)


scheduler.add_job(
    process_pending,
    trigger="interval",
    minutes=1,
    id="lead_scheduler",
    replace_existing=True
)