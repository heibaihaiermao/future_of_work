"""
Last modified by: Sophie
Modify date: 2026-07-20
"""

from assistant import Assistant, persistent_send
from json import loads, dumps, dump as jdump
from operator import itemgetter
from tqdm import tqdm
from time import sleep
from os.path import exists, basename
import itertools as itt


# diable Azure warnings about assistants deprication
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="AzureOpenAI.beta.assistants")
warnings.filterwarnings("ignore", category=UserWarning, module="AzureOpenAI.beta.threads")


# Define system prompt

# 1. join GSBPM update, and implication > wd_update_inputs
# 2. send wd_update_inputs, requesting key-activities that are affected, updated and skills.
#     -  Looping over wd_update_input element : a GSBPM update with justification for implication to
#        work-description.
#     -  Structured work-description is included in prompt.

def read(path):
    with open(path, 'r', encoding='utf-8') as fil:
        return fil.read()

input_data_path = "data/wd_update_input"
pjoin = lambda f: "/".join((input_data_path, f))

background = read("prompts/prompt_01_-_background_prompt.txt")

gsbpm_intro = read("prompts/prompt_02_-_GSBPM_context_intro.txt")
gsbpm = read(pjoin("2025-09-23_-_updated_GSBPM_descriptions.json"))

wd_implications_intro = read("prompts/prompt_03_-_work-description_context_intro.txt")
wd_implicated_updates = loads(read(pjoin("implicated_GSBPM_updates_per_work-description_-_all.json")))

work_descriptions = loads(read(pjoin("work_descriptions.json")))

task = read("prompts/prompt_04_-_task_and_schema.txt")


def find_work_description(work_descriptions, classification, title):
    job_family = get_job_family(work_descriptions,
                                classification)

    work_description = select_job_from_family(job_family,
                                              title)
    return work_description


def get_job_family(work_descriptions, classification):

    wds = filter(lambda x: x['Classification'].lower() == classification,
                 work_descriptions)

    # Select the positions from it.
    wds = map(itemgetter("Positions"), wds)

    return next(wds)


def select_job_from_family(wds, title):
    work_description = filter(
            lambda x: x['Position Title'].__eq__(title),
            wds)
    work_description = list(work_description)
    assert len(work_description) == 1

    work_description = work_description[0]
    return work_description



def forecast_competency_gaps(implication):
    title = implication['title']
    classification = implication['classification']

    # Get corresponding work-description.
    work_description = find_work_description(work_descriptions,
                                            classification,
                                            title)
   
    # Prepare system prompt.
    system_prompt = f'''{background}
    
## Context
### GSBPM
{gsbpm_intro}
```[JSON]
{gsbpm}
```

### Targeted Work-description
{wd_implications_intro}
```[JSON]
{dumps(work_description)}
```

{task}

RESPOND IN VALID JSON ONLY.
'''


    # Init agent.
    buddy = Assistant(system_prompt=system_prompt)
    send = buddy.send_message
    
    
    #init = send("Before proceeding with the task, validate if my instructions are clear, and if all of the required information has been provided. If necessary, ask clarifying follow-up questions or request additional information.")
    
    init = send("Prepare for the task. First updated element is forecoming.")
    
    messages = []
    for update_element in tqdm(implication['implicated phases and sub-processes']):
        prompt = dumps(update_element)
        response = persistent_send(send, prompt)
        messages.append(response)

    return messages


def preprocess_message(message):
    message = message.strip("`")

    if message[:4].lower() == 'json':
        message = message[4:]

    return message


def _test_preprocess_message():
    assert preprocess_message('```json\n{"a": "1"}```') == {"a": "1"}



def postprocess_message(message):
    if type(message) is list:
        if len(message) == 1:
            message = message[0]
    return message

def _test_postprocess_message():
    assert postprocess_message([{"a": "1"}]) == {"a": "1"}



def process_message(message):
    message = preprocess_message(message)
    message = loads(message)
    message = postprocess_message(message)
    return message


ojoin = "data/updated_wd_with_skills/".__add__ 
def make_path(title):
    proposed_updates_path = "".join((title.replace(" ","_"),
                                     "_-_proposed_updates.json"))

    proposed_updates_path = proposed_updates_path.replace("/", "_-_")
    proposed_updates_path = proposed_updates_path.replace("\\", "_-_")

    proposed_updates_path = ojoin(proposed_updates_path)
    return proposed_updates_path
 
if __name__ == "__main__":
    #from sys import argv

    #ind = int(argv[1])
    #implication = wd_implicated_updates[ind]

    for implication in wd_implicated_updates:
        title = implication['title'] 
        proposed_updates_path = make_path(title)

        file_already_exists = exists(proposed_updates_path)
        if file_already_exists:
            print(f"exists: {basename(proposed_updates_path)}")

            # Skip line
            continue
        


        raw_messages = forecast_competency_gaps(implication)

        # Post processes messages.
        messages = map(process_message, raw_messages)
        messages = itt.chain(messages)
        try:
            messages = list(messages)

        except:
            from pickle import dump
            with open("debug.pkl", 'wb') as fil:
                dump(raw_messages, fil)
        
        title = implication['title'] 
        proposed_updates_path = make_path(title)

        with open(proposed_updates_path, 'w') as fil:
            jdump(messages, fil, indent=4)
        
    
    
    
    #    for implication in wd_implicated_updates:
    #        forecast_competency_gaps(implication)
