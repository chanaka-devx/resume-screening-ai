This document carries the notes I took while researching on the internet for building this AI tool. 

## 1. Sentence Transformers
Sentence Transformers refer to both a highly efficient neural network architecture (like SBERT) and the popular Python library used to implement it. They process text to generate **embeddings**—dense mathematical vectors that capture the deep semantic meaning of a sentence. Because they use a Siamese network architecture, they allow for lightning-fast comparisons between thousands of sentences, forming the backbone of semantic search and Retrieval-Augmented Generation (RAG).

## 2. spaCy
**spaCy** is an industrial-strength, open-source Python library for advanced NLP. Built for production rather than research, it is highly optimized (using Cython) for speed and memory efficiency. It provides pre-trained pipelines for fundamental text processing tasks, including Tokenization, Part-of-Speech tagging, lemmatization, and Named Entity Recognition (NER). It is widely used for extracting structured linguistic rules from unstructured text.

## 3. PDF Parsing Libraries
Extracting reliable data from PDFs is notoriously difficult because they are presentation-oriented. The ecosystem offers specialized tools depending on the need:
*   **Text Extraction:** `PyMuPDF` (fast C-bindings) and `pypdf` (pure Python) for raw text ripping.
*   **AI/RAG Ingestion:** `Unstructured` and `LlamaParse` for preserving document hierarchy (headers, paragraphs).
*   **Table Extraction:** `pdfplumber` and `Camelot` for using spatial bounding boxes to rebuild data tables.
*   **OCR:** `Tesseract` and `EasyOCR` for extracting text from scanned images using computer vision.

## 4. Resume Parsing Techniques
Turning unstructured CVs into a clean database schema involves handling massive formatting variances (like complex tables and multi-column layouts). Techniques include:
*   **Legacy Rule-Based:** Relying on regular expressions and hardcoded keyword dictionaries.
*   **Statistical NLP (NER):** Training models to recognize the contextual placement of entities like "Job Title" or "Skill".
*   **Modern Generative AI:** Using spatial layout models (like LayoutLM) or passing raw text directly into Large Language Models (LLMs) instructed to return the data strictly formatted to a predefined JSON schema.

## 5. Semantic Similarity
Semantic similarity is the metric used to determine how close two pieces of text are in *meaning*, moving beyond exact keyword matching. Once text is converted into vector embeddings, they are plotted in a high-dimensional vector space. Systems typically calculate the **Cosine Similarity**—measuring the angle between the two vectors. A smaller angle indicates a highly similar semantic meaning, enabling intelligent matching systems.