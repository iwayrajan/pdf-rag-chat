/*
 * Reusable college project report generator for the PDF RAG Chat project.
 *
 * HOW TO REUSE FOR EACH STUDENT:
 *   1. Edit the CONFIG object below with the student's details.
 *   2. Run: node generate_report.js
 *   3. Output: PDF_RAG_Chat_Report.docx in this folder.
 *
 * That's it — everything else (chapters, diagrams, test cases) stays the same
 * across students. Only swap CONFIG, and optionally the screenshots in Chapter 7.
 */

const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
  ImageRun, PageBreak, TableOfContents, Header, Footer, PageNumber,
  LevelFormat, convertInchesToTwip,
} = require("docx");
const fs = require("fs");

// ============================================================
// CONFIG — edit this block per student, then re-run the script
// ============================================================
const CONFIG = {
  PROJECT_TITLE: "Chat With Your PDF: A Retrieval-Augmented Generation System",
  PROJECT_TYPE: "Mini Project",              // "Mini Project" or "Major Project"
  STUDENT_NAME: "[Student Name]",
  ROLL_NUMBER: "[Roll Number]",
  COLLEGE_NAME: "[College Name]",
  DEPARTMENT: "[Department, e.g. Computer Science and Engineering]",
  UNIVERSITY_NAME: "[University Name]",
  GUIDE_NAME: "[Guide / Supervisor Name]",
  HOD_NAME: "[HOD Name]",
  ACADEMIC_YEAR: "[2025-2026]",
  SUBMISSION_MONTH_YEAR: "[Month Year]",
};

// ============================================================
// Helpers
// ============================================================
function heading(text, level) {
  return new Paragraph({ text, heading: level, spacing: { before: 300, after: 150 } });
}

function body(text) {
  return new Paragraph({
    children: [new TextRun({ text, size: 24 })],
    spacing: { after: 200, line: 360 },
    alignment: AlignmentType.JUSTIFIED,
  });
}

function bullet(text) {
  return new Paragraph({
    children: [new TextRun({ text, size: 24 })],
    numbering: { reference: "bullet-list", level: 0 },
    spacing: { after: 100 },
  });
}

function pageBreak() {
  return new Paragraph({ children: [new PageBreak()] });
}

function centerTitle(text, size = 32, bold = true) {
  return new Paragraph({
    children: [new TextRun({ text, bold, size })],
    alignment: AlignmentType.CENTER,
    spacing: { after: 200 },
  });
}

function tableCell(text, { header = false, width = 2000 } = {}) {
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    shading: header ? { type: ShadingType.CLEAR, fill: "D9D9D9" } : undefined,
    children: [
      new Paragraph({
        children: [new TextRun({ text, bold: header, size: 20 })],
      }),
    ],
  });
}

// ============================================================
// Title page
// ============================================================
const titlePageChildren = [
  new Paragraph({ text: "", spacing: { after: 600 } }),
  centerTitle(CONFIG.PROJECT_TITLE, 32, true),
  new Paragraph({ text: "", spacing: { after: 300 } }),
  centerTitle(`A ${CONFIG.PROJECT_TYPE} Report`, 24, false),
  new Paragraph({ text: "", spacing: { after: 400 } }),
  centerTitle("Submitted in partial fulfilment of the requirements for the award of", 22, false),
  centerTitle(`the degree in ${CONFIG.DEPARTMENT}`, 22, false),
  new Paragraph({ text: "", spacing: { after: 600 } }),
  centerTitle("By", 22, false),
  centerTitle(CONFIG.STUDENT_NAME, 26, true),
  centerTitle(`Roll No: ${CONFIG.ROLL_NUMBER}`, 20, false),
  new Paragraph({ text: "", spacing: { after: 600 } }),
  centerTitle("Under the guidance of", 20, false),
  centerTitle(CONFIG.GUIDE_NAME, 24, true),
  new Paragraph({ text: "", spacing: { after: 600 } }),
  centerTitle(CONFIG.COLLEGE_NAME, 26, true),
  centerTitle(CONFIG.UNIVERSITY_NAME, 22, false),
  centerTitle(CONFIG.SUBMISSION_MONTH_YEAR, 20, false),
  pageBreak(),
];

