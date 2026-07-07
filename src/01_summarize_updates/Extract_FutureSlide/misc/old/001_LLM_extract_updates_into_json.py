from openai import AzureOpenAI
from dotenv import load_dotenv
from os import getenv, listdir
from glob import glob

def load_markdown_file(path):
    with open(path, 'r', encoding="utf-8") as fil:
        markdown_content = fil.read()
    return markdown_content

def load_prompt(path):
    with open(path, 'r', encoding="utf-8") as fil:
        prompt_preamble = fil.read()
    return prompt_preamble


#system_prompt = {"role": "system",
#                 "content": '''
#The task is to extract text from a markdown document, quoting verbatim
#from the content, and organizing the extracts into JSON format.'''
from hashlib import md5
def make_file_id(file_stream):
    content = file_stream.read()
    content_hash = md5(content).hexdigest()
    file_id = "assistant_"+content_hash
    return file_id


if __name__ == "__main__":
    #prompt_path = "gsbpm_extract_prompt.txt"
    #markdown_path  = "data/output/GSBPM_v5_2.md"
    #prompt_preamble = load_prompt(prompt_path)
    #markdown_content = load_markdown_file(markdown_path)

    #prompt_content = "\n".join((prompt_preamble,
    #                            "```{Markdown}",
    #                            markdown_content,
    #                            "```"))
    #user_prompt = {"role": "user",
    #               "content": prompt_content}

    load_dotenv("../py.env")
    endpoint = getenv("AZURE_OPENAI_ENDPOINT")
    subscription_key = iter([getenv("AZURE_OPENAI_API_KEY")])

    deployment = "gpt-4.1-standard"
    # api_version = "2024-12-01-preview"
    api_version = "2025-01-01-preview"

    raw_data_paths = listdir("data/raw")
    file_paths = map(glob, raw_data_paths)
    1/0
    file_streams = [open(p, 'rb') for p in file_paths]
    file_ids = list(map(make_file_id, file_streams))

    client = AzureOpenAI(api_version=api_version,
                     azure_endpoint=endpoint,
                     api_key=next(subscription_key))
    if True:
    #with AzureOpenAI(api_version=api_version,
    #                 azure_endpoint=endpoint,
    #                 api_key=next(subscription_key)) as client:

        vs = client.vector_stores.list().data[0]
        file_batch = client.vector_stores.file_batches.upload_and_poll(
                                vector_store_id = vs.id,
                                file_ids = file_ids,
                                files = file_streams)

        1/0
        response = client.chat.completions.create(
                        messages = [user_prompt],
                        max_completion_tokens=13107,
                        #temperature=1.0,
                        #top_p=1.0,
                        #frequency_penalty=0.0,
                        #presence_penalty=0.0,
                        model=deployment)


    # Save full response
    from pickle import dump
    output_path = "/".join(("data",
                            "output",
                        markdown_path.split("/")[-1].split(".")[0]+".pkl"))
    with open(output_path, 'wb') as fil:
        dump(response, fil)

    # Save response content in JSON
    import json
    response_content = response.choices[0].message.content
    response_content = response_content.lstrip("`json\n").rstrip("`\n")
    response_content = json.loads(response_content)

    #from json import dump as jdump, 
    json_path = markdown_path.rstrip(".md")+".json"
    with open(json_path, 'w') as fil:
        json.dump(response_content,
                  fil,
                  indent=4)




    print(response.choices[0].message.content)
