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

# required file structure to run:
0000_raw\
	└── data\
		└── 0000_raw\
			└── GSBPM_v5_1.pdf
	000_convertPDF2MD.ps1
	001_LLM_extract_updates_into_json.py

# RUNNING STEP - Step 1
*prerun: 
 replace the location within marker:$pandocExe = "" 
	in 000_convertPDF2MD.ps1 with the location of pandoc.exe in ur os.
 1) go into miniforge
 2) step 1: extracting md from pdf
 	2.1) run: cd ..\00_extract_gsbpm  *ps: ..\ is where the folder located
 	2.2) run: pwsh .\000_convertPDF2MD.ps1


# RUNNING STEP - Step 2

 1) go into miniforge
 2) run: cd ..\00_extract_gsbpm  *ps: ..\ is where the folder located 
 3) enter into conda enviroment. run: conda activate dsBase
 4) run: python 001_LLM_extract_updates_into_json.py