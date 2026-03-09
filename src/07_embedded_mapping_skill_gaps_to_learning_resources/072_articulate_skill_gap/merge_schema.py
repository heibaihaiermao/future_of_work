import json
from os import listdir
from itertools import tee
from dotenv import load_dotenv
load_dotenv("../../py.env")


from get_schema import JSONSchemaIdentifier
identifier = JSONSchemaIdentifier()

from sys import path
path.append("../../05_forecast_skill_gaps_of_wd")
from assistant import Assistant

def load_json(path):
    with open(path, 'r', encoding="utf-8-sig") as fil:
        return json.load(fil)


input_dir = "data/0721_identified/"
output_dir = "data/0722_standard/"
# Collect all input JSON paths
json_files = filter(lambda s: s.endswith("json"),
                    listdir(input_dir))
json_files = map(input_dir.__add__, json_files)
json_files = list(json_files)

# Generate set of unique schema
schemas = map(identifier.generate_schema, json_files)
schemas = set(map(json.dumps, schemas)) # set unique schemas.

schemas = map(json.loads, schemas)
schemas = list(schemas) # list of unique dictionary object (schemas)

# Query Agent for code that applies a common schema.
schematizer = Assistant("You are a highly methodical python coding agent that generates code to standardize JSON data into a common schema")

code = schematizer.send_message(f"Given the following schema: \n```{json.dumps(schemas)}```\n decide whether they are compatible and if so, write python code so to standardize the data in both schema. Respond only with python code. Name the function which standardizes the data \"apply_common_schema\"")

code = code.strip("```python")
exec(code)
schematizer.delete()

# Load relevant data.
output_files, json_data = tee(json_files, 2)

# Make output paths
output_files = map(lambda s: s.replace(input_dir, output_dir), output_files)

# Apply common schema to all input data
json_data = map(load_json, json_files)
standard_json = map(apply_common_schema, json_data)

# Write to output.
for output_path_i, output_data_i in zip(output_files, standard_json):
    with open(output_path_i, 'w', encoding="utf-8") as fil:
        json.dump(output_data_i,
                  fil,
                  ensure_ascii=False)

