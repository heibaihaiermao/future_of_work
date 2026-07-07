import re
import yaml
import pandas as pd




with open("2025-09-23_-_updated_descriptions.json",'r',encoding='utf-8') as fil:
    js = json.load(fil)

d = pd.DataFrame((d_i.values() for d_i in js), columns=js[0].keys())
dsub = d[d['id'].apply(float) < 4]

def process(s):
    return re.sub(r"\\u....", "-", s.replace(r"\n", '\n    ').replace("\n    \\","").replace(r"\ "," "))

dsub['yaml'] = dsub['implicated updates'].apply(yaml.safe_dump).apply(process)