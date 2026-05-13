# WHO Guideline PDFs — Data Directory

Place your WHO (World Health Organization) guideline PDF files in this directory.

## Recommended PDFs

- WHO Pocket Book of Hospital Care for Children
- WHO Model Formulary for Children
- WHO Guidelines for the Treatment of Malaria
- WHO Guidelines for the Treatment of Tuberculosis
- WHO Integrated Management of Childhood Illness (IMCI) Chart Booklet
- WHO Essential Medicines List

You can download official WHO publications free of charge from:
https://www.who.int/publications/

## After Adding PDFs

Run the ingestion script from the `backend/` directory:

```bash
cd backend
source venv/bin/activate
python ingest_pdfs.py
```

This will:
1. Extract text from each PDF using PyMuPDF
2. Split the text into overlapping chunks
3. Embed each chunk using the all-MiniLM-L6-v2 sentence transformer
4. Store all embeddings in a local FAISS vector index

The vector store is saved to `backend/vector_store/` and will be used
automatically by the VoiceDoc backend when answering queries.

## Notes

- Ingestion only needs to be run once per set of documents.
- Re-running the script will add new documents without removing existing ones.
- Larger PDFs take longer to process but improve diagnostic accuracy.
- All processing is done 100% locally — no data is sent to any external server.


