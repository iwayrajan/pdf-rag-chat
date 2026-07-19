"""
Core RAG pipeline: PDF -> markdown (per page) -> chunks -> embeddings -> FAISS index -> retrieval.
Supports multiple PDFs indexed together, with each chunk tagged to its source file and page
number so answers can cite exactly where they came from.
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

        self.chunks: list[str] = []
        # chunk_meta[i] = {"source": filename, "page": page_number} for chunks[i]
        self.chunk_meta: list[dict] = []

        # full_text_by_source["file.pdf"] -> full extracted text, for whole-document
        # questions (summaries) scoped to a single file or all files combined.
        self.full_text_by_source: dict[str, str] = {}

    # ---------- Step 1: PDF -> per-page Markdown ----------
    def pdf_to_pages(self, pdf_path: str) -> list[dict]:
        """
        Returns a list of {"text": ..., "page": ...} using pymupdf4llm's page_chunks
        mode, which preserves per-page boundaries so we can cite page numbers later.
        """
        pages = pymupdf4llm.to_markdown(pdf_path, page_chunks=True)
        return [
            {"text": p["text"], "page": p["metadata"].get("page_number", i + 1)}
            for i, p in enumerate(pages)
        ]

    # ---------- Step 2: Chunking (per page, so metadata stays attached) ----------
    def chunk_page_text(self, text: str, max_words: int = 250, overlap_words: int = 40) -> list[str]:
        """
        Split primarily on markdown headers to keep chunks semantically coherent,
        then sub-split any section that's still too long by word count.
        """
        sections = re.split(r"(?=^#{1,6}\s)", text, flags=re.MULTILINE)
        sections = [s.strip() for s in sections if s.strip()]

        chunks = []
        for section in sections:
            words = section.split()
            if len(words) <= max_words:
                chunks.append(section)
            else:
                step = max_words - overlap_words
                for i in range(0, len(words), step):
                    piece = " ".join(words[i:i + max_words])
                    if piece.strip():
                        chunks.append(piece)
        return chunks

    # ---------- Step 3: Embeddings + Index (rebuilt over all chunks so far) ----------
    def _rebuild_index(self):
        if not self.chunks:
            self.index = None
            return
        embeddings = self.embed_model.encode(
            self.chunks, show_progress_bar=False, convert_to_numpy=True
        )
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(np.array(embeddings).astype("float32"))
        self.index = index

    # ---------- Step 4: Retrieval (returns chunk + metadata pairs) ----------
    def retrieve(self, query: str, k: int = 4) -> list[dict]:
        """Returns [{"text": chunk, "source": filename, "page": n}, ...]"""
        if self.index is None or not self.chunks:
            return []
        query_vec = self.embed_model.encode([query], convert_to_numpy=True).astype("float32")
        k = min(k, len(self.chunks))
        distances, indices = self.index.search(query_vec, k)
        results = []
        for i in indices[0]:
            if i == -1:
                continue
            results.append({"text": self.chunks[i], **self.chunk_meta[i]})
        return results

    def retrieve_hybrid(self, query: str, k: int = 4) -> list[dict]:
        """
        Vector search alone struggles with exact identifiers (task numbers, section
        codes, IDs) because embeddings capture meaning, not literal digit sequences -
        "TASK 3.1.2" and "TASK 3.2.2" look almost identical to the embedding model.

        Checks for identifier-like tokens in the query and does a literal
        case-insensitive search for them first, then fills remaining slots with
        vector search results.
        """
        if self.index is None or not self.chunks:
            return []

        identifier_pattern = r"\b\d+(?:\.\d+){1,3}\b"
        identifiers = re.findall(identifier_pattern, query)

        exact_matches = []
        if identifiers:
            for i, chunk in enumerate(self.chunks):
                if any(ident in chunk for ident in identifiers):
                    exact_matches.append({"text": chunk, **self.chunk_meta[i]})

        vector_matches = self.retrieve(query, k=k)

        seen = set()
        combined = []
        for item in exact_matches + vector_matches:
            key = item["text"]
            if key not in seen:
                combined.append(item)
                seen.add(key)
            if len(combined) >= max(k, len(exact_matches)):
                break

        return combined

    # ---------- End to end setup ----------
    def add_pdf(self, pdf_path: str, source_name: str, max_words: int = 250, overlap_words: int = 40):
        """
        Adds one PDF into the shared index. Can be called multiple times for
        multiple PDFs - each call appends rather than replacing.
        """
        pages = self.pdf_to_pages(pdf_path)

        full_text_parts = []
        for page in pages:
            page_chunks = self.chunk_page_text(page["text"], max_words=max_words, overlap_words=overlap_words)
            for chunk in page_chunks:
                self.chunks.append(chunk)
                self.chunk_meta.append({"source": source_name, "page": page["page"]})
            full_text_parts.append(page["text"])

        self.full_text_by_source[source_name] = "\n\n".join(full_text_parts)
        self._rebuild_index()
        return sum(1 for m in self.chunk_meta if m["source"] == source_name)

    def remove_pdf(self, source_name: str):
        """Removes a previously added PDF from the index."""
        keep_indices = [i for i, m in enumerate(self.chunk_meta) if m["source"] != source_name]
        self.chunks = [self.chunks[i] for i in keep_indices]
        self.chunk_meta = [self.chunk_meta[i] for i in keep_indices]
        self.full_text_by_source.pop(source_name, None)
        self._rebuild_index()

    def get_full_text(self, source_name: str = None) -> str:
        """Full text for one source, or all sources combined if none specified."""
        if source_name:
            return self.full_text_by_source.get(source_name, "")
        return "\n\n".join(
            f"=== {name} ===\n{text}" for name, text in self.full_text_by_source.items()
        )

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
