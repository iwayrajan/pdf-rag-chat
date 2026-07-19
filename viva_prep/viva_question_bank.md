# Viva Question Bank — Chat With Your PDF (RAG System)

## How to use this

Read through once for understanding, then use the **cheat sheet** at the end for
last-minute review. Practice saying the **2-minute pitch** out loud at least twice —
examiners often just want to see you can explain your own project fluently before
they start asking specifics.

---

## Section 1: Conceptual (RAG & AI basics)

**Q: What is RAG (Retrieval-Augmented Generation)?**
A: RAG is a technique that combines an information retrieval system with a large
language model. Instead of relying only on what the LLM learned during training,
the system first retrieves relevant passages from a document collection, then gives
those passages to the LLM as context so it can generate an answer grounded in that
specific content.

**Q: How is this different from just using ChatGPT?**
A: ChatGPT (or any base LLM) only knows what it learned during training and has no
access to your private documents. If you ask it about a PDF it's never seen, it can
only guess or refuse. This system extracts and indexes the actual content of your
PDF, retrieves the exact relevant sections, and gives them to the LLM as context — so
the answer is grounded in your document rather than the model's general knowledge.

**Q: What is an embedding?**
A: An embedding is a numerical vector representation of text that captures its
meaning. Texts with similar meaning get vectors that are close together in this
high-dimensional space, even if they use completely different words. This is what
allows "semantic" search, as opposed to matching exact keywords.

**Q: Why do you need a vector database / FAISS?**
A: Once every chunk of text is converted into an embedding vector, we need an
efficient way to find which vectors are closest to a query's vector. Comparing
against every chunk one by one would be slow at scale. FAISS is a library built
specifically for fast similarity search over large collections of vectors.

**Q: What is semantic search vs keyword search?**
A: Keyword search matches literal words or phrases — it fails if the query uses a
synonym or different phrasing than the document. Semantic search compares meaning
via embeddings, so a question like "how much does it cost" can match a passage that
says "the price is" even though no words overlap.

**Q: What is hallucination in LLMs, and how does this project reduce it?**
A: Hallucination is when a language model generates a confident, plausible-sounding
answer that is actually false or fabricated, typically because it's asked about
something outside its training data. This project reduces hallucination by
explicitly instructing the model to answer only from the retrieved context, and to
say so when the answer isn't present in that context, rather than guessing.

