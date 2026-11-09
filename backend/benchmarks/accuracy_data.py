"""Synthetic, hand-labeled email inboxes for benchmarking LLM extraction quality.

Each batch simulates one inbox scrape (the unit the real pipeline processes
together into a single EmailDigest). Every signal email carries an `expect`
phrase that must appear (case-insensitive substring) somewhere in the matching
category of the model's output for it to count as a true positive. Noise
emails should never surface in the digest; their `leak_phrase` is checked
against the full serialized output to catch hallucinated/over-inclusive noise.
"""

from dataclasses import dataclass

from backend.schemas.email import Email


@dataclass
class LabeledEmail:
    email: Email
    label: str  # "deadline" | "opportunity" | "event" | "announcement" | "noise"
    expect: str | None = None  # required substring for signal emails
    leak_phrase: str | None = None  # required ABSENCE substring for noise emails


def _e(subject: str, sender: str, body: str) -> Email:
    return Email(subject=subject, sender=sender, timestamp="2026-07-28T08:00:00+08:00", body=body)


BATCHES: list[list[LabeledEmail]] = [
    # Batch 1 - Fall semester kickoff
    [
        LabeledEmail(
            _e(
                "Course Add/Drop Deadline Reminder",
                "registrar@ust.hk",
                "This is a reminder that the deadline to add or drop courses for the Fall semester is September 5th at 11:59pm. No changes will be accepted after this date.",
            ),
            "deadline",
            expect="add/drop",
        ),
        LabeledEmail(
            _e(
                "COMP3711 Assignment 2 Due Soon",
                "comp3711-ta@ust.hk",
                "Assignment 2 for COMP3711 (Design and Analysis of Algorithms) is due September 10th at 11:59pm on Canvas. Late submissions will not be accepted.",
            ),
            "deadline",
            expect="Assignment 2",
        ),
        LabeledEmail(
            _e(
                "Apply Now: Global Excellence Scholarship",
                "scholarships@ust.hk",
                "The Global Excellence Scholarship is now accepting applications from undergraduates with a GPA above 3.5. Applications close September 20th. Award value: HK$50,000.",
            ),
            "opportunity",
            expect="Global Excellence Scholarship",
        ),
        LabeledEmail(
            _e(
                "Summer Internship at Bloomberg - Applications Open",
                "careers@ust.hk",
                "Bloomberg is now recruiting for their Summer 2027 internship program in engineering and quantitative research. Info session and application link inside.",
            ),
            "opportunity",
            expect="Bloomberg",
        ),
        LabeledEmail(
            _e(
                "Guest Lecture: AI in Healthcare - Sept 15",
                "cse-dept@ust.hk",
                "Join us for a guest lecture titled 'AI in Healthcare' by Dr. Wong on September 15th at 4pm in Lecture Theater F. Open to all students.",
            ),
            "event",
            expect="AI in Healthcare",
        ),
        LabeledEmail(
            _e(
                "Career Fair 2026 - Register to Attend",
                "careers@ust.hk",
                "The annual Career Fair will be held on September 18th in the Atrium. Over 80 companies will be attending. Register now to reserve a spot.",
            ),
            "event",
            expect="Career Fair",
        ),
        LabeledEmail(
            _e(
                "COMP3711 Lecture Moved to LTA",
                "comp3711-ta@ust.hk",
                "Please note that this Friday's COMP3711 lecture has been moved from LTB to LTA due to a room conflict.",
            ),
            "announcement",
            expect="LTA",
        ),
        LabeledEmail(
            _e(
                "New Academic Integrity Policy Effective This Semester",
                "provost@ust.hk",
                "A revised Academic Integrity Policy takes effect this semester. All students are required to review the updated guidelines on plagiarism and collaboration.",
            ),
            "announcement",
            expect="Academic Integrity Policy",
        ),
        LabeledEmail(
            _e(
                "50% OFF Textbooks This Week Only!",
                "deals@campusbookstore.com",
                "Huge savings on textbooks, backpacks, and stationery this week only at the Campus Bookstore. Visit us in person or shop online!",
            ),
            "noise",
            leak_phrase="50% OFF Textbooks",
        ),
        LabeledEmail(
            _e(
                "Weekly Campus Newsletter - Issue 42",
                "newsletter@ust.hk",
                "This week: club fair recap, dining hall menu changes, and a photo gallery from orientation week. Read the full newsletter online.",
            ),
            "noise",
            leak_phrase="Weekly Campus Newsletter",
        ),
        LabeledEmail(
            _e(
                "You have unsubscribed from Career Services Digest",
                "no-reply@ust.hk",
                "You have successfully unsubscribed from the Career Services Digest mailing list. You will no longer receive these emails.",
            ),
            "noise",
            leak_phrase="unsubscribed from Career Services",
        ),
        LabeledEmail(
            _e(
                "RE: RE: RE: Group Project Meeting",
                "classmate123@connect.ust.hk",
                "Sounds good, see you then.\n\nSent from my iPhone",
            ),
            "noise",
            leak_phrase="Sent from my iPhone",
        ),
    ],
    # Batch 2 - Midterm season
    [
        LabeledEmail(
            _e(
                "Midterm Exam Schedule Released - COMP2611",
                "comp2611-ta@ust.hk",
                "The midterm exam for COMP2611 will be held on October 20th from 7-9pm in Sports Hall 2. Seating arrangements will be posted closer to the date.",
            ),
            "deadline",
            expect="Midterm",
        ),
        LabeledEmail(
            _e(
                "Course Withdrawal Deadline is Oct 25",
                "registrar@ust.hk",
                "The last day to withdraw from a course with a 'W' grade is October 25th. Withdrawals after this date will not be processed.",
            ),
            "deadline",
            expect="Withdrawal Deadline",
        ),
        LabeledEmail(
            _e(
                "Dean's List Research Assistant Positions Open",
                "cse-dept@ust.hk",
                "The department is hiring undergraduate Research Assistants for the Spring semester. Priority given to students on the Dean's List. Apply via the department portal.",
            ),
            "opportunity",
            expect="Research Assistant",
        ),
        LabeledEmail(
            _e(
                "McKinsey Case Competition - Apply by Nov 1",
                "careers@ust.hk",
                "McKinsey & Company is hosting a case competition for undergraduates. Top teams win an interview fast-track. Applications close November 1st.",
            ),
            "opportunity",
            expect="McKinsey",
        ),
        LabeledEmail(
            _e(
                "Workshop: Resume Building for Tech Internships",
                "careers@ust.hk",
                "Join our hands-on workshop on building a resume tailored for tech internship applications. October 22nd, 2pm, Career Center.",
            ),
            "event",
            expect="Resume Building",
        ),
        LabeledEmail(
            _e(
                "Mental Health Awareness Week - Free Yoga Sessions",
                "wellness@ust.hk",
                "As part of Mental Health Awareness Week, we're offering free yoga sessions every morning this week at the Wellness Center.",
            ),
            "event",
            expect="Mental Health Awareness",
        ),
        LabeledEmail(
            _e(
                "Grade Appeal Process Updated",
                "registrar@ust.hk",
                "The grade appeal process has been updated to include a new online submission form. Please review the updated procedure on the registrar's website.",
            ),
            "announcement",
            expect="Grade Appeal",
        ),
        LabeledEmail(
            _e(
                "Congratulations to our Dean's Honor List Students",
                "cse-dept@ust.hk",
                "Congratulations to the students named to this semester's Dean's Honor List for outstanding academic achievement.",
            ),
            "announcement",
            expect="Dean's Honor List",
        ),
        LabeledEmail(
            _e(
                "Flash Sale: Campus Bookstore Merch",
                "deals@campusbookstore.com",
                "24 hours only: 30% off all university-branded hoodies, mugs, and stationery. Shop now before it's gone!",
            ),
            "noise",
            leak_phrase="Flash Sale",
        ),
        LabeledEmail(
            _e(
                "Daily Campus Events Digest",
                "events@ust.hk",
                "Here's what's happening on campus today: club meetings, intramural sports, and the daily dining hall specials.",
            ),
            "noise",
            leak_phrase="Daily Campus Events Digest",
        ),
        LabeledEmail(
            _e(
                "Your Password Was Changed Successfully",
                "no-reply@ust.hk",
                "This is an automated confirmation that your account password was changed successfully. If this wasn't you, contact IT support.",
            ),
            "noise",
            leak_phrase="Password Was Changed",
        ),
        LabeledEmail(
            _e(
                "Thanks!",
                "classmate456@connect.ust.hk",
                "Thanks! -- John\n\n(sent from mobile)",
            ),
            "noise",
            leak_phrase="sent from mobile",
        ),
    ],
    # Batch 3 - Finals / end of semester
    [
        LabeledEmail(
            _e(
                "Final Project Submission Deadline: Dec 5",
                "comp4211-ta@ust.hk",
                "The final project report and code submission for COMP4211 is due December 5th at 11:59pm on Canvas. No extensions will be granted.",
            ),
            "deadline",
            expect="Final Project",
        ),
        LabeledEmail(
            _e(
                "Library Book Return Deadline Before Winter Break",
                "library@ust.hk",
                "All borrowed library books must be returned by December 12th, before the campus closes for winter break. Late fees apply after this date.",
            ),
            "deadline",
            expect="Library Book Return",
        ),
        LabeledEmail(
            _e(
                "Spring Study Abroad Applications Now Open",
                "global-programs@ust.hk",
                "Applications for Spring semester study abroad exchange programs are now open. Explore partner universities in Europe, North America, and Asia.",
            ),
            "opportunity",
            expect="Study Abroad",
        ),
        LabeledEmail(
            _e(
                "Google STEP Internship Applications Close Jan 15",
                "careers@ust.hk",
                "Google's STEP internship program for first and second-year students closes applications on January 15th. Apply early, spots are limited.",
            ),
            "opportunity",
            expect="Google STEP",
        ),
        LabeledEmail(
            _e(
                "End of Semester Social - Dec 10",
                "student-union@ust.hk",
                "Come celebrate the end of the semester with food, games, and music at the Atrium on December 10th, 6pm onwards.",
            ),
            "event",
            expect="End of Semester Social",
        ),
        LabeledEmail(
            _e(
                "Free Exam Stress Relief Workshop",
                "wellness@ust.hk",
                "Feeling overwhelmed by finals? Join our free stress relief workshop with breathing exercises and therapy dogs, December 3rd at the Wellness Center.",
            ),
            "event",
            expect="Exam Stress Relief",
        ),
        LabeledEmail(
            _e(
                "Final Exam Seating Arrangement Posted",
                "registrar@ust.hk",
                "Final exam seating arrangements for all courses have been posted on the registrar's website. Please check your assigned seat before exam day.",
            ),
            "announcement",
            expect="Final Exam Seating",
        ),
        LabeledEmail(
            _e(
                "You Won the Departmental Coding Competition!",
                "cse-dept@ust.hk",
                "Congratulations! You placed 1st in this semester's Departmental Coding Competition. A certificate will be mailed to your department mailbox.",
            ),
            "announcement",
            expect="Coding Competition",
        ),
        LabeledEmail(
            _e(
                "Holiday Sale - Campus Store",
                "deals@campusbookstore.com",
                "Our biggest sale of the year is here! Up to 40% off apparel and gifts for the holidays. In-store and online.",
            ),
            "noise",
            leak_phrase="Holiday Sale",
        ),
        LabeledEmail(
            _e(
                "Alumni Monthly Digest",
                "alumni@ust.hk",
                "Catch up on alumni news, upcoming reunions, and donation opportunities in this month's Alumni Digest.",
            ),
            "noise",
            leak_phrase="Alumni Monthly Digest",
        ),
        LabeledEmail(
            _e(
                "Unsubscribe Confirmation - Sports Newsletter",
                "no-reply@ust.hk",
                "You have been unsubscribed from the Sports Newsletter mailing list.",
            ),
            "noise",
            leak_phrase="Unsubscribe Confirmation",
        ),
        LabeledEmail(
            _e(
                "Ok thanks",
                "classmate789@connect.ust.hk",
                "Ok thanks, talk later.\n\nBest,\nSarah",
            ),
            "noise",
            leak_phrase="talk later",
        ),
    ],
]