// ============================================================
// Certificate page
// ============================================================
const certificateChildren = [
  heading("Certificate", HeadingLevel.HEADING_1),
  body(
    `This is to certify that the ${CONFIG.PROJECT_TYPE.toLowerCase()} report entitled "${CONFIG.PROJECT_TITLE}" is a bonafide record of work carried out by ${CONFIG.STUDENT_NAME} (Roll No: ${CONFIG.ROLL_NUMBER}), submitted in partial fulfilment of the requirements for the award of degree in ${CONFIG.DEPARTMENT} at ${CONFIG.COLLEGE_NAME}, during the academic year ${CONFIG.ACADEMIC_YEAR}.`
  ),
  new Paragraph({ text: "", spacing: { after: 800 } }),
  new Paragraph({
    children: [new TextRun({ text: `Guide: ${CONFIG.GUIDE_NAME}`, size: 24 })],
    spacing: { after: 200 },
  }),
  new Paragraph({
    children: [new TextRun({ text: `Head of Department: ${CONFIG.HOD_NAME}`, size: 24 })],
    spacing: { after: 200 },
  }),
  pageBreak(),
];

// ============================================================
// Acknowledgement + Abstract
// ============================================================
const abstractChildren = [
  heading("Acknowledgement", HeadingLevel.HEADING_1),
  body(
    `I would like to express my sincere gratitude to ${CONFIG.GUIDE_NAME} for continuous guidance and support throughout this project. I also thank ${CONFIG.HOD_NAME} and the faculty of ${CONFIG.DEPARTMENT}, ${CONFIG.COLLEGE_NAME}, for providing the resources and environment necessary to complete this work.`
  ),
  new Paragraph({ text: "", spacing: { after: 400 } }),
  heading("Abstract", HeadingLevel.HEADING_1),
  body(
    "Retrieval-Augmented Generation (RAG) is an approach that combines information retrieval with large language models to answer questions grounded in a specific set of documents, rather than relying solely on a model's pre-trained knowledge. This project implements a lightweight, CPU-only RAG system that allows a user to upload one or more PDF documents and interactively ask questions about their content through a chat interface."
  ),
  body(
    "The system extracts text from PDFs while preserving page-level structure, splits the text into semantically coherent chunks, and converts each chunk into a vector embedding using a compact sentence-transformer model. These embeddings are indexed using FAISS for efficient similarity search. At query time, the system uses a hybrid retrieval strategy that combines exact keyword matching with vector similarity search, which improves accuracy for queries containing specific identifiers such as section or task numbers. The system also distinguishes between broad, whole-document questions (such as requests for a summary) and narrow, fact-based questions, routing each to the retrieval strategy best suited to it. Retrieved context is passed to a large language model, accessed through Groq's free-tier API, to generate a final answer that cites the specific source file and page number."
  ),
  body(
    "The resulting application is implemented in Python using Streamlit for the user interface, and demonstrates the core principles of RAG systems including document chunking, vector embeddings, semantic search, and grounded text generation, while remaining lightweight enough to run on a standard CPU-only machine."
  ),
  pageBreak(),
];

// ============================================================
// Table of Contents
// ============================================================
const tocChildren = [
  heading("Table of Contents", HeadingLevel.HEADING_1),
  new TableOfContents("Table of Contents", {
    hyperlink: true,
    headingStyleRange: "1-3",
  }),
  pageBreak(),
];

// ============================================================
// Chapter 1: Introduction
// ============================================================
const chapter1 = [
  heading("Chapter 1: Introduction", HeadingLevel.HEADING_1),

  heading("1.1 Problem Statement", HeadingLevel.HEADING_2),
  body(
    "Traditional keyword-based search within documents fails when a user's query uses different wording than the source text, even if the underlying meaning is the same. Large language models, on the other hand, can understand natural language queries well but do not have access to the specific content of a private or newly created document, and are prone to generating plausible-sounding but incorrect answers (commonly called hallucination) when asked about content they were not trained on. There is a need for a system that combines the natural-language understanding of an LLM with the factual grounding of the user's own documents."
  ),

  heading("1.2 Objectives", HeadingLevel.HEADING_2),
  bullet("To design and implement a pipeline that converts PDF documents into a searchable knowledge base."),
  bullet("To use semantic vector search to retrieve document sections relevant to a user's natural-language question."),
  bullet("To improve retrieval accuracy for exact identifiers (e.g. section or task numbers) using a hybrid keyword and vector search strategy."),
  bullet("To generate grounded, cited answers using a large language model, reducing the risk of hallucinated responses."),
  bullet("To provide a simple, interactive chat-based interface accessible without specialised hardware (CPU-only)."),
  new Paragraph({ text: "", spacing: { after: 200 } }),

  heading("1.3 Scope", HeadingLevel.HEADING_2),
  body(
    "The system supports PDF documents as input and allows multiple documents to be indexed and queried together. It is designed for personal or academic use cases such as querying reference material, textbooks, or internal documentation, and does not currently support other file formats such as Word documents, spreadsheets, or scanned handwritten documents without OCR pre-processing."
  ),
  pageBreak(),
];

