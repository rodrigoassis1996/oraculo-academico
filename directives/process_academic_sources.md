# SOP: Process Academic Sources

This directive describes how to ingest and process various academic sources (PDFs, URLs, DOCX, CSV, TXT) to prepare them for the knowledge base.

## Goal
Extract clean text from provided files or URLs while maintaining as much academic context as possible.

## Inputs
- File paths or URLs to academic content.

## Tools (Execution Layer)
- `execution/document_ingestion.py`: Standalone script to process sources.

## Steps

1.  **Identify Source**: Determine if the input is a URL or a local file.
2.  **Run Ingestion**: Call `execution/document_ingestion.py` with the appropriate arguments.
    - For URLs: `python execution/document_ingestion.py --url <URL>`
    - For Files: `python execution/document_ingestion.py --file <PATH>`
3.  **Check Output**: The script will output the processed text or save it to a temporary file in `.tmp/`.
4.  **Error Handling**:
    - If a URL fails due to status codes, wait and retry (handled by `UploadManager` logic in the script).
    - If a file is too large (>10MB), inform the user and request a smaller version or split.
    - If no text is extracted, check for scanned PDFs (OCR might be needed).

## Learning Log
*(To be updated by the agent)*
- Initial version created.
