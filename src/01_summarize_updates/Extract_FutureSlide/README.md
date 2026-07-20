TASK: Identify update points ("motivations") for subsequent Future of Work determinations.

 1) Extract and format contents from motivating documents 

APPROACH:
 1) Convert source documents to strict markdown.
 2) Filter strict markdown, removing binary data, base64 content, formatting information etc.
 3) Upload original document to vector-store.
 4) Load cleaned markdown content into prompt.
 5) Successively prompt the LLM to identify points from the document, progressing by slide, page, or section.
 6) Collate updates into a single JSON file.

Required:
- requests

