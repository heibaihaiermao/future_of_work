# TASK
Convert PDFs that define GSBPM into structured JSON documents.

## Details
The GSBPM document outlines the key activities that an NSO conducts. A major portion of this lists a structured set of phases and sub-processes detailing the activities. There is additional information regarding the purpose of the standard and how it should be applied. Therefore, the GSPBM can be represented as a JSON object with the following structure.
```
{"preamble": <preamble text or LLM summary of non-structured content>,
 "Phases and sub-processes": [
	{"phase": {id,
	           title,
	           description,
	           sub-processes: [{id, title, description}]}}]}
``` 

# APPROACH
 1) Convert PDF to DOCX, then Convert DOCX to Markdown
 2) LLM extract from Markdown into JSON.

Step 1) are accomplished with the "000_convertPDF2MD.ps1" powershell script. This script leverages Microsoft Office Word (could be converted to Powerpoint or Excel) to import a PDF document, and save it as a DOCX. Then, using Pandoc the DOCX is converted to strict Markdown.

Step 2) leverages an LLM to extract the text of structured portion of the GSBPM into a JSON format. The non-structured part can be summarized by an LLM and captured in the "preamble" attribute of the above JSON schema.

## Requirements
 - Powershell7
 - Microsoft Word.
 - Python3

## Required Python packages
 - openai
 - dotenv

## Required AI
 - LLM useful for abstraction (e.g. GPT4.1 through Azure AI Foundry API)
