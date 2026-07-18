"""
Core RAG pipeline: PDF -> markdown -> chunks -> embeddings -> FAISS index -> retrieval.
Kept deliberately simple and CPU-only.
"""

import re
import numpy as np
import faiss
import pymupdf4llm
from sentence_transformers import SentenceTransformer


class PDFRag:
    def __init__(self, embed_model_name: str = "all-MiniLM-L6-v2"):
        # Loaded once, reused across the session
        self.embed_model = SentenceTransformer(embed_model_name)
        self.index = None
        self.chunks = []
        self.chunk_sources = []  # page/section info per chunk, for citations
        self.full_text = ""  # kept for whole-document questions (summaries, etc.)

    # ---------- Step 1: PDF -> Markdown ----------
    def pdf_to_markdown(self, pdf_path: str) -> str:
        """Uses pymupdf4llm which detects headings/tables via layout, not guesswork."""
        md_text = pymupdf4llm.to_markdown(pdf_path)
        return md_text

    # ---------- Step 2: Chunking ----------
    def chunk_markdown(self, md_text: str, max_words: int = 250, overlap_words: int = 40):
        """
        Split primarily on markdown headers (## Section) to keep chunks semantically
        coherent, then sub-split any section that's still too long by word count.
        """
        # Split on headers, keeping the header with its following text
        sections = re.split(r"(?=^#{1,6}\s)", md_text, flags=re.MULTILINE)
        sections = [s.strip() for s in sections if s.strip()]

        chunks = []
        for section in sections:
            words = section.split()
            if len(words) <= max_words:
                chunks.append(section)
            else:
                # sub-split long sections with overlap
                step = max_words - overlap_words
                for i in range(0, len(words), step):
                    piece = " ".join(words[i:i + max_words])
                    if piece.strip():
                        chunks.append(piece)

        self.chunks = chunks
        return chunks

    # ---------- Step 3: Embeddings + Index ----------
    def build_index(self, chunks: list[str]):
        embeddings = self.embed_model.encode(
            chunks, show_progress_bar=False, convert_to_numpy=True
        )
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(np.array(embeddings).astype("float32"))
        self.index = index
        return index

    # ---------- Step 4: Retrieval ----------
    def retrieve(self, query: str, k: int = 4) -> list[str]:
        if self.index is None or not self.chunks:
            return []
        query_vec = self.embed_model.encode([query], convert_to_numpy=True).astype("float32")
        k = min(k, len(self.chunks))
        distances, indices = self.index.search(query_vec, k)
        return [self.chunks[i] for i in indices[0] if i != -1]

    # ---------- End to end setup ----------
    def process_pdf(self, pdf_path: str, max_words: int = 250, overlap_words: int = 40):
        md_text = self.pdf_to_markdown(pdf_path)
        self.full_text = md_text
        chunks = self.chunk_markdown(md_text, max_words=max_words, overlap_words=overlap_words)
        self.build_index(chunks)
        return len(chunks)

    @staticmethod
    def is_broad_question(query: str) -> bool:
        """
        Detects whole-document questions (summaries, overviews) that vector
        retrieval handles poorly, since there's no specific passage to match against.
        """
        broad_signals = [
            "summar", "what is this document about", "what is this pdf about",
            "overview of", "what does this document cover", "main points",
            "key takeaways", "tl;dr", "gist of", "what's in this",
        ]
        q = query.lower()
        return any(signal in q for signal in broad_signals)
