import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

VECTOR_STORE_PATH = os.path.join(os.path.dirname(__file__), "vector_store")
INDEX_FILE = os.path.join(VECTOR_STORE_PATH, "index.faiss")
CHUNKS_FILE = os.path.join(VECTOR_STORE_PATH, "chunks.json")
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384  # all-MiniLM-L6-v2 output dimension

SYSTEM_PROMPT = (
    "You are VoiceDoc, an offline AI assistant helping community health workers in rural areas. "
    "You help triage symptoms, check basic drug safety, and explain treatment steps. "
    "You are NOT a replacement for a licensed doctor. "
    "Always advise the health worker to escalate to a physician for serious cases. "
    "Be concise, factual, and use simple language. "
    "Only use information from the provided context."
)


class RAGEngine:
    def __init__(self, vector_store_path: str = VECTOR_STORE_PATH):
        self.vector_store_path = vector_store_path
        os.makedirs(self.vector_store_path, exist_ok=True)

        self.index_file = os.path.join(self.vector_store_path, "index.faiss")
        self.chunks_file = os.path.join(self.vector_store_path, "chunks.json")

        print("[RAGEngine] Loading embedding model...")
        self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        print("[RAGEngine] Embedding model loaded.")

        if os.path.exists(self.index_file) and os.path.exists(self.chunks_file):
            print("[RAGEngine] Loading existing FAISS index...")
            self.index = faiss.read_index(self.index_file)
            with open(self.chunks_file, "r", encoding="utf-8") as f:
                self.chunks = json.load(f)
            print(f"[RAGEngine] Loaded {len(self.chunks)} chunks from disk.")
        else:
            print("[RAGEngine] No existing index found. Starting fresh.")
            self.index = faiss.IndexFlatL2(EMBEDDING_DIM)
            self.chunks = []  # list of {"text": str, "source": str}

    def _split_text(self, text: str, chunk_size: int = 500, overlap: int = 50):
        """Split text into overlapping chunks."""
        chunks = []
        start = 0
        text_length = len(text)
        while start < text_length:
            end = min(start + chunk_size, text_length)
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start += chunk_size - overlap
        return chunks

    def ingest_text(self, text: str, source: str) -> int:
        """
        Split text into chunks, embed, and add to FAISS index.

        Args:
            text: Raw text to ingest.
            source: Filename or identifier for the source document.

        Returns:
            Number of new chunks added.
        """
        raw_chunks = self._split_text(text)
        if not raw_chunks:
            return 0

        print(f"[RAGEngine] Embedding {len(raw_chunks)} chunks from '{source}'...")
        embeddings = self.model.encode(raw_chunks, show_progress_bar=True)
        embeddings = np.array(embeddings, dtype="float32")

        self.index.add(embeddings)
        for chunk_text in raw_chunks:
            self.chunks.append({"text": chunk_text, "source": source})

        self._save()
        print(f"[RAGEngine] Added {len(raw_chunks)} chunks. Total: {len(self.chunks)}")
        return len(raw_chunks)

    def _save(self):
        """Persist FAISS index and chunk metadata to disk."""
        faiss.write_index(self.index, self.index_file)
        with open(self.chunks_file, "w", encoding="utf-8") as f:
            json.dump(self.chunks, f, ensure_ascii=False, indent=2)

    def query(self, question: str, top_k: int = 5) -> list:
        """
        Retrieve the top_k most relevant text chunks for a question.

        Args:
            question: The user's query.
            top_k: Number of chunks to return.

        Returns:
            List of relevant text strings.
        """
        if self.index.ntotal == 0:
            return []

        question_embedding = self.model.encode([question])
        question_embedding = np.array(question_embedding, dtype="float32")

        k = min(top_k, self.index.ntotal)
        distances, indices = self.index.search(question_embedding, k)

        results = []
        for idx in indices[0]:
            if 0 <= idx < len(self.chunks):
                results.append(self.chunks[idx]["text"])
        return results

    def build_prompt(self, question: str, context_chunks: list) -> str:
        """
        Construct the full LLM prompt with system instructions, context, and question.

        Args:
            question: The health worker's query.
            context_chunks: List of retrieved context strings.

        Returns:
            A complete prompt string ready to send to Ollama.
        """
        context_section = ""
        if context_chunks:
            formatted = "\n\n".join(
                f"[Source {i+1}]\n{chunk}" for i, chunk in enumerate(context_chunks)
            )
            context_section = f"\n\nCONTEXT:\n{formatted}"
        else:
            context_section = "\n\nCONTEXT:\nNo specific source documents matched this query. Answer based on general medical knowledge and advise consulting a physician."

        prompt = (
            f"{SYSTEM_PROMPT}"
            f"{context_section}"
            f"\n\nQUESTION: {question}"
            f"\n\nANSWER (be concise and structured):"
        )
        return prompt
