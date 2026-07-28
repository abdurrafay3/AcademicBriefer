import logging

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from backend.schemas.email import Email, EmailDigest
from backend.services.courses.canvas_scraper import Assignment, format_canvas_context
from backend.services.email.email_scraper import format_email_context

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an academic assistant preparing a morning briefing for a student.

You are given the student's recent emails and the assignments scraped from Canvas
(the Canvas assignments have already been added to the student's calendar).

Only include:

1. Deadlines (from emails and Canvas assignments)
2. Course-related announcements
3. Scholarships
4. Internships
5. Career opportunities
6. Academic regulations
7. Workshops worth attending
8. Important personal achievements
9. Events

Ignore:

- newsletters
- marketing
- repetitive event calendars
- unsubscribe notices
- email signatures

Canvas assignments are already scheduled on the calendar, so list them as deadlines
but do not duplicate an item that appears in both emails and Canvas.
"""


def generate_briefing_summary(emails: list[Email], assignments: list[Assignment]) -> EmailDigest:
    """Summarizes emails and Canvas assignments into a single digest of what matters."""
    context = (
        "=== EMAILS ===\n"
        f"{format_email_context(emails)}\n"
        "=== CANVAS ASSIGNMENTS ===\n"
        f"{format_canvas_context(assignments)}"
    )
    llm = ChatOpenAI(model="gpt-4o", temperature=0, max_tokens=2000)
    structured_llm = llm.with_structured_output(EmailDigest)
    digest = structured_llm.invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=context)])
    logger.info("Briefing summary generated successfully.")
    return digest
