import logging
from datetime import datetime, timezone

from backend.ai.briefing_graph import generate_briefing_summary
from backend.schemas.briefing import BriefingResponse
from backend.services.calendar.calendar import add_assignments_to_calendar
from backend.services.courses.canvas_scraper import get_canvas_assignments
from backend.services.email.email_scraper import get_emails

logger = logging.getLogger(__name__)


class Orchestrator:
    def __init__(self, canvas_scraper=get_canvas_assignments, email_scraper=get_emails):
        self.canvas_scraper = canvas_scraper
        self.email_scraper = email_scraper

    def orchestrate(self) -> BriefingResponse:
        logger.info("Fetching emails...")
        try:
            emails = self.email_scraper()
            email_status = "success"
        except Exception:
            logger.exception("Failed to fetch emails")
            emails = []
            email_status = "failed"

        logger.info("Scraping Canvas assignments...")
        try:
            assignments = self.canvas_scraper()
            canvas_status = "success"
        except Exception:
            logger.exception("Failed to scrape Canvas")
            assignments = []
            canvas_status = "failed"

        if assignments:
            logger.info("Uploading assignments to calendar...")
            try:
                add_assignments_to_calendar(assignments)
                calendar_status = "success"
            except Exception:
                logger.exception("Failed to sync assignments to calendar")
                calendar_status = "failed"
        else:
            calendar_status = "skipped"

        logger.info("Generating briefing summary...")
        try:
            summary = generate_briefing_summary(emails, assignments)
        except Exception:
            logger.exception("Failed to generate briefing summary")
            summary = None

        return BriefingResponse(
            generated_at=datetime.now(timezone.utc).isoformat(),
            email_status=email_status,
            canvas_status=canvas_status,
            calendar_status=calendar_status,
            emails_scraped=len(emails),
            assignments=assignments,
            summary=summary,
        )
