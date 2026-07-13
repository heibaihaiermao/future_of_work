Step name: Internal Courses in LMS
purpose: converting internal statcan course into json format 

needed additonal pacakge:
conda install -c conda-forge pymupdf
Also for python-docx

pseudo process: two main steps
step 1:
1.extracting information into json schema from pdf
2.extracting infroamtino into json scheme from docx
3.Combine all json into one file

step 2:
1.process these json information into universal course schema, with competencies added

output: courses_ai_competencies.json


 
