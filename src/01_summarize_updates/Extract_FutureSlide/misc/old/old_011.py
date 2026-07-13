'''
Inputs: Deck, structured GSPBM data
Output: update-indexed implicated (s)BSP w/ justifications JSON.

This script extracts proposed updates to the GSBPM from a
reference document, listing for each (s)BSP that are
affected by the update. (s)BSPs are identified either by
being explicitly stated, or deduced by the LLM. Each
implicated (s)BSP includes a justification for association
with the update.


 - (s)BSP: a phase or sub-phase from the GSBPM.
'''

#from sys import argv
#deck_path = argv[1]


from openai import AzureOpenAI
from dotenv import load_dotenv
from os import getenv, listdir
from glob import glob
from itertools import chain
from pickle import load as pload, dump as pdump
import json

system_prompt = {"role": "system",
                 "content": "Only respond with valid JSON. Do not include preamble or concluding paragraphs."}
#''
#The task is to extract text from a markdown document, quoting verbatim
#from the content, and organizing the extracts into JSON format.'''
from hashlib import md5


def load_markdown_file(path):
    with open(path, 'r', encoding="utf-8-sig") as fil:
        markdown_content = fil.read()
    return markdown_content

def load_prompt(path):
    with open(path, 'r', encoding="utf-8-sig") as fil:
        prompt_preamble = fil.read()
    return prompt_preamble



# NEED TO MAKE FILE-LOOKUP TO AVOID REUPLOADING FILES.
def make_file_id(file_stream):
    content = file_stream.read() 
    file_stream.seek(0)
    content_hash = md5(content).hexdigest()
    file_id = "assistant-"+content_hash
    return file_id





if __name__ == "__main__":
    prompt_path = "prompts/01_extract_updates.txt"
    gsbpm_json_path = "data/input/GSBPM_v5_2.json"

    prompt_preamble = load_prompt(prompt_path)
    gsbpm = load_prompt(gsbpm_json_path)

    prompt_content = "\n".join((prompt_preamble,
                                "```{JSON",
                                gsbpm,
                                "```"))
    #prompt_path = "gsbpm_extract_prompt.txt"
    #markdown_path  = "data/output/GSBPM_v5_2.md"
    #prompt_preamble = load_prompt(prompt_path)
    #markdown_content = load_markdown_file(markdown_path)

    #prompt_content = "\n".join((prompt_preamble,
    #                            "```{Markdown}",
    #                            markdown_content,
    #                            "```"))
    user_prompt = {"role": "user",
                   "content": prompt_content}

    load_dotenv(".env")
    endpoint = getenv("AZURE_OPENAI_ENDPOINT")
    #subscription_key = iter([getenv("AZURE_OPENAI_API_KEY")])
    
    api_key = getenv("AZURE_OPENAI_API_KEY")
    endpoint = getenv("AZURE_OPENAI_ENDPOINT")
    api_version = getenv("AZURE_OPENAI_API_VERSION")

    assert api_key, "API key NOT loaded"
    assert endpoint, "Endpoint NOT loaded"
    assert api_version, "API version NOT loaded"

    #endpoint = "https://evan-mfsqg9b6-eastus2.cognitiveservices.azure.com/"
<<<<<<< HEAD:src/01_summarize_updates/Extract_FutureSlide/misc/old/old_011.py
    #endpoint = "https://futureofwork-aifoundry-resource.cognitiveservices.azure.com/"
    #deployment = "gpt-4.1-standard"
    #deployment = "gpt-5-mini"
    #api_version = "2024-12-01-preview"
    deployment = "gpt-4.1"
    #api_version = "2024-12-01-preview"
=======
    endpoint = "https://futureofwork-aifoundry-resource.cognitiveservices.azure.com/"
    endpoint = getenv("AZURE_EXTRACT_ENDPOINT")
    #deployment = "gpt-4.1-standard"
    #deployment = "gpt-5-mini"
    #api_version = "2024-12-01-preview"
    deployment = "o3-mini"
    api_version = "2024-12-01-preview"
    api_version = "2025-01-01-preview"
>>>>>>> origin/main:src/01_summarize_updates/011_extract_updates.py

    raw_data_dir = "data/raw/"
    #raw_data_paths = map(raw_data_dir.__add__,
    #                     listdir(raw_data_dir))
    raw_data_paths = [raw_data_dir + x for x in ['1. A glimpse of the future - Tier 2 Committee Visions for the future of the agency (2) - Copy.pptx']]

    #file_paths = map(glob, raw_data_paths)
    file_paths = raw_data_paths
    file_paths = list(file_paths)
    file_streams = [open(p, 'rb') for p in file_paths]
    file_hashes = list(map(make_file_id, file_streams))

    #client = AzureOpenAI(api_version=api_version,
    #                 azure_endpoint=endpoint,
    #                 api_key=next(subscription_key))
    #if True:

    with AzureOpenAI(
        api_version=api_version,
        azure_endpoint=endpoint,
        api_key=api_key) as client:

        try:
            vs = client.vector_stores.list().data[0]
        except IndexError:
            vs = client.vector_stores.create()
        #file_batch = client.vector_stores.file_batches.create_and_poll(
        #file_batch = client.vector_stores.files.create_and_poll(
        #                        vector_store_id = vs.id,
        #                        file_id = file_ids[0])



        # NEED TO MAKE FILE-LOOKUP TO AVOID REUPLOADING FILES.
        file_batch = client.vector_stores.file_batches.upload_and_poll(
                                vector_store_id = vs.id,
        #                        file_ids = file_ids,
                                files = file_streams)

        assistant = client.beta.assistants.create(name="Update Extractor",
                                                  description="By following the instructions carefully, extract any and all updates from each and every slide.",
                                                  instructions=json.dumps([system_prompt,
                                                                user_prompt]),
                                                  model=deployment,
                                                  tools=[{"type": "file_search"}])

        assistant = client.beta.assistants.update(assistant_id=assistant.id,
                                                  tool_resources={"file_search":{"vector_store_ids":[vs.id]}})

        thread = client.beta.threads.create()
