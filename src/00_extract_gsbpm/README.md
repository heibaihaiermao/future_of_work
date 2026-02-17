# TASK
Convert PDFs that define GSBPM into structured JSON documents

# APPROACH
 1) Convert PDF to DOCX, then Convert DOCX to Markdown
 2) LLM extract from Markdown into JSON.

Step 1) are accomplished with the "000_convertPDF2MD.ps1" powershell script. This script leverages Microsoft Office Word (could be converted to Powerpoint or Excel) to import a PDF document, and save it as a DOCX. Then, using Pandoc the DOCX is converted to strict Markdown.

## Requirements
 - Powershell7
 - Microsoft Word.
 - 