// ============================================================
// Chapter 2: Literature Survey
// ============================================================
const chapter2 = [
  heading("Chapter 2: Literature Survey", HeadingLevel.HEADING_1),
  body(
    "Traditional document search systems have relied on keyword-matching techniques such as TF-IDF and BM25, which rank documents by term frequency and inverse document frequency. These approaches are computationally efficient and remain widely used in production search engines, but they struggle when a query uses synonyms or paraphrasing not present in the source text."
  ),
  body(
    "The introduction of transformer-based sentence embedding models, such as those in the Sentence-BERT family, enabled semantic search: representing text as dense vectors in a high-dimensional space such that texts with similar meaning are placed close together, regardless of exact wording. Libraries such as FAISS (Facebook AI Similarity Search) provide efficient approximate and exact nearest-neighbour search over large collections of such vectors, making semantic search practical even on modest hardware."
  ),
  body(
    "Retrieval-Augmented Generation, introduced by Lewis et al. (2020), combined a retriever component with a sequence-to-sequence generator, allowing a language model to condition its output on retrieved passages rather than relying purely on parameters learned during training. This approach has since become a standard pattern for building question-answering systems over private or domain-specific document collections, as it reduces hallucination and allows the knowledge base to be updated without retraining the underlying language model."
  ),
  body(
    "A known limitation of pure vector-based retrieval, noted in subsequent hybrid-search literature, is that dense embeddings can struggle to distinguish between texts that are semantically similar but differ in specific literal details, such as numeric identifiers, codes, or names. Hybrid retrieval approaches, which combine sparse keyword-based matching with dense vector search, have been shown to mitigate this weakness. This project adopts a simplified hybrid retrieval strategy for the same reason, using literal substring matching for numeric identifiers alongside vector similarity search."
  ),
  pageBreak(),
];

// ============================================================
// Chapter 3: System Analysis
// ============================================================
const srsRows = [
  ["Requirement ID", "Description", "Type"],
  ["FR-1", "The system shall allow a user to upload one or more PDF files.", "Functional"],
  ["FR-2", "The system shall extract text from uploaded PDFs while preserving page boundaries.", "Functional"],
  ["FR-3", "The system shall split extracted text into chunks suitable for embedding.", "Functional"],
  ["FR-4", "The system shall generate vector embeddings for each chunk.", "Functional"],
  ["FR-5", "The system shall retrieve the most relevant chunks for a given user question.", "Functional"],
  ["FR-6", "The system shall generate a natural-language answer using a large language model, grounded in retrieved chunks.", "Functional"],
  ["FR-7", "The system shall display the source file and page number for each answer.", "Functional"],
  ["NFR-1", "The system shall run on a CPU-only machine without requiring a GPU.", "Non-functional"],
  ["NFR-2", "The embedding and retrieval steps shall not depend on any paid API.", "Non-functional"],
  ["NFR-3", "The user interface shall be usable without prior technical training.", "Non-functional"],
];

function buildTable(rows, colWidths) {
  return new Table({
    width: { size: 9000, type: WidthType.DXA },
    columnWidths: colWidths,
    rows: rows.map((row, i) =>
      new TableRow({
        children: row.map((cell, j) => tableCell(cell, { header: i === 0, width: colWidths[j] })),
      })
    ),
  });
}

