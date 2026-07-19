"""
Multi-PDF RAG chat app.
Upload one or more PDFs -> ask questions -> answers grounded in retrieved chunks,
cited with source filename + page number, via Groq's free API.

Run with: streamlit run app.py
"""

import os
import tempfile

import streamlit as st
from groq import Groq

from rag import PDFRag

st.set_page_config(page_title="Chat with your PDFs", page_icon="📄", layout="wide")

# ---------------- Sidebar: API key + settings ----------------
with st.sidebar:
    st.header("Settings")

    default_key = os.environ.get("GROQ_API_KEY", "")
    groq_key = st.text_input(
        "Groq API key",
        value=default_key,
        type="password",
        help="Free key from https://console.groq.com/keys — never stored, only used in this session.",
    )

    model_name = st.selectbox(
        "Groq model",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"],
        help="70B is smarter but slower; 8B is near-instant.",
    )

    top_k = st.slider("Chunks to retrieve per question", 2, 8, 4)

    st.markdown("---")
    st.caption(
        "Pipeline: PDF → per-page Markdown (pymupdf4llm) → chunks tagged with "
        "source + page → embeddings (sentence-transformers, CPU) → FAISS index → "
        "Groq LLM for the answer."
    )

# ---------------- Session state ----------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "loaded_files" not in st.session_state:
    st.session_state.loaded_files = set()


@st.cache_resource(show_spinner=False)
def get_rag_engine():
    return PDFRag()


rag = get_rag_engine()

# ---------------- Main: multi-file upload ----------------
st.title("📄 Chat with your PDFs")
st.caption("A small local RAG pipeline — upload one or more PDFs, then ask questions across all of them.")

uploaded_files = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    new_files = [f for f in uploaded_files if f.name not in st.session_state.loaded_files]
    if new_files:
        for f in new_files:
            with st.spinner(f"Indexing '{f.name}'... (extracting text, chunking, embedding)"):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(f.read())
                    tmp_path = tmp.name

                num_chunks = rag.add_pdf(tmp_path, source_name=f.name)
                st.session_state.loaded_files.add(f.name)
                os.unlink(tmp_path)

            st.success(f"Indexed '{f.name}' into {num_chunks} chunks.")

# ---------------- Loaded documents panel ----------------
if st.session_state.loaded_files:
    with st.expander(f"📚 Loaded documents ({len(st.session_state.loaded_files)})", expanded=False):
        for fname in sorted(st.session_state.loaded_files):
            col1, col2 = st.columns([5, 1])
            col1.write(fname)
            if col2.button("Remove", key=f"remove_{fname}"):
                rag.remove_pdf(fname)
                st.session_state.loaded_files.discard(fname)
                st.rerun()

# ---------------- Chat ----------------
if st.session_state.loaded_files:
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    question = st.chat_input("Ask a question across all loaded PDFs...")

    if question:
        if not groq_key:
            st.error("Add your Groq API key in the sidebar first (it's free, no credit card needed).")
        else:
            st.session_state.chat_history.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)

            with st.chat_message("assistant"):
                is_broad = PDFRag.is_broad_question(question)

                spinner_msg = (
                    "This looks like a whole-document question, using full document text instead of search..."
                    if is_broad
                    else "Retrieving relevant chunks and generating an answer..."
                )

                with st.spinner(spinner_msg):
                    if is_broad:
                        # Summaries/overviews need the whole document, not similarity-matched
                        # fragments — vector search has nothing relevant to match a broad
                        # question against, so it returns near-random chunks.
                        retrieved = []
                        context = rag.get_full_text()
                        # Groq free models have limited context; trim defensively.
                        context = context[:24000]
                    else:
                        retrieved = rag.retrieve_hybrid(question, k=top_k)
                        context = "\n\n---\n\n".join(
                            f"[Source: {item['source']}, page {item['page']}]\n{item['text']}"
                            for item in retrieved
                        )

                    prompt = f"""Answer the question using ONLY the context below. \
If the answer isn't in the context, say you don't have enough information from the documents. \
When you use information from the context, mention which source file and page it came from.

Context:
{context}

Question: {question}

Answer:"""

                    try:
                        client = Groq(api_key=groq_key)
                        response = client.chat.completions.create(
                            model=model_name,
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.2,
                        )
                        answer = response.choices[0].message.content
                    except Exception as e:
                        answer = f"Error calling Groq API: {e}"

                    st.markdown(answer)

                    if is_broad:
                        with st.expander("Show what the model actually saw"):
                            st.caption("Whole-document mode: full extracted text was sent, not retrieved chunks.")
                            st.markdown(context)
                    else:
                        with st.expander("Show retrieved chunks (what the model actually saw)"):
                            for i, item in enumerate(retrieved, 1):
                                st.markdown(f"**Chunk {i}** — *{item['source']}, page {item['page']}*\n\n{item['text']}")

            st.session_state.chat_history.append({"role": "assistant", "content": answer})
else:
    st.info("Upload one or more PDFs above to get started.")
