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