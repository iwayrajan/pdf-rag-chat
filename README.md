# Chat with your PDF (local RAG, CPU-only)

Upload a PDF, ask questions, get answers grounded in the document — no GPU, no paid API.

## How it works

1. **PDF → Markdown** (`pymupdf4llm`) — preserves headings/structure instead of a flat text dump.
2. **Chunking** — split by markdown headers first, then by word count with overlap for long sections.
3. **Embeddings** (`sentence-transformers`, model: `all-MiniLM-L6-v2`) — runs on CPU, no API needed.
4. **Vector search** (`faiss-cpu`) — local, in-memory index, no server to run.
5. **Answer generation** (Groq's free API) — retrieved chunks are stuffed into a prompt and sent to a fast open-weight model.

## Setup

```bash
# 1. Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
```

## Get a free Groq API key

1. Go to https://console.groq.com/keys
2. Sign up with email or Google (no credit card required)
3. Create an API key and copy it

You'll paste this into the app's sidebar when you run it (or set it as an environment
variable `GROQ_API_KEY` so it's pre-filled).

## Run it

```bash
streamlit run app.py
```

This opens a browser tab at `http://localhost:8501`. From there:

1. Paste your Groq API key in the sidebar
2. Upload a PDF
3. Wait for indexing (a progress spinner shows while it extracts/chunks/embeds)
4. Ask questions in the chat box at the bottom

## Notes

- First run will download the embedding model (~90MB) from Hugging Face — needs internet
  once, then it's cached locally for future runs.
- The "Show retrieved chunks" expander under each answer lets you see exactly what
  context the model was given — useful for understanding why an answer is right or wrong.
- If answers seem off, try increasing "Chunks to retrieve" in the sidebar, or switch to
  the 70B model for better reasoning (slightly slower).

## Files

- `app.py` — Streamlit UI (upload, chat, settings)
- `rag.py` — the actual RAG pipeline logic (reusable outside the UI too)
- `requirements.txt` — dependencies

## Using this as a college mini/major project

This repo also includes everything needed to package and sell this as a college
project submission:

- `student_config.json` — one shared config (name, college, guide, etc.) used by
  both generators below
- `scripts/generate_all.sh` — regenerates the report + presentation and packages
  them into `deliverables/<student_name>/` in one command
- `report_template/` — the 8-chapter Word report generator
- `presentation/` — the 13-slide PowerPoint deck generator
- `docs/` — architecture and query-routing diagrams (SVG + PNG)
- `viva_prep/viva_question_bank.md` — anticipated viva questions with answers,
  a cheat sheet, and a rehearsed pitch script
- `tracker/Student_Order_Tracker.xlsx` — personal order/revenue tracker and a
  reusable per-order delivery checklist

**Quickest path for a new order:** edit `student_config.json`, then run
`bash scripts/generate_all.sh` from the repo root.
