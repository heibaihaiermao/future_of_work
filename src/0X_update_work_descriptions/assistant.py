import os
import json
import requests
import time
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv("../py.env")

# diable Azure warnings about assistants deprication
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="AzureOpenAI.beta.assistants")
warnings.filterwarnings("ignore", category=UserWarning, module="AzureOpenAI.beta.threads")




def setup_azure(system_prompt):
    # Setup assistant.
    client = AzureOpenAI(
      azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
      api_key= os.getenv("AZURE_OPENAI_API_KEY"),
      api_version="2024-05-01-preview")
    
    assistant = client.beta.assistants.create(
      model="gpt-4.1-standard", # replace with model deployment name.
      instructions=system_prompt,
      tools=[{"type":"file_search"}],
      #tool_resources={"file_search":{"vector_store_ids":["vs_uYZmeovSd2CrCoEzgEw4MA4h"]}},
      temperature=1,
      top_p=1
    )
    return client, assistant


class Assistant():
#    def __init__(self, client, assistant):
#        self.client = client
#        self.assistant = assistant
    def __init__(self, system_prompt):
        self.message_history = [{"system": system_prompt}]
        self.client, self.assistant = setup_azure(system_prompt)

        # Create a thread
        self.thread = self.client.beta.threads.create()

        self.errors = []

    def send_fresh(self, user_prompt):
        self.client.beta.threads.delete(self.thread.id)
        self.thread = self.client.beta.threads.create()
        return self.send_message(user_prompt)


        
    ## Add a user question to the thread
    def send_message(self, user_prompt):
        # Add user message to the thread
        self.message_history.append({"user": user_prompt})
        message = self.client.beta.threads.messages.create(thread_id=self.thread.id,
                                                           role="user",
                                                           content=user_prompt)
        # Run the thread
        run = self.client.beta.threads.runs.create(thread_id=self.thread.id,
                                                   assistant_id=self.assistant.id)

        # Looping until the run completes or fails
        while run.status in ['queued', 'in_progress', 'cancelling']:
          time.sleep(1)
          run = self.client.beta.threads.runs.retrieve(
            thread_id=self.thread.id,
            run_id=run.id
          )
        
        if run.status == 'completed':
          messages = self.client.beta.threads.messages.list(
            thread_id=self.thread.id
          )

          message_text = messages.data[0].content[0].text.value

          #if message_text is None:
          #    print("recurse")
          #    message_text = self.send_message(user_prompt)

          self.message_history.append({"ai": message_text})
          return message_text

        elif run.status == 'requires_action':
          # the assistant requires calling some functions
          # and submit the tool outputs back to the run
          pass
        
        else:
          #time.sleep(1)
          #message_text = self.send_message(user_prompt)
          print(run.status)
          self.errors.append(run)
          raise IOError
        #return message_text

    def persistent_send(self, prompt):
        n_messages = 1
        response = self.send_message(prompt)
    
        while response is None:
            print(n_messages)
            time.sleep(n_messages)
            response = self.send_message(prompt)
            n_messages += 1
    
        return response





def persistent_send(send, prompt):
    n_messages = 1
    response = send(prompt)

    while response is None:
        print(n_messages)
        time.sleep(n_messages)
        response = send(prompt)
        n_messages += 1

    return response

if __name__ == "__main__":
    #client, assistant = setup_azure(system_prompt)
    buddy = Assistant(system_prompt="tell me joke, I'll tell you what kind")
    send = buddy.send_message

