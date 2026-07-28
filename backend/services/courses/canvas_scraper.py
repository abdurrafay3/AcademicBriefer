from datetime import datetime
from typing import Literal
from playwright.sync_api import sync_playwright
from backend.services.email.email_scraper import complete_login
import logging
from pydantic import BaseModel, Field
from backend.color import Color
from zoneinfo import ZoneInfo

class Assignment(BaseModel):
    title: str = Field(..., description="The title of the assignment")
    due_date: datetime | None = Field(..., description="The due date of the assignment")
    description: str = Field(..., description="The description of the assignment")
    max_points: int | None = Field(..., description="The maximum points for the assignment")
    available: str | None = Field(..., description="Whether the assignment is available or not")
    course_id: str | None = Field(..., description="The course ID for the assignment")

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
#.            COMP2611.FINA1303. COMP2012
course_ids = ["67649", "68566", "68100"]

def get_canvas_assignments():
    """This function first logs in to your canvas account and then it fetches the courses and creates the course list. Then for each course it goes to the announcements and fetches/scrapes them"""
    complete_login()
    HK = ZoneInfo("Asia/Hong_Kong")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state="state.json")
        page = context.new_page()
        logger.info(f"{Color.BLUE}Logging in to Canvas...{Color.RESET}")
        page.goto("https://canvas.ust.hk/courses")
        assignments_list = []
        for id in course_ids:
            try:
                page.goto(f"https://canvas.ust.hk/courses/{id}/assignments")
                page.wait_for_load_state("networkidle")
                logger.info(f"{Color.BLUE}Scraping announcements for course: {id}{Color.RESET}")
                page.wait_for_timeout(5000)
                assignments = page.locator("li.assignment")
                count = assignments.count()
                for i in range(count):
                    assignment = assignments.nth(i)
                    title = assignment.locator(".ig-title").inner_text()
                    locator = assignment.locator(".assignment-date-available")
                    date_available = None # optional 
                    due_date = None # optional 
                    if locator.count() > 0:
                        date_available = locator.inner_text()
                    due_locator = assignment.locator(".assignment-date-due")
                    lines = None
                    if due_locator.count() > 0:
                        due_date = due_locator.inner_text()
                        lines = due_date.splitlines()
                    date_str = lines[-1].strip() if lines else None
                    due_str = f"{date_str} 2026"
                    if due_date is not None:
                        due_date = datetime.strptime(due_str, "%b %d at %I:%M%p %Y")
                        due_date = due_date.replace(tzinfo=HK)
                    score = assignment.locator(".js-score").inner_text()
                    max_points = int(score.split("/")[1].strip().split()[0]) if "/" in score else None
                    our_assignment = Assignment(
                        title=title,
                        due_date=due_date,
                        description="",
                        max_points=max_points,
                        available=date_available,
                        course_id=id
                    )
                    assignments_list.append(our_assignment)
                    logger.info(f"{Color.BLUE}Scraped assignment: {title}, Due Date: {due_date}, Available: {date_available}, Max Points: {max_points}{Color.RESET}")
                # add scraping logic here to extract announcements
            except Exception as e:
                logger.error(f"Error occurred while scraping course {id}: {e}")
                continue
        return assignments_list

if __name__ == "__main__":
    assignments_list = get_canvas_assignments()