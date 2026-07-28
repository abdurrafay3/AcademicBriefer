from langchain_core.messages import HumanMessage, SystemMessage
from backend.schemas.email import EmailDigest
from backend.services.email.email_scraper import get_email_context
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import logging

load_dotenv()  # Load environment variables from .env file

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def email_agent():
    """Produces the morning briefing"""
    email_context = get_email_context()
    system_prompt = """You are an academic assistant.
    Analyze the following emails.

    Only include:

    1. Deadlines
    2. Course-related announcements
    3. Scholarships
    4. Internships
    5. Career opportunities
    6. Academic regulations
    7. Workshops worth attending
    8. Important personal achievements

    Ignore:

    - newsletters
    - marketing
    - repetitive event calendars
    - unsubscribe notices
    - email signatures
    """
    system_message = SystemMessage(content=system_prompt)
    human_message = HumanMessage(content=email_context)
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0, max_tokens=2000)
    structured_llm = llm.with_structured_output(EmailDigest)
    briefing = structured_llm.invoke([system_message, human_message])
    logger.info("Email briefing generated successfully.")
    return briefing


if __name__ == "__main__":
    digest = email_agent()
    print(digest.model_dump_json(indent=2))




