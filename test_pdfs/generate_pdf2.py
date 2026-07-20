from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="SectionHeading", parent=styles["Heading3"], spaceBefore=14, spaceAfter=6, textColor=colors.HexColor("#534AB7")))
styles.add(ParagraphStyle(name="MetaLine", parent=styles["Normal"], textColor=colors.HexColor("#5F5E5A"), fontSize=9, spaceAfter=10))

doc = SimpleDocTemplate("GreenLeaf_Employee_Handbook.pdf", pagesize=letter,
                         topMargin=0.9*inch, bottomMargin=0.9*inch, leftMargin=0.9*inch, rightMargin=0.9*inch)
story = []

def section(code, title, body):
    story.append(Paragraph(f"{code}: {title}", styles["SectionHeading"]))
    story.append(Paragraph(body, styles["Normal"]))
    story.append(Spacer(1, 6))

# ---------- Title ----------
story.append(Paragraph("GreenLeaf Corp", styles["Title"]))
story.append(Paragraph("Employee Handbook &mdash; Leave &amp; Attendance Policy", styles["Heading2"]))
story.append(Spacer(1, 12))
story.append(Paragraph(
    "Policy version 4.1 &nbsp;|&nbsp; Effective: January 2026 &nbsp;|&nbsp; Applies to: All full-time employees",
    styles["MetaLine"]))
story.append(Spacer(1, 10))

# ---------- Section 1 ----------
story.append(Paragraph("Section 1: Purpose and Scope", styles["Heading1"]))
story.append(Paragraph(
    "This policy defines the types of leave available to GreenLeaf employees, the process for "
    "requesting leave, and the approval workflow. It applies to all full-time employees across all "
    "office locations. Contract and intern staff should refer to their individual agreements.",
    styles["Normal"]))
story.append(Spacer(1, 14))

# ---------- Section 2 ----------
story.append(Paragraph("Section 2: Types of Leave", styles["Heading1"]))
story.append(Spacer(1, 4))

section("Section 2.1", "Casual Leave",
        "Employees are entitled to 12 days of casual leave per calendar year, credited monthly at the "
        "rate of one day per month. Casual leave cannot be carried forward to the next year and lapses "
        "on December 31st.")

section("Section 2.2", "Sick Leave",
        "Employees are entitled to 10 days of sick leave per calendar year. A medical certificate is "
        "required for sick leave exceeding 2 consecutive days. Unused sick leave may be carried forward "
        "up to a maximum of 15 days.")

section("Section 2.3", "Earned Leave",
        "Earned leave accrues at 1.5 days per month of continuous service and may be accumulated up to "
        "45 days. Earned leave requires at least 5 working days of advance notice, except in cases "
        "covered under emergency leave provisions.")

story.append(PageBreak())

# ---------- Section 3 ----------
story.append(Paragraph("Section 3: Application Process", styles["Heading1"]))
story.append(Spacer(1, 4))

section("Section 3.1", "Advance Notice Requirements",
        "Planned leave of any type must be submitted through the HR portal at least 5 working days "
        "before the intended start date, except for sick leave and emergencies, which may be applied "
        "for retroactively within 48 hours of returning to work.")

section("Section 3.2", "Emergency Leave Requests",
        "Emergency leave requests may be submitted with less than 24 hours' notice via the HR portal or "
        "direct communication with the reporting manager. See Sections 3.2.1 and 3.2.2 for verification "
        "and extension procedures.")

section("Section 3.2.1", "Emergency Contact Verification",
        "For emergency leave exceeding 2 days, HR may request verification through the employee's "
        "registered emergency contact before the leave is formally approved in the system.")

section("Section 3.2.2", "Extended Emergency Leave Protocol",
        "If an emergency situation requires leave beyond 5 consecutive working days, the employee's "
        "manager must escalate the case to HR for review under the Extended Leave provisions described "
        "in Section 4.3, which may draw against earned leave balance or be granted as unpaid leave "
        "depending on balance availability.")

story.append(PageBreak())

# ---------- Section 4 ----------
story.append(Paragraph("Section 4: Approval Workflow", styles["Heading1"]))
story.append(Spacer(1, 4))

section("Section 4.1", "Manager Approval",
        "All leave requests are first routed to the employee's direct reporting manager, who must "
        "approve or reject the request within 2 working days of submission.")

section("Section 4.2", "HR Escalation",
        "If a manager does not respond within 2 working days, the request is automatically escalated "
        "to the HR team, who will make a determination within 1 additional working day.")

section("Section 4.3", "Extended Leave Review",
        "Leave requests exceeding 10 consecutive working days, regardless of leave type, require "
        "review by both the department head and HR before approval, and may involve a temporary "
        "handover plan being documented for the employee's ongoing responsibilities.")

story.append(PageBreak())

# ---------- Appendix ----------
story.append(Paragraph("Appendix A: Leave Balance Summary (Example)", styles["Heading1"]))
table_data = [
    ["Leave Type", "Annual Entitlement", "Carry-Forward Limit"],
    ["Casual Leave", "12 days", "None (lapses annually)"],
    ["Sick Leave", "10 days", "15 days"],
    ["Earned Leave", "18 days (accrued)", "45 days"],
]
t = Table(table_data, colWidths=[2.0*inch, 2.2*inch, 2.2*inch])
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#534AB7")),
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
print("Generated GreenLeaf_Employee_Handbook.pdf")
