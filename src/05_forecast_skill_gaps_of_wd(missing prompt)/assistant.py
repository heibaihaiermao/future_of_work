import os
import json
import requests
import time
from openai import AzureOpenAI, RateLimitError
from dotenv import load_dotenv

from datetime import date, datetime
today = date.today().isoformat()

from time import sleep


from datetime import datetime, timedelta
from time import sleep
from collections import deque


# diable Azure warnings about assistants deprication
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="AzureOpenAI.beta.assistants")
warnings.filterwarnings("ignore", category=UserWarning, module="AzureOpenAI.beta.threads")




def setup_azure(system_prompt, dotenv_path="../py.env"):
    load_dotenv(dotenv_path)
    # Setup assistant.
    client = AzureOpenAI(
      azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
      api_key= os.getenv("AZURE_OPENAI_API_KEY"),
      api_version="2024-05-01-preview")
    
    assistant = client.beta.assistants.create(
      model="gpt-4.1-standard", # replace with model deployment name.
      instructions=system_prompt,
      tools=[{"type":"file_search"}],
      temperature=0.2,
      top_p=1,
      name=f"PyAssistant - {today}")
    return client, assistant


class Assistant():
    def __init__(self, system_prompt, dotenv_path="../py.env"):
        self.message_history = [{"system": system_prompt}]
        self.response_history = []
        self.system_prompt = system_prompt
        self.client, self.assistant = setup_azure(system_prompt, dotenv_path)

        # Create a thread
        self.thread = self.client.beta.threads.create()

        self.errors = []


    def delete(self):
        self.client.beta.threads.delete(self.thread.id)
        self.client.beta.assistants.delete(self.assistant.id)

    def send_fresh(self, user_prompt):
        '''send message on fresh thread.'''
        self.client.beta.threads.delete(self.thread.id)
        self.thread = self.client.beta.threads.create()
        return self.send_message(user_prompt)


        
    ## Add a user question to the thread
    def send_message(self, user_prompt):
        # Add user message to the thread
        self.message_history.append({"user": user_prompt})
        try:
            message = self.client.beta.threads.messages.create(thread_id=self.thread.id,
                                                               role="user",
                                                               content=user_prompt)
        except RateLimitError as e:
            self.err_response = e.response
            raise IOError



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
          self.response_history.append(run)
          return message_text

        elif run.status == 'requires_action':
          # the assistant requires calling some functions
          # and submit the tool outputs back to the run
          self.response_history.append(run)
          raise IOError
        
        else:
          #time.sleep(1)
          #message_text = self.send_message(user_prompt)
          print(run.status)
          self.errors.append(run)

          self.err_run = run
          self.wait_after_error()
          message_text = self.send_message(user_prompt)
          return message_text

    def wait_after_error(self):
        error_message = str(self.err_run.last_error)
        time_req = error_message.split("Please retry after ")[-1].split()[0]
        time_req = int(time_req)
        print(f"sleeping: {time_req:.1f}")
        sleep(time_req)


    def persistent_send(self, prompt):
        n_messages = 1
        response = self.send_message(prompt)
    
        while response is None:
            print(n_messages)
            time.sleep(n_messages)
            response = self.send_message(prompt)
            n_messages += 1
    
        return response

    def count_tokens(self, prompt):
        try:
            tokenized = self.encode(prompt)

        except AttributeError:
            from tiktoken import encoding_for_model
            encoder = encoding_for_model("gpt-4.1")
            self.encode = encoder.encode

            tokenized = self.encode(prompt)

        return len(tokenized)

    def cautious_send(self, prompt, send_func):
        n_cost = self.count_tokens(prompt)

        estimated_response_tokens = n_cost * 2
        estimated_total_cost = n_cost + estimated_response_tokens
        
        # Initialize tracking variables on first call
        if not hasattr(self, 'token_history'):
            self.token_history = deque()  # Store (timestamp, token_count) tuples
            self.rate_limit = 80000  # tokens per minute
            self.window_size = 60  # seconds
            # Add system prompt tokens
            self.system_tokens = self.count_tokens(self.system_prompt)
            self.token_history.append((datetime.now(), self.system_tokens))
        
        current_time = datetime.now()
        
        # Remove tokens outside the sliding window
        cutoff_time = current_time - timedelta(seconds=self.window_size)
        while self.token_history and self.token_history[0][0] < cutoff_time:
            self.token_history.popleft()
        
        # Calculate tokens used in current window
        tokens_in_window = sum(count for _, count in self.token_history)
        tokens_in_window += self.system_tokens
        
        # Wait if adding this request would exceed the limit
        while tokens_in_window + n_cost > self.rate_limit:
            # Calculate how long to wait
            if self.token_history:
                oldest_timestamp = self.token_history[0][0]
                wait_time = (oldest_timestamp - cutoff_time).total_seconds() + 1
            else:
                wait_time = 1
            
            print(f"Rate limit approaching: {tokens_in_window + n_cost}/{self.rate_limit} tokens")
            print(f"Waiting {wait_time:.1f} seconds...")
            sleep(wait_time)
            
            # Recalculate after waiting
            current_time = datetime.now()
            cutoff_time = current_time - timedelta(seconds=self.window_size)
            while self.token_history and self.token_history[0][0] < cutoff_time:
                self.token_history.popleft()
            tokens_in_window = sum(count for _, count in self.token_history)
        
        # Record this request
        self.token_history.append((current_time, n_cost))
        
        # Send the request
        m = send_func(prompt)
        
        # If the response also has tokens, record them
        if hasattr(m, 'usage') and hasattr(m.usage, 'completion_tokens'):
            response_tokens = m.usage.completion_tokens
        elif hasattr(m, 'usage') and hasattr(m.usage, 'output_tokens'):
            response_tokens = m.usage.output_tokens
        else:
            response_tokens = estimated_response_tokens
        self.token_history.append((datetime.now(), response_tokens))

        total_tokens = n_cost + response_tokens
        print(f"Request: {n_cost} tokens, Response: {response_tokens} tokens, Total: {total_tokens} tokens")
        
        return m





#    def cautious_send(self, prompt, send_func):
#        n_cost = self.count_tokens(prompt)
#
#        try:
#            self.tot_tok += n_cost
#
#        except AttributeError:
#            self.tot_tok = n_cost + self.count_tokens(self.system_prompt)
#            self.beginning = datetime.today()
#            self.time_of_last_message = datetime.today()
#            self.rate_limit = 37000#150000
#
#        self.tot_mins = (datetime.today() - self.beginning).total_seconds() / 60
#        self.tok_rate = self.tot_tok / self.tot_mins if self.tot_mins > 1 else self.tot_tok
#
#        while self.tok_rate > self.rate_limit:
#            required_time = (self.tot_tok/self.rate_limit - self.tot_mins) * 60
#            print(self.tot_tok, self.tot_mins, self.tok_rate, required_time)
#            sleep(required_time)
#
#            # update rate
#            self.tot_mins = (datetime.today() - self.beginning).total_seconds() / 60
#            self.tok_rate = self.tot_tok / self.tot_mins if self.tot_mins > 1 else self.tot_tok
#
#        m = send_func(prompt)
#        return m














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
    pass
    #client, assistant = setup_azure(system_prompt)
    #buddy = Assistant(system_prompt="tell me joke, I'll tell you what kind")
    #send = buddy.send_message

