#!/usr/bin/env python3
"""
ingest_pdfs.py — Scan backend/data/ for WHO guideline PDFs and ingest them
into the VoiceDoc FAISS vector store.

Usage:
    python ingest_pdfs.py
"""

import os
import sys

# Ensure the backend package root is on the path when running standalone
sys.path.insert(0, os.path.dirname(__file__))

import fitz  # PyMuPDF
from rag_engine import RAGEngine

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def extract_text_from_pdf(pdf_path: str) -> tuple:
    """
    Extract all text from a PDF using PyMuPDF.

    Returns:
        (full_text: str, page_count: int)
    """
    doc = fitz.open(pdf_path)
    pages_text = []
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text("text")
        if text.strip():
            pages_text.append(text)
    doc.close()
    full_text = "\n".join(pages_text)
    return full_text, len(pages_text)


def main():
    if not os.path.isdir(DATA_DIR):
        print(f"[ERROR] Data directory not found: {DATA_DIR}")
        print("Create the directory and place WHO guideline PDFs inside it.")
        sys.exit(1)

    pdf_files = [f for f in os.listdir(DATA_DIR) if f.lower().endswith(".pdf")]

    if not pdf_files:
        print(f"[WARNING] No PDF files found in {DATA_DIR}")
        print("Place WHO guideline PDFs in that folder, then re-run this script.")
        sys.exit(0)

    print(f"Found {len(pdf_files)} PDF(s) in {DATA_DIR}\n")

    rag = RAGEngine()
    total_chunks = 0

    for filename in sorted(pdf_files):
        pdf_path = os.path.join(DATA_DIR, filename)
        print(f"Processing: {filename}")
        try:
            text, page_count = extract_text_from_pdf(pdf_path)
            print(f"  Extracted {page_count} pages, {len(text)} characters")
            if not text.strip():
                print(f"  [SKIP] No readable text found in {filename}")
                continue
            chunks_added = rag.ingest_text(text, source=filename)
            total_chunks += chunks_added
            print(f"  Added {chunks_added} chunks to vector store.\n")
        except Exception as e:
            print(f"  [ERROR] Failed to process {filename}: {e}\n")

    print(f"Ingestion complete. {total_chunks} total chunks added.")
    print("Vector store saved to vector_store/")


if __name__ == "__main__":
    main()
