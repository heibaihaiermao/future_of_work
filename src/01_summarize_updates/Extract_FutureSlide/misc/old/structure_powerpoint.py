# preferred

from sys import path
path.append("../05_forecast_skill_gaps_of_wd")
from assistant import Assistant



from openai import AzureOpenAI
from dotenv import load_dotenv
from os import getenv, listdir
from glob import glob
from itertools import chain
from pickle import load as pload, dump as pdump
import json
import atexit

def load_prompt(path):
    with open(path, 'r', encoding="utf-8-sig") as fil:
        content  = fil.read()
    return content

# TODO: makefile use pandoc in a bash shell script to convert ppt to MD file
#       MD file is one of the 2 inputs here

if __name__ == "__main__":
    # Load prompt, gsbpm 
    load_dotenv("../py.env")
    prompt_path = "prompts/01_extract_updates.txt"
    gsbpm_json_path = "data/input/GSBPM_v5_2.json"
    
    system_prompt = {"role": "system",
                     "content": "My method of converting Powerpoint slides to markdown is pretty flawed. I've uploaded the original powerpoint presentation, and it can also be found in the vector store. Search through it and then help me produce a better conversion. Later in the prompt I'll also include the Pandoc-produced markdown text. I think an effective way to represent the powerpoint presentation is in JSON format, where 'slide-objects' will comprise a list."}

    prompt_content = load_prompt("data/raw/1. A glimpse of the future - Tier 2 Committee Visions for the future of the agency (2) - Copy.txt")
    user_prompt = {"role": "user",
                   "content": "Here is the markdown content \n```markdown\n" + prompt_content + "\n```"}
    #pack the prompt into one, may causing the ai read it as a json input data
    buddy = Assistant(json.dumps([system_prompt,
                                  user_prompt]))
    atexit.register(buddy.delete)
    
    #Maybe not pass the buddy argument as it's not theri when calling
    vs = buddy.client.vector_stores.create()
    def delete_vector_store(buddy):
        buddy.client.vector_stores.delete(vector_store_id=vs.id)
    atexit.register(delete_vector_store)

    #def delete_vector_store():
    #    buddy.client.vector_stores.delete(vector_store_id=vs.id)

    #atexit.register(delete_vector_store)

    
    file_paths = ["data/raw/1. A glimpse of the future - Tier 2 Committee Visions for the future of the agency (2).pptx"]
    file_streams = [open(p, 'rb') for p in file_paths]
    
    # Upload and poll
    file_batch = buddy.client.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vs.id,
        files=file_streams
    )
    
    # Close file streams
    for stream in file_streams:
        stream.close()
    
    # Check the batch status
    print(f"Batch status: {file_batch.status}")
    print(f"File counts: {file_batch.file_counts}")
    
    # Check individual file statuses
    files_list = buddy.client.vector_stores.files.list(vector_store_id=vs.id)
    for file in files_list.data:
        print(f"File {file.id}: status={file.status}, last_error={file.last_error}")
    
    # Update assistant with file_search tool
    buddy.assistant = buddy.client.beta.assistants.update(
        assistant_id=buddy.assistant.id,
        tools=[{"type": "file_search"}],
        tool_resources={"file_search": {"vector_store_ids": [vs.id]}}
    )
    
    #m = buddy.send_fresh("Search the files I've uploaded. Then follow the instructions. Include updates from all slides. Multiple distinct update points should all be included. Proceed with the task!")
    m = buddy.send_fresh("Proceed with the task!")
    print(m)

# Final output as JSON
# refresh context window
# the entire slide + GSBPM content as system prompt, then loop through each sub process / phase
# 02 - implicated work description 