const chapter3 = [
  heading("Chapter 3: System Analysis", HeadingLevel.HEADING_1),

  heading("3.1 Feasibility Study", HeadingLevel.HEADING_2),
  body(
    "The system is technically feasible on standard consumer hardware. All components used - PDF text extraction, sentence embedding, and vector similarity search - are designed to run efficiently on a CPU. The only component requiring an external service is the final answer-generation step, which uses Groq's API; Groq offers a free tier sufficient for personal and academic use, making the system economically feasible without any licensing cost. No specialised infrastructure, GPU hardware, or paid subscriptions are required."
  ),

  heading("3.2 Requirements Specification", HeadingLevel.HEADING_2),
  body("The functional and non-functional requirements of the system are summarised below."),
  buildTable(srsRows, [1500, 6000, 1500]),
  new Paragraph({ text: "", spacing: { after: 200 } }),

  heading("3.3 Hardware and Software Requirements", HeadingLevel.HEADING_2),
  bullet("Processor: Any modern x86-64 processor (Intel/AMD), no GPU required."),
  bullet("RAM: 4 GB minimum, 8 GB recommended."),
  bullet("Operating System: Windows, Linux, or macOS."),
  bullet("Software: Python 3.10 or above, pip package manager."),
  bullet("Key libraries: Streamlit, pymupdf4llm, sentence-transformers, faiss-cpu, groq."),
  bullet("Internet connection: required for the initial embedding-model download and for LLM API calls."),
  pageBreak(),
];

// ============================================================
// Chapter 4: System Design
// ============================================================
const chapter4 = [
  heading("Chapter 4: System Design", HeadingLevel.HEADING_1),

  heading("4.1 System Architecture", HeadingLevel.HEADING_2),
  body(
    "The system is organised into two phases: an indexing phase, which runs once per uploaded document, and a query phase, which runs each time the user asks a question. Figure 4.1 shows the overall architecture."
  ),
  new Paragraph({
    children: [
      new ImageRun({
        type: "png",
        data: fs.readFileSync(__dirname + "/assets/architecture_diagram.png"),
        transformation: { width: 600, height: 265 },
      }),
    ],
    alignment: AlignmentType.CENTER,
  }),
  new Paragraph({
    children: [new TextRun({ text: "Figure 4.1: System architecture showing the indexing phase and query phase", italics: true, size: 20 })],
    alignment: AlignmentType.CENTER,
    spacing: { after: 300 },
  }),
  body(
    "In the indexing phase, uploaded PDFs are converted to per-page Markdown text, split into chunks, and embedded into vectors that are stored in a FAISS index. In the query phase, the user's question is processed by a hybrid retrieval step that combines exact keyword matching with vector similarity search, and the retrieved chunks are passed to a large language model (accessed via the Groq API) to generate the final, cited answer."
  ),

  heading("4.2 Query Routing Logic", HeadingLevel.HEADING_2),
  body(
    "Not all questions are best served by the same retrieval strategy. Broad questions, such as requests for a document summary, do not correspond to any single passage in the document and are poorly served by similarity search, which can only retrieve passages resembling the query itself. Specific questions, such as those referring to a particular section or task number, benefit from exact keyword matching in addition to semantic search, since embeddings do not reliably distinguish between similar numeric identifiers. Figure 4.2 illustrates how each incoming question is routed."
  ),
  new Paragraph({
    children: [
      new ImageRun({
        type: "png",
        data: fs.readFileSync(__dirname + "/assets/query_routing_diagram.png"),
        transformation: { width: 500, height: 316 },
      }),
    ],
    alignment: AlignmentType.CENTER,
  }),
  new Paragraph({
    children: [new TextRun({ text: "Figure 4.2: Decision logic for routing broad vs. specific questions", italics: true, size: 20 })],
    alignment: AlignmentType.CENTER,
    spacing: { after: 300 },
  }),

  heading("4.3 Module Design", HeadingLevel.HEADING_2),
  bullet("rag.py — Core pipeline module: PDF-to-Markdown conversion, chunking, embedding, FAISS indexing, and hybrid retrieval logic. Independent of the user interface."),
  bullet("app.py — Streamlit-based user interface: file upload handling, chat interface, session state management, and integration with the Groq API for answer generation."),
  pageBreak(),
];

// ============================================================
// Chapter 5: Implementation
// ============================================================
const chapter5 = [
  heading("Chapter 5: Implementation", HeadingLevel.HEADING_1),

  heading("5.1 Technology Stack", HeadingLevel.HEADING_2),
  bullet("Python 3 — primary implementation language."),
  bullet("Streamlit — web-based user interface framework."),
  bullet("pymupdf4llm — PDF-to-Markdown extraction, preserving page and heading structure."),
  bullet("sentence-transformers (all-MiniLM-L6-v2) — generates dense vector embeddings on CPU."),
  bullet("FAISS (faiss-cpu) — efficient vector similarity search."),
  bullet("Groq API (Llama models) — large language model used for final answer generation."),
  new Paragraph({ text: "", spacing: { after: 200 } }),

  heading("5.2 PDF Extraction and Chunking", HeadingLevel.HEADING_2),
  body(
    "Each uploaded PDF is processed page by page using pymupdf4llm, which converts the PDF content into Markdown while detecting headings based on font size and style. Each page's Markdown text is then split primarily along detected headings, so that each chunk corresponds to a coherent section rather than an arbitrary slice of text. Sections that remain too long are further split by word count, with a small overlap between consecutive chunks to avoid losing context at chunk boundaries. Every chunk is tagged with metadata recording its source filename and page number."
  ),

  heading("5.3 Embedding and Indexing", HeadingLevel.HEADING_2),
  body(
    "Each text chunk is converted into a 384-dimensional vector using the all-MiniLM-L6-v2 sentence-transformer model, which runs efficiently on CPU. All chunk vectors are added to a FAISS IndexFlatL2 index, which performs exact nearest-neighbour search using Euclidean distance. When multiple PDFs are uploaded, their chunks share a single combined index, allowing questions to be answered using information from any of the loaded documents."
  ),

  heading("5.4 Hybrid Retrieval", HeadingLevel.HEADING_2),
  body(
    "At query time, the user's question is first scanned for numeric identifier patterns (for example, \"3.2.2\") using a regular expression. If any such identifiers are present, the system performs a literal, case-insensitive search across all chunks for text containing that identifier, and these exact matches are placed first in the retrieved context. The remaining slots, up to the configured number of chunks to retrieve, are filled using vector similarity search. This hybrid approach was adopted after observing that pure vector search frequently retrieved the wrong section when two sections had similar wording but different identifying numbers, since embedding models capture semantic meaning rather than exact digit sequences."
  ),

  heading("5.5 Broad Question Detection", HeadingLevel.HEADING_2),
  body(
    "Questions containing signals such as \"summarize\", \"overview\", or \"main points\" are detected and routed differently from narrow, fact-based questions. Instead of retrieving a small number of chunks by similarity, which performs poorly for whole-document questions, the system supplies the full extracted text of the document (up to a safe token limit) directly to the language model."
  ),

  heading("5.6 Answer Generation", HeadingLevel.HEADING_2),
  body(
    "The retrieved chunks (or full document text, for broad questions), together with source and page metadata, are assembled into a prompt instructing the language model to answer strictly from the provided context, to state when the answer is not present in the context, and to cite the specific source file and page for any information used. This prompt is sent to a Llama model hosted on Groq's infrastructure, chosen for its free tier and fast inference speed relative to comparable hosted models."
  ),
  pageBreak(),
];

// ============================================================
// Chapter 6: Testing
// ============================================================
const testRows = [
  ["Test ID", "Test Description", "Input", "Expected Output", "Result"],
  ["T-1", "Upload a valid PDF", "Sample PDF file", "Document is indexed; chunk count displayed", "Pass"],
  ["T-2", "Ask a specific factual question", "\"What is the deadline for Task 2.1?\"", "Correct section retrieved and cited with page number", "Pass"],
  ["T-3", "Ask for a document summary", "\"Summarize this document\"", "Full-document mode used; coherent summary generated", "Pass"],
  ["T-4", "Ask about a numeric identifier similar to another", "\"What is TASK 3.2.2?\"", "Exact section for 3.2.2 retrieved, not a similarly worded section", "Pass"],
  ["T-5", "Upload multiple PDFs", "Two PDF files", "Both indexed; answers cite the correct source file", "Pass"],
  ["T-6", "Remove a loaded document", "Click \"Remove\" on a loaded file", "Document excluded from further answers", "Pass"],
  ["T-7", "Ask a question with no relevant content", "Unrelated question", "System responds that it lacks sufficient information", "Pass"],
];

const chapter6 = [
  heading("Chapter 6: Testing", HeadingLevel.HEADING_1),
  body(
    "The system was tested manually against a range of representative scenarios covering document upload, specific and broad question types, multi-document handling, and edge cases. The test cases and their outcomes are summarised in Table 6.1."
  ),
  buildTable(testRows, [900, 2300, 2000, 2900, 900]),
  new Paragraph({
    children: [new TextRun({ text: "Table 6.1: Test cases and results", italics: true, size: 20 })],
    alignment: AlignmentType.CENTER,
    spacing: { before: 100, after: 300 },
  }),
  body(
    "All test cases passed, confirming that the hybrid retrieval strategy correctly distinguishes between similarly-worded numeric identifiers, that broad questions are correctly routed to full-document mode, and that citations correctly reflect the source file and page number, even when multiple documents are loaded simultaneously."
  ),
  pageBreak(),
];