**Q: What is chunking and why is it necessary?**
A: Chunking is splitting a document into smaller pieces before embedding them. It's
necessary because embedding an entire document as one vector would lose fine-grained
detail (you couldn't tell which part of a 50-page PDF matched your query), and
because language models have a limited context window, so you can only feed in a
limited amount of text at answer time.

---

## Section 2: Architecture & design

**Q: Walk me through what happens when I upload a PDF.**
A: The PDF is converted to Markdown text page by page using pymupdf4llm, which
detects headings and structure based on font size. Each page's text is then split
into chunks, primarily along detected headings, with a word-count fallback for
long sections. Each chunk is converted into a vector embedding using a
sentence-transformer model, and all vectors are added to a FAISS index. Every chunk
is tagged with metadata recording which file and page it came from.

**Q: Walk me through what happens when I ask a question.**
A: First, the system checks whether the question is "broad" (like a summary
request) or "specific." For specific questions, it checks for numeric identifiers
(like a task number) and does an exact text match for those first, then fills the
rest with vector similarity search — this is the hybrid retrieval step. For broad
questions, it skips retrieval and sends the whole document text instead. Either way,
the retrieved content (with source and page metadata) is placed into a prompt and
sent to the Groq API, which generates the final answer with citations.

**Q: Why did you choose FAISS over a full database?**
A: For the scale of a single-user, personal-use application, FAISS is simpler to set
up (an in-memory library, not a separate server process), free, and fast enough. A
full vector database like Pinecone or Weaviate would add operational complexity and,
in Pinecone's case, ongoing cost, without meaningful benefit at this scale.

**Q: Why sentence-transformers/MiniLM instead of a bigger embedding model?**
A: MiniLM is a compact model (~22 million parameters) that runs efficiently on a
CPU with no GPU required, while still producing good-quality embeddings for
semantic search. Larger embedding models would be more accurate but slower and
often require a GPU to run at a reasonable speed — not necessary for this project's
scale.

**Q: Why Groq instead of OpenAI or another paid API?**
A: Groq offers a generous free tier and very fast inference for open-weight models
like Llama, which suits a personal/academic project where cost and speed both
matter. OpenAI's API is not free, which would add a real cost for something used
mainly for learning and demonstration.

**Q: What's the difference between the indexing phase and the query phase?**
A: Indexing happens once per uploaded document: extraction, chunking, embedding,
and adding to the FAISS index. Querying happens every time the user asks a
question: retrieval against the already-built index, followed by answer
generation. Separating these means the expensive embedding step only happens once
per document, not on every question.

---

## Section 3: Technical deep-dive

**Q: What is hybrid retrieval and why did you implement it?**
A: Hybrid retrieval combines exact keyword/identifier matching with vector
similarity search. I implemented it after finding that vector search alone
performed poorly on questions containing numeric identifiers — for example, "TASK
3.1.2" and "TASK 3.2.2" produce nearly identical embeddings because the model
captures general meaning, not exact digit sequences. The system detects
number-like patterns in a question, searches for literal matches first, then fills
any remaining slots with vector search results.

**Q: How do you detect a "broad" question like a summary request?**
A: I check the question against a list of signal phrases — words like "summarize,"
"overview," "main points," "tl;dr," and similar. If any of these appear, the system
treats it as a whole-document question and skips the normal retrieval path.

**Q: What happens if the document doesn't have proper markdown headers?**
A: If pymupdf4llm doesn't detect any heading-level formatting (for example, if the
PDF uses plain paragraph text without distinct font sizes for headings), the
chunker falls back to splitting by word count with overlap, so the document is
still divided into indexable pieces, just without section-aware boundaries.

**Q: How do you handle multiple PDFs at once?**
A: Each PDF is processed independently and added to a single shared FAISS index.
Every chunk carries metadata recording which source file it came from, so when
multiple documents are loaded, retrieval can pull relevant chunks from any of them,
and the final answer cites the correct source file per chunk.

**Q: How is page-level citation achieved?**
A: pymupdf4llm's page_chunks mode returns text separately for each page along with
its page number. That page number is attached as metadata to every chunk derived
from that page, so it can be included in the answer's citation.

**Q: What's the chunk overlap for and why does it matter?**
A: When a long section is split by word count, a small overlap (e.g. 40 words)
between consecutive chunks helps preserve context that spans a chunk boundary — for
example, a sentence that starts near the end of one chunk and continues into the
next won't lose its full meaning in either chunk.

**Q: What are the limitations of your system?**
A: It currently only supports PDF files; it re-processes documents from scratch
each session rather than persisting the index; it uses a simple pattern-based
detection for broad questions rather than a learned classifier; and retrieval
quality hasn't been measured with formal metrics like precision or recall, only
manual testing.

---

## Section 4: Testing & evaluation

**Q: How did you test your system?**
A: I tested it manually against a set of representative scenarios: uploading valid
PDFs, asking specific factual questions, asking for summaries, asking about
similar-looking numeric identifiers, uploading multiple PDFs together, removing a
loaded document, and asking questions with no relevant content in the document. All
test cases produced the expected behavior.

**Q: What would you do to formally evaluate retrieval quality?**
A: I would build a small labeled test set of questions with known correct source
passages, then measure standard information-retrieval metrics like precision@k and
recall@k — checking what fraction of retrieved chunks are actually relevant, and
what fraction of relevant chunks get retrieved.

**Q: What edge cases did you consider?**
A: Documents with no detectable headings, questions with no answer in the document,
multiple documents with overlapping topics, and questions referencing numeric
identifiers that are semantically similar to other identifiers in the same
document.

---

## Section 5: Tricky / comparative questions examiners like to ask

