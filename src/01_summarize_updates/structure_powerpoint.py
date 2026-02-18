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



if __name__ == "__main__":

    load_dotenv("../py.env")
    prompt_path = "prompts/01_extract_updates.txt"
    gsbpm_json_path = "data/input/GSBPM_v5_2.json"
    
    system_prompt = {"role": "system",
                     "content": "My method of converting Powerpoint slides to markdown is pretty flawed. I've uploaded the original powerpoint presentation, and it can also be found in the vector store. Search through it and then help me produce a better conversion. Later in the prompt I'll also include the Pandoc-produced markdown text. I think an effective way to represent the powerpoint presentation is in JSON format, where 'slide-objects' will comprise a list."}

    prompt_content = load_prompt("data/raw/1. A glimpse of the future - Tier 2 Committee Visions for the future of the agency (2) - Copy.txt")
    user_prompt = {"role": "user",
                   "content": "Here is the markdown content \n```markdown\n" + prompt_content + "\n```"}
    
    buddy = Assistant(json.dumps([system_prompt,
                                  user_prompt]))
    atexit.register(buddy.delete)
    
    vs = buddy.client.vector_stores.create()
    def delete_vector_store(buddy):
        buddy.client.vector_stores.delete(vector_store_id=vs.id)
    atexit.register(delete_vector_store)
    
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




#    load_dotenv("../py.env")
#
#    system_prompt = {"role": "system",
#                     "content": "search the vector store. If there is no vector store then state so."}
#
#    user_prompt = {"role": "user",
#                   "content": ""}
#
#    buddy = Assistant(json.dumps([system_prompt,
#                                  user_prompt]))
#    atexit.register(buddy.delete)
#
#    vs = buddy.client.vector_stores.create()
#    def delete_vector_store():
#        buddy.client.vector_stores.delete(vs.id)
#    atexit.register(delete_vector_store)
#
#    file_paths = ["data/raw/briefing.txt"]
#
#    file_streams = [open(p, 'rb') for p in file_paths]
#
#
#        # NEED TO MAKE FILE-LOOKUP TO AVOID REUPLOADING FILES.
#    file_batch = buddy.client.vector_stores.file_batches.upload_and_poll(vector_store_id = vs.id,
#                                                                         files = file_streams)
#    
#
#    buddy.assistant = buddy.client.beta.assistants.update(assistant_id=buddy.assistant.id,
#                                              tools=[{"type": "file_search"}],
#                                              tool_resources={"file_search":{"vector_store_ids":[vs.id]}})
#
#    m = buddy.send_message("Search the vector store. Tell me about you find.")

    #m == 'There is no vector store present. I can only search the files you have uploaded using keyword-based search. If you have specific questions or topics you want to know about from your files, please let me know!'
#
#    endpoint = getenv("AZURE_OPENAI_ENDPOINT")
#    subscription_key = iter([getenv("AZURE_OPENAI_API_KEY")])
#    endpoint = "https://futureofwork-aifoundry-resource.cognitiveservices.azure.com/"
#    #deployment = "gpt-4.1-standard"
#    #deployment = "gpt-5-mini"
#    #api_version = "2024-12-01-preview"
#    deployment = "o3-mini"
#    api_version = "2024-12-01-preview"
#
#    client = AzureOpenAI(api_version=api_version,
#                         azure_endpoint=endpoint,
#                         api_key=next(subscription_key))
#
#
#    atexit.register(delete_vector_store)
#    

#
#
#    thread = client.beta.threads.create()
#    message = client.beta.threads.messages.create(
#                        thread_id=thread.id,
#                        role="user",
#                        content="Follow the instructions provided")
#
#        run = client.beta.threads.runs.create_and_poll(
#                        thread_id = thread.id,
#                        assistant_id = assistant.id)
#        response = client.beta.threads.messages.list(
#                        thread_id = thread.id,
#                        run_id = run.id)
#        1/0
#        #reponse = messages[0].content[0].text
#        response  = message[0].content[0].text
#
#
#
##        response = client.chat.completions.create(
##                        messages = [system_prompt, user_prompt],
##                        #max_completion_tokens=13107,
##                        #temperature=1.0,
##                        #top_p=1.0,
##                        #frequency_penalty=0.0,
##                        #presence_penalty=0.0,
##                        model=deployment,
##                        tools=[{"type": "file_search"}])
##                        #tool_resources={"file_search": {"vector_store_ids": [vs.id]}})
##
##
#    # Save full response
#    output_path = "data/output/deck_updates_response.pkl"
#    with open(output_path, 'wb') as fil:
#        pdump(message, fil)
#
#    # Save response content in JSON
#    #response_content = response.choices[0].message.content
#    response_content = response[0].content[0].text.value
#    response_content = response_content.lstrip("`json\n").rstrip("`\n")
#    response_content = json.loads(response_content)
#
#    #from json import dump as jdump, 
#    #json_path = markdown_path.rstrip(".md")+".json"
#    json_path = "data/output/deck_updates_o3.json"
#    with open(json_path, 'w') as fil:
#        json.dump(response_content,
#                  fil,
#                  indent=4)
#
#
#
#
#    print(response.choices[0].message.content)
