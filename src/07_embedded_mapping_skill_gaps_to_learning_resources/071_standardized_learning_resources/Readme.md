step 071
Purpose: Standardrize three datasets from education station: DataCamp, CSPS and Onyxia into a consistent format with detailed competency information

files needed to run:
Makefile
data/imputed/dataCamp.json
data/imputed/csps.jsons
data/imputed/onlyxia.json
data/raw/dataCamp.json
filterCSPS.jq 
filterDataCamp.jq
fitlerOnlyxia.jq
join_competency_descriptions.json


input:

Makefile: the main file, combining the whole cleaning process together
data/imputed/dataCamp.json: raw data from datacamp, main input
data/imputed/csps.json: raw data for csps
data/imputed/onlyxia.json:raw data from onlyxia

data/raw/dataCamp.json: additional information from datacamp, more details

filterCSPS.jq:Standardrize CSPS information 
filterDataCamp.jq: Stamdardroze DataCamp information
fitlerOnlyxia.jq: standardrize Onlyxia information
join_competency_descriptions.json:Cleaning the competency profilS

Output:
data/standard/dataCamp.json
data/standard/csps.json
data/standard/onyxia.json



note for code: 
$@: the target file, output
data/standard/dataCamp.json: data/imputed/dataCamp.json  -> output: input


useful command:
conda env list: listing exisintg conda enviroment


enviroment setup:
1.just use the dbase

How to run:
1.start miniforge  
2.cd to the folder 
3.activate the specific enviroment
4. make


