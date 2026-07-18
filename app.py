"""
Simple PDF RAG chat app.
Upload a PDF -> ask questions -> answers grounded in retrieved chunks via Groq's free API.

Run with: streamlit run app.py
"""

import os
import tempfile

import streamlit as st
from groq import Groq

from rag import PDFRag

st.set_page_config(page_title="Chat with your PDF", page_icon="📄", layout="wide")

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
        "Pipeline: PDF → Markdown (pymupdf4llm) → chunks → embeddings "
        "(sentence-transformers, CPU) → FAISS index → Groq LLM for the answer."
    )

# ---------------- Session state ----------------
if "rag" not in st.session_state:
    st.session_state.rag = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "processed_filename" not in st.session_state:
    st.session_state.processed_filename = None


@st.cache_resource(show_spinner=False)
def get_rag_engine():
    return PDFRag()


# ---------------- Main: upload ----------------
st.title("📄 Chat with your PDF")
st.caption("A small local RAG pipeline — upload a PDF, then ask it questions.")

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file is not None and uploaded_file.name != st.session_state.processed_filename:
    with st.spinner("Reading and indexing the PDF... (extracting text, chunking, embedding)"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        rag = get_rag_engine()
        rag.chunks = []
        rag.index = None
        num_chunks = rag.process_pdf(tmp_path)

        st.session_state.rag = rag
        st.session_state.processed_filename = uploaded_file.name
        st.session_state.chat_history = []

        os.unlink(tmp_path)

    st.success(f"Indexed '{uploaded_file.name}' into {num_chunks} chunks. Ask away below.")

elif st.session_state.processed_filename:
    st.info(f"Currently loaded: **{st.session_state.processed_filename}**")

# ---------------- Chat ----------------
if st.session_state.rag is not None:
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    question = st.chat_input("Ask a question about the PDF...")

    if question:
        if not groq_key:
            st.error("Add your Groq API key in the sidebar first (it's free, no credit card needed).")
        else:
            st.session_state.chat_history.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)

            with st.chat_message("assistant"):
                with st.spinner("Retrieving relevant chunks and generating an answer..."):
                    retrieved_chunks = st.session_state.rag.retrieve(question, k=top_k)
                    context = "\n\n---\n\n".join(retrieved_chunks)

                    prompt = f"""Answer the question using ONLY the context below. \
If the answer isn't in the context, say you don't have enough information from the document.

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

                    with st.expander("Show retrieved chunks (what the model actually saw)"):
                        for i, chunk in enumerate(retrieved_chunks, 1):
                            st.markdown(f"**Chunk {i}:**\n\n{chunk}")

            st.session_state.chat_history.append({"role": "assistant", "content": answer})
else:
    st.info("Upload a PDF above to get started.")
