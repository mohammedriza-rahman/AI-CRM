from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

from app.scheduler import scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Start background scheduler when FastAPI starts
    and stop it gracefully on shutdown.
    """
    logger.info("==========================================")
    logger.info("Starting AI Sales CRM Backend...")
    logger.info("Starting APScheduler...")
    logger.info("==========================================")

    scheduler.start()

    yield

    logger.info("==========================================")
    logger.info("Stopping APScheduler...")
    logger.info("Shutting down AI Sales CRM Backend...")
    logger.info("==========================================")

    scheduler.shutdown()


app = FastAPI(
    title="AI Sales CRM Backend",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
def home():
    return {
        "status": "running",
        "application": "AI Sales CRM Backend",
        "scheduler": scheduler.running
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/scheduler")
def scheduler_status():
    """
    Check whether APScheduler is running.
    """
    return {
        "running": scheduler.running
    }


@app.post("/process-pending")
def trigger_processing():
    """
    Manually trigger processing of pending leads.
    """
    from app.scheduler import process_pending
    process_pending()
    return {
        "status": "success",
        "message": "Processing of pending leads triggered."
    }


@app.post("/check-responses")
def trigger_response_check():
    """
    Manually trigger email response checking and classification.
    """
    from app.scheduler import check_responses
    check_responses()
    return {
        "status": "success",
        "message": "Response classification check triggered."
    }


@app.post("/report")
def generate_campaign_report():
    """
    Manually trigger campaign report generation and sending.
    """
    from app.agents.report_generator import ReportGenerator
    generator = ReportGenerator()
    report_content = generator.generate_campaign_report()
    return {
        "status": "success",
        "report": report_content
    }