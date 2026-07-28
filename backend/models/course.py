import logging
from backend.services.courses.canvas_scraper import get_canvas_assignments

logger = logging.getLogger(__name__)

def get_canvas_digest():
    assignments = get_canvas_assignments()
    filtered_assignments = [assignment for assignment in assignments if assignment.due_date != "N/A"]
    filtered_assignments.sort(key=lambda x: x.due_date) # earliest come first
    return filtered_assignments
