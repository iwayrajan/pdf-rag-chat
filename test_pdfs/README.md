# Sample test PDFs

Two ready-made PDFs designed to show off the tool's key features in under 2 minutes —
hand these to anyone testing the app before they buy, so they don't need their own
document to try it.

- **EduTrack_LMS_Project_Requirements.pdf** — a fictional software project plan with
  numbered tasks (TASK 1.1.1, TASK 3.2.2, etc.), owners, and deadlines across 3 chapters.
- **GreenLeaf_Employee_Handbook.pdf** — a fictional HR leave policy with numbered
  sections (Section 2.1, Section 4.3, etc.) — a completely different domain, for
  testing multi-document behavior.

Both were generated with distinct heading styles so the app's chunking correctly
detects section boundaries — confirmed by checking the extracted markdown structure
before finalizing these.

## Suggested test script (in this order)

**1. Upload just `EduTrack_LMS_Project_Requirements.pdf`**

- Ask: *"What is TASK 3.2.2?"*
  Shows off hybrid retrieval — the document also has TASK 3.1.2 and TASK 3.2.1, which
  are easy for pure vector search to confuse with 3.2.2. This should return the exact
  right task (Push Notification Service) with the correct page cited.

- Ask: *"Summarize this document"*
  Shows off whole-document mode — should give a coherent overview instead of a
  disjointed answer stitched from random chunks.

- Ask: *"Who owns the SMS alerts task and what's the deadline?"*
  A natural-language question with no exact keyword match to test semantic search
  (the document says "SMS Alerts for Deadlines" under TASK 3.1.2 — Karan D., Sprint 8).

**2. Upload `GreenLeaf_Employee_Handbook.pdf` as well (now both are loaded)**

- Ask: *"What is 3.2.2?"*
  This is the best demo moment: **both documents contain a "3.2.2"** — EduTrack's
  TASK 3.2.2 (Push Notification Service) and GreenLeaf's Section 3.2.2 (Extended
  Emergency Leave Protocol) — completely unrelated content that happens to share a
  number. A good answer should surface the relevant one(s) with correct source-file
  and page citations, showing the tool doesn't get confused across documents even
  when identifiers collide.

- Ask: *"What's the sick leave policy?"*
  Should pull only from GreenLeaf, correctly ignoring EduTrack even though both are
  loaded.

- Try removing one PDF from the loaded-documents panel and asking a question that
  only the remaining document can answer, to show documents can be managed without
  restarting the app.

## Regenerating or customizing

Both PDFs were built with reportlab (`generate_pdf1.py`, `generate_pdf2.py`). Edit
the task/section content in either script and rerun with:
```bash
pip install reportlab --break-system-packages   # if not already installed
python3 generate_pdf1.py
python3 generate_pdf2.py
```
Useful if you want to swap the domain (e.g. a syllabus instead of an HR handbook) to
match a specific student's interests, or to keep a few variants around so not every
prospective buyer tests with the exact same file.