#         message = client.beta.threads.messages.create(
#                         thread_id=thread.id,
#                         role="user",
#                         content="Follow the instructions provided")

<<<<<<< HEAD:src/01_summarize_updates/Extract_FutureSlide/misc/old/old_011.py
#         run = client.beta.threads.runs.create_and_poll(
#                         thread_id = thread.id,
#                         assistant_id = assistant.id)
#         response = client.beta.threads.messages.list(
#                         thread_id = thread.id,
#                         run_id = run.id)
#         #1/0
#         #reponse = messages[0].content[0].text
        
#         messages = client.beta.threads.messages.list(
#             thread_id=thread.id,
#             run_id=run.id
#         )

#         response_text = messages.data[0].content[0].text.value
        
#         print("MODEL OUTPUT:")
#         print(response_text)
=======
        run = client.beta.threads.runs.create_and_poll(
                        thread_id = thread.id,
                        assistant_id = assistant.id)
        response = client.beta.threads.messages.list(
                        thread_id = thread.id,
                        run_id = run.id)
        # 1/0
        #TODO add code
        #reponse = messages[0].content[0].text
        response = response[0].content[0].text

#        response = client.chat.completions.create(
#                        messages = [system_prompt, user_prompt],
#                        #max_completion_tokens=13107,
#                        #temperature=1.0,
#                        #top_p=1.0,
#                        #frequency_penalty=0.0,
#                        #presence_penalty=0.0,
#                        model=deployment,
#                        tools=[{"type": "file_search"}])
#                        #tool_resources={"file_search": {"vector_store_ids": [vs.id]}})
#
#
    # Save full response
    output_path = "data/output/deck_updates_response.pkl"
    with open(output_path, 'wb') as fil:
        pdump(message, fil)

    # Save response content in JSON
    #response_content = response.choices[0].message.content
    response_content = response[0].content[0].text.value
    response_content = response_content.lstrip("`json\n").rstrip("`\n")
    response_content = json.loads(response_content)

    #from json import dump as jdump, 
    #json_path = markdown_path.rstrip(".md")+".json"
    json_path = "data/output/deck_updates_o3.json"
    with open(json_path, 'w') as fil:
        json.dump(response_content,
                  fil,
                  indent=4)
>>>>>>> origin/main:src/01_summarize_updates/011_extract_updates.py




# #        response = client.chat.completions.create(
# #                        messages = [system_prompt, user_prompt],
# #                        #max_completion_tokens=13107,
# #                        #temperature=1.0,
# #                        #top_p=1.0,
# #                        #frequency_penalty=0.0,
# #                        #presence_penalty=0.0,
# #                        model=deployment,
# #                        tools=[{"type": "file_search"}])
# #                        #tool_resources={"file_search": {"vector_store_ids": [vs.id]}})
# #
# #
#     # Save full response
#     output_path = "data/output/deck_updates_response.pkl"
#     with open(output_path, 'wb') as fil:
#         pdump(message, fil)

#     # Save response content in JSON
#     #response_content = response.choices[0].message.content
#     #response_content = response[0].content[0].text.value
#     #response_content = response_content.lstrip("`json\n").rstrip("`\n")
#     #response_content = json.loads(response_content)

#     #from json import dump as jdump, 
#     #json_path = markdown_path.rstrip(".md")+".json"
#     json_path = "data/output/deck_updates_o3.json"
#     with open(json_path, 'w') as fil:
#         json.dump(response_content,
#                   fil,
#                   indent=4)




    #     print(response.choices[0].message.content)
    thread = client.beta.threads.create()

    # ✅ Step 1: send instruction to assistant
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="Extract all update points from the uploaded PowerPoint. Do not ask questions. Return valid JSON only."
    )

    # ✅ Step 2: run assistant
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id
    )

    # ✅ Step 3: retrieve output
    messages = client.beta.threads.messages.list(
        thread_id=thread.id,
        run_id=run.id
    )

    response_text = messages.data[0].content[0].text.value

    print("MODEL OUTPUT:")
    print(response_text)

    # ✅ Step 4: save JSON
    try:
        parsed = json.loads(response_text)

        with open("data/output/deck_updates_o3.json", "w") as fil:
            json.dump(parsed, fil, indent=4)

        print("✅ JSON saved successfully")

    except Exception:
        print("❌ Output not valid JSON")
        print(response_text)