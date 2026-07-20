from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TaskHeading", parent=styles["Heading3"], spaceBefore=14, spaceAfter=4, textColor=colors.HexColor("#0B3D62")))
styles.add(ParagraphStyle(name="MetaLine", parent=styles["Normal"], textColor=colors.HexColor("#5F5E5A"), fontSize=9, spaceAfter=10))

doc = SimpleDocTemplate("EduTrack_LMS_Project_Requirements.pdf", pagesize=letter,
                         topMargin=0.9*inch, bottomMargin=0.9*inch, leftMargin=0.9*inch, rightMargin=0.9*inch)
story = []

def task(code, title, description, owner, deadline, priority):
    story.append(Paragraph(f"{code}: {title}", styles["TaskHeading"]))
    story.append(Paragraph(f"Owner: {owner} &nbsp;&nbsp;|&nbsp;&nbsp; Deadline: {deadline} &nbsp;&nbsp;|&nbsp;&nbsp; Priority: {priority}", styles["MetaLine"]))
    story.append(Paragraph(description, styles["Normal"]))
    story.append(Spacer(1, 6))

# ---------- Title ----------
story.append(Paragraph("EduTrack LMS", styles["Title"]))
story.append(Paragraph("Project Requirements &amp; Task Breakdown", styles["Heading2"]))
story.append(Spacer(1, 12))
story.append(Paragraph(
    "Document version 2.3 &nbsp;|&nbsp; Last updated: March 2026 &nbsp;|&nbsp; Status: In Development",
    styles["MetaLine"]))
story.append(Spacer(1, 10))

# ---------- Overview ----------
story.append(Paragraph("Overview", styles["Heading1"]))
story.append(Paragraph(
    "EduTrack is a learning management system being built for mid-sized coaching institutes to manage "
    "course content, track student engagement, and automate deadline reminders. This document defines "
    "the task breakdown across three core modules: Content Management, User Analytics, and the "
    "Notification System. Each task includes an owner, deadline, and priority level for sprint planning.",
    styles["Normal"]))
story.append(Spacer(1, 14))

# ---------- Chapter 1 ----------
story.append(Paragraph("Chapter 1: Content Management", styles["Heading1"]))
story.append(Paragraph(
    "This module handles course creation, video content delivery, and version control for instructors "
    "updating existing material.", styles["Normal"]))
story.append(Spacer(1, 6))

task("TASK 1.1.1", "Course Upload Interface",
     "Build a drag-and-drop interface allowing instructors to upload course materials including PDFs, "
     "slide decks, and video files up to 2GB per file. Uploaded files must be virus-scanned before "
     "being made available to students.",
     "Ananya R.", "Sprint 4 (Apr 12)", "High")

task("TASK 1.1.2", "Video Transcoding Pipeline",
     "Implement an automated pipeline that transcodes uploaded videos into multiple resolutions "
     "(360p, 720p, 1080p) using FFmpeg, and generates thumbnail previews at the 10-second mark of "
     "each video.",
     "Rohit K.", "Sprint 5 (Apr 26)", "High")

task("TASK 1.2.1", "Content Versioning",
     "Allow instructors to publish a new version of a lesson without deleting the old one. Students "
     "already partway through the old version should be notified of the update but not force-migrated "
     "mid-course.",
     "Ananya R.", "Sprint 6 (May 10)", "Medium")

story.append(PageBreak())

# ---------- Chapter 2 ----------
story.append(Paragraph("Chapter 2: User Analytics Dashboard", styles["Heading1"]))
story.append(Paragraph(
    "Provides instructors and institute administrators visibility into student engagement, so that "
    "at-risk students can be identified early in the term.", styles["Normal"]))
story.append(Spacer(1, 6))

task("TASK 2.1.1", "Engagement Metrics",
     "Track and display per-student metrics including video watch time, quiz attempt count, and "
     "days-since-last-login, updated on a rolling 24-hour basis.",
     "Priya M.", "Sprint 5 (Apr 26)", "High")

task("TASK 2.1.2", "Cohort Comparison Reports",
     "Generate a weekly report comparing the current cohort's average quiz scores and engagement "
     "against the historical average of the same course from previous terms.",
     "Priya M.", "Sprint 7 (May 24)", "Medium")

task("TASK 2.2.1", "Data Export (CSV/PDF)",
     "Allow administrators to export any analytics view as CSV for further analysis in spreadsheet "
     "tools, or as a formatted PDF suitable for sharing with institute management.",
     "Vikram S.", "Sprint 7 (May 24)", "Low")

story.append(PageBreak())

# ---------- Chapter 3 ----------
story.append(Paragraph("Chapter 3: Notification System", styles["Heading1"]))
story.append(Paragraph(
    "Keeps students informed of upcoming deadlines and new content across email, SMS, and in-app "
    "channels, with configurable preferences per student.", styles["Normal"]))
story.append(Spacer(1, 6))

task("TASK 3.1.1", "Email Digest Scheduler",
     "Send a daily digest email at 7 AM local time summarizing assignments due within the next 48 "
     "hours, using a queued job system to handle institutes with over 10,000 students.",
     "Karan D.", "Sprint 8 (Jun 7)", "Medium")

task("TASK 3.1.2", "SMS Alerts for Deadlines",
     "Send an SMS reminder 2 hours before an assignment deadline, only for assignments marked as "
     "high-priority by the instructor. Integrate with a third-party SMS gateway supporting Indian "
     "carrier numbers.",
     "Karan D.", "Sprint 8 (Jun 7)", "Medium")

task("TASK 3.2.1", "In-App Notification Center",
     "Build a bell-icon notification center within the student dashboard showing the last 30 days of "
     "notifications, with read/unread status and the ability to jump directly to the related course "
     "content.",
     "Meera T.", "Sprint 9 (Jun 21)", "High")

task("TASK 3.2.2", "Push Notification Service",
     "Implement mobile push notifications for the EduTrack Android and iOS apps, triggered by the "
     "same events as the email digest, using Firebase Cloud Messaging. Push notifications must respect "
     "the student's configured quiet hours.",
     "Meera T.", "Sprint 9 (Jun 21)", "High")

story.append(PageBreak())

# ---------- Appendix ----------
story.append(Paragraph("Appendix A: Glossary", styles["Heading1"]))
glossary = [
    ["Term", "Definition"],
    ["Cohort", "A group of students enrolled in the same course during the same term"],
    ["Digest", "A single summary notification bundling multiple individual updates"],
    ["Quiet hours", "A student-configured time window during which push notifications are suppressed"],
]
t = Table(glossary, colWidths=[1.6*inch, 4.6*inch])
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B3D62")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 9),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E4E8")),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
]))
story.append(t)

doc.build(story)
print("Generated EduTrack_LMS_Project_Requirements.pdf")