**Q: Why not just feed the whole PDF into the LLM's context window?**
A: For short documents this can work, and the system actually does this for
whole-document summary questions. But for longer documents, the text may exceed
the model's context window, and even when it fits, sending the entire document on
every question is slower and, for paid APIs, more expensive than retrieving only
the relevant few chunks.

**Q: Why not use ChatGPT's built-in file upload feature?**
A: That's a valid alternative for casual use, but it's a closed system you can't
inspect, customize, or run at no cost beyond a subscription. Building the pipeline
manually demonstrates understanding of how retrieval and grounding actually work
underneath, rather than treating it as a black box — which is the point of an
academic project.

**Q: What if two PDFs contain contradictory information?**
A: Currently, the system would retrieve relevant chunks from both and pass them to
the LLM, which may either mention both perspectives or favor whichever chunk
appears more relevant to the specific question. The system doesn't currently have
explicit conflict-resolution logic; this is a reasonable direction for future work.

**Q: Is this system scalable to thousands of documents?**
A: The current FAISS index (IndexFlatL2) performs an exact, brute-force search
across all vectors, which is fine for a personal collection but would slow down at
a much larger scale. For thousands of documents, an approximate nearest-neighbor
index (like FAISS's IVF or HNSW index types) would trade a small amount of accuracy
for much faster search.

**Q: What are the security/privacy implications of sending documents to a
third-party API?**
A: Retrieved chunks (not the full raw PDF) are sent to Groq's API to generate the
answer, meaning some document content does leave the local machine. For sensitive
or confidential documents, this is a real consideration — a fully local setup would
require running an open-weight LLM locally instead, which needs more powerful
hardware than this project targets.

---

## Cheat sheet — one-pager

| Component | Tool used | One-line justification |
|---|---|---|
| PDF extraction | pymupdf4llm | Preserves page and heading structure, unlike a flat text dump |
| Chunking | Custom (header-based + word-count fallback) | Keeps chunks semantically coherent where possible |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) | Runs on CPU, no GPU needed, good quality-to-speed ratio |
| Vector search | FAISS (IndexFlatL2) | Fast, free, in-memory, no server to run |
| Retrieval strategy | Hybrid (keyword + vector) | Fixes vector search's weakness on numeric identifiers |
| Answer generation | Groq API (Llama models) | Free tier, fast inference, no local GPU needed |
| Interface | Streamlit | Quick to build a chat UI in pure Python |

---

## 2-minute pitch script

Practice saying this out loud until it's fluent — it's meant to sound natural, not
memorized word-for-word.

> "My project is a system that lets you upload a PDF and ask it questions in plain
> English, and get answers that are actually grounded in that document — with the
> exact page cited — instead of a generic AI response.
>
> The way it works: when you upload a PDF, I extract the text page by page,
> preserving headings, and split it into chunks. Each chunk gets converted into a
> vector embedding using a small model that runs on a regular CPU, and all those
> vectors go into a FAISS index for fast search.
>
> When you ask a question, the system decides whether it's a broad question — like
> asking for a summary — or a specific one, like asking about a particular section.
> Broad questions get the whole document as context. Specific questions go through
> what I call hybrid retrieval: I check if the question mentions something like a
> section number, and if so, I search for that exact text first, because I found
> that pure vector search actually confuses similar-looking numbers — it can't
> reliably tell '3.1.2' from '3.2.2' since they mean almost the same thing to an
> embedding model. Vector search fills in the rest.
>
> Whatever's retrieved gets sent to a large language model through Groq's API, which
> is free and fast, and it generates an answer that cites exactly which file and
> page the information came from.
>
> The whole thing runs on a normal laptop, no GPU, no paid subscriptions — which was
> a deliberate design goal, to show this is achievable without specialized
> infrastructure."

---

## Tips for the actual viva

- If you don't know an answer, say what you *do* know and reason toward it out
  loud — examiners often care more about your thought process than a perfect
  answer.
- If asked "why did you choose X," always have a *comparison in mind* (what you
  didn't choose, and why) — this cheat sheet's justification column is built for
  exactly that.
- Expect at least one "what would you improve" question — Chapter 8 (Future
  Scope) in the report is your prepared answer.