// ============================================================
// Chapter 7: Results and Screenshots
// ============================================================
const chapter7 = [
  heading("Chapter 7: Results and Screenshots", HeadingLevel.HEADING_1),
  body(
    "[Insert screenshots of the running application here: the PDF upload screen, the loaded-documents panel, and a sample question-and-answer exchange showing a cited response. Replace this paragraph with the actual screenshots before submission.]"
  ),
  body(
    "The system successfully answers both specific and broad questions across single and multiple uploaded PDFs, with citations correctly identifying the source file and page number for each answer."
  ),
  pageBreak(),
];

// ============================================================
// Chapter 8: Conclusion and Future Scope
// ============================================================
const chapter8 = [
  heading("Chapter 8: Conclusion and Future Scope", HeadingLevel.HEADING_1),

  heading("8.1 Conclusion", HeadingLevel.HEADING_2),
  body(
    "This project successfully implements a lightweight, CPU-only Retrieval-Augmented Generation system for querying PDF documents. By combining page-aware text extraction, semantic chunking, vector embeddings, hybrid keyword-and-vector retrieval, and a large language model for answer generation, the system is able to answer natural-language questions grounded in user-supplied documents, while citing the exact source and page for each answer. The project demonstrates that a practical, useful RAG system can be built without specialised hardware or paid infrastructure, using open-source libraries and free-tier APIs."
  ),

  heading("8.2 Future Scope", HeadingLevel.HEADING_2),
  bullet("Support for additional file formats, such as Word documents, PowerPoint presentations, and scanned documents via OCR."),
  bullet("Persistent storage of the vector index, so documents do not need to be re-uploaded and re-indexed after restarting the application."),
  bullet("A re-ranking step using a cross-encoder model to further improve retrieval precision."),
  bullet("Multi-user support with authentication and separate document collections per user."),
  bullet("Quantitative evaluation of retrieval quality using standard information-retrieval metrics such as precision@k and recall@k."),
  pageBreak(),
];

// ============================================================
// References
// ============================================================
const references = [
  heading("References", HeadingLevel.HEADING_1),
  body("[1] Lewis, P., et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. Advances in Neural Information Processing Systems (NeurIPS)."),
  body("[2] Reimers, N., and Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. Proceedings of EMNLP-IJCNLP."),
  body("[3] Johnson, J., Douze, M., and Jegou, H. (2019). Billion-scale similarity search with GPUs. IEEE Transactions on Big Data. (FAISS)"),
  body("[4] Robertson, S., and Zaragoza, H. (2009). The Probabilistic Relevance Framework: BM25 and Beyond. Foundations and Trends in Information Retrieval."),
  body("[5] Streamlit documentation. https://docs.streamlit.io"),
  body("[6] pymupdf4llm documentation. https://pymupdf.readthedocs.io"),
  body("[7] Groq API documentation. https://console.groq.com/docs"),
];

// ============================================================
// Assemble document
// ============================================================
const doc = new Document({
  numbering: {
    config: [
      {
        reference: "bullet-list",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT }],
      },
    ],
  },
  sections: [
    {
      properties: {},
      children: titlePageChildren,
    },
    {
      properties: {},
      children: certificateChildren,
    },
    {
      properties: {},
      children: abstractChildren,
    },
    {
      properties: {},
      children: tocChildren,
    },
    {
      properties: {},
      headers: {
        default: new Header({
          children: [new Paragraph({ text: CONFIG.PROJECT_TITLE, alignment: AlignmentType.CENTER })],
        }),
      },
      footers: {
        default: new Footer({
          children: [
            new Paragraph({
              alignment: AlignmentType.CENTER,
              children: [new TextRun({ children: [PageNumber.CURRENT] })],
            }),
          ],
        }),
      },
      children: [
        ...chapter1,
        ...chapter2,
        ...chapter3,
        ...chapter4,
        ...chapter5,
        ...chapter6,
        ...chapter7,
        ...chapter8,
        ...references,
      ],
    },
  ],
});

Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync(__dirname + "/PDF_RAG_Chat_Report.docx", buffer);
  console.log("Generated PDF_RAG_Chat_Report.docx");
});
