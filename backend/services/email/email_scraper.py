import sys
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from backend.schemas.email import NotLoggedInException, Email
from bs4 import BeautifulSoup

def first_login():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://outlook.office.com/mail/inbox")
        # Perform actions on the page
        page.fill("input[type='email']", "your-email")
        page.click("input[type='submit']")
        page.wait_for_selector("input[type='password']", state="visible")

        page.fill("input[type='password']", "your-password")
        page.click("input[type='submit']")
        try:
            page.get_by_role("button", name="Yes").click(timeout=5000)  # Click "Yes" if prompted to stay signed in
        except:
            print("No 'Stay signed in?' prompt appeared.")
        input("Press enter if you have completed the login process and are on the inbox page...")
        context.storage_state(path="state.json")
        browser.close()

def login():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        try:
            context = browser.new_context(storage_state="state.json")
        except:
            raise NotLoggedInException("User is not logged in. Please run first_login() to log in.")
        page = context.new_page()
        page.goto("https://outlook.office.com/mail/inbox")
        try:
            page.get_by_text("Inbox").first.wait_for(timeout=5000)  # Wait for the "Inbox" text to appear
        except:
            raise NotLoggedInException("User is not logged in. Please run first_login() to log in.")
        browser.close()

def get_emails() -> list[Email]:
    """This function fetches the latest 15 emails from the user's Outlook inbox and returns them as a list of Email objects."""
    complete_login() # first we login to outlook
    # we assume that state is there 
    emails = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context(storage_state="state.json")
        page = context.new_page()
        page.goto("https://outlook.office.com/mail/inbox")
        page.get_by_role("option").first.wait_for(timeout=5000)  # Wait for the first email to appear
        seen_keys = set()
        while len(emails) <= 15:
            emails_list = page.get_by_role("option").all()
            for i in range(len(emails_list)):
                emails_list[i].click()
                try:
                    page.locator('[data-test-id="mailMessageBodyContainer"]').first.wait_for(timeout=0)
                except PlaywrightTimeoutError:
                    print("Email body not found for this email. Skipping.")
                    continue
                body = page.locator('[data-test-id="mailMessageBodyContainer"]')
                if body.count() == 0:
                    print("No email body found for this email.")
                    continue
                html = body.first.inner_html()
                soup = BeautifulSoup(html, 'html.parser')
                email_text = soup.get_text()
                message = page.locator('[id="ConversationReadingPaneContainer"]').first
                title = get_text_when_ready(message.locator('[id$="_SUBJECT"]').first)
                timestamp = get_text_when_ready(message.locator('[data-testid="SentReceivedSavedTime"]').first)
                sender = get_text_when_ready(message.locator('[id$="_FROM"]').first)
                key=f"{title},{timestamp},{sender}"
                if key not in seen_keys:
                    seen_keys.add(key)
                    emails.append(Email(subject=title, sender=sender, timestamp=timestamp, body=email_text))
            scroller = page.locator('[data-testid="virtuoso-scroller"]')
            scroller.evaluate("scroller => scroller.scrollBy(0,400)")  # Scroll down by 400 pixels
            page.wait_for_timeout(1000)
        
        print(f"Total emails fetched: {len(emails)}")
        print("printing all emails now")
        emails = list(emails)
        for i in range(len(emails)):
            print(f"Email {i + 1}\n {emails[i]}\n\n")
        browser.close()

# data-test-id="mailMessageBodyContainer"
    return emails

def complete_login():
    # first we try normal login
    try:
        login()
    except NotLoggedInException:
        print("User is not logged in. Please run first_login() to log in.")
        first_login()
        login()

# role=heading for email title, and timestamp
# id ending with _SUBJECT for email subject
# id ending with _FROM for email sender
# data-testid="SentReceivedSavedTime" for email timestamp

def debug() -> None:
    """ This function opens outlook and then opens playwright's interactive debug window"""
    complete_login() # first we login to outlook
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context(storage_state="state.json")
        page = context.new_page()
        page.goto("https://outlook.office.com/mail/inbox")
        page.pause()
        browser.close()

def get_text_when_ready(locator, timeout=5000, interval=200):
    """This function waits for a locator to be ready and then returns its inner text."""
    elapsed = 0
    while elapsed < timeout:
        text = locator.inner_text()
        if text:
            return text
        locator.page.wait_for_timeout(interval)  # Wait for 100 milliseconds before checking again
        elapsed += interval
    return locator.inner_text()  # Return whatever text is available after timeout


def format_email_context(emails: list[Email]) -> str:
    return "".join(f"{email.subject}\n{email.sender}\n{email.timestamp}\n{email.body}\n\n" for email in emails)


def get_email_context() -> str:
    emails = get_emails()
    return format_email_context(emails)

if __name__ == "__main__":
   debug()
