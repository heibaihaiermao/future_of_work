"""
===============================================================================
File: assistant.py

Purpose:
    Provides Azure OpenAI integration and reliable communication utilities
    for interacting with Large Language Models (LLMs) used in future skills
    forecasting and workforce analysis.

Classes:
    Assistant
        Wraps Azure OpenAI Assistant functionality, manages conversation
        threads, submits prompts, and retrieves model responses.

Functions:
    setup_azure(system_prompt, dotenv_path="../py.env")
        Initializes Azure OpenAI resources, authenticates using environment
        variables, and creates a configured assistant instance.

    persistent_send(send_func, prompt)
        Provides continuous retry logic for message submission and response
        retrieval in the event of transient failures.

Author:
    Souroosh Memarian (Statistics Canada)

Created:
    2026-07-21

Last Modified:
    2026-07-21

Version:
    1.0.0

Dependencies:
    - os
    - time
    - dotenv
    - openai.AzureOpenAI
    - openai.RateLimitError

Environment Variables:
    AZURE_OPENAI_ENDPOINT
        Azure OpenAI service endpoint.

    AZURE_OPENAI_API_KEY
        Azure OpenAI service API key.

Notes:
    - Uses Azure OpenAI Assistants for conversational analysis.
    - Assistant instructions are supplied through a system prompt during
      initialization.
    - Creates and maintains a dedicated conversation thread for each
      Assistant instance.
    - Implements exponential backoff when Azure rate limits are encountered.
    - Implements persistent retry logic for resilience against temporary
      API, network, or service interruptions.
    - Designed for long-running workforce analysis and skills forecasting
      workflows where reliability is critical.

Error Handling:
    - Retries RateLimitError exceptions using exponential backoff.
    - Automatically polls run status until completion.
    - Raises RuntimeError when the maximum number of retries is exceeded.
    - persistent_send() continuously retries failed requests until a
      response is successfully obtained.

Workflow:
    1. Load Azure OpenAI credentials from environment variables.
    2. Create an Azure OpenAI client.
    3. Create an Assistant configured with forecasting instructions.
    4. Create a conversation thread.
    5. Submit user prompts.
    6. Monitor execution status.
    7. Retrieve the generated response.
    8. Retry automatically when transient failures occur.

===============================================================================
"""

import os
import time

from dotenv import load_dotenv

from openai import (
    AzureOpenAI,
    RateLimitError
)


def setup_azure(
    system_prompt,
    dotenv_path="../py.env"
):

    load_dotenv(dotenv_path)

    client = AzureOpenAI(
        azure_endpoint=os.getenv(
            "AZURE_OPENAI_ENDPOINT"
        ),
        api_key=os.getenv(
            "AZURE_OPENAI_API_KEY"
        ),
        api_version="2025-01-01-preview"
    )

    assistant = client.beta.assistants.create(
        model="gpt-4.1",
        instructions=system_prompt,
        temperature=0.2,
        top_p=1,
        tools=[],
        name="Future Skills Forecasting Assistant"
    )

    return client, assistant


class Assistant:

    def __init__(
        self,
        system_prompt,
        dotenv_path="../py.env"
    ):

        self.client, self.assistant = (
            setup_azure(
                system_prompt,
                dotenv_path
            )
        )

        self.thread = (
            self.client
            .beta
            .threads
            .create()
        )

    def send_message(
        self,
        user_prompt,
        max_retries=5
    ):

        attempt = 0

        while attempt < max_retries:

            try:

                self.client.beta.threads.messages.create(
                    thread_id=self.thread.id,
                    role="user",
                    content=user_prompt
                )

                run = (
                    self.client.beta.threads.runs.create(
                        thread_id=self.thread.id,
                        assistant_id=self.assistant.id
                    )
                )

                while run.status in (
                    "queued",
                    "in_progress",
                    "cancelling"
                ):

                    time.sleep(1)

                    run = (
                        self.client.beta.threads.runs.retrieve(
                            thread_id=self.thread.id,
                            run_id=run.id
                        )
                    )

                if run.status == "completed":

                    messages = (
                        self.client
                        .beta
                        .threads
                        .messages
                        .list(
                            thread_id=self.thread.id
                        )
                    )

                    return (
                        messages
                        .data[0]
                        .content[0]
                        .text.value
                    )

            except RateLimitError:

                wait_time = (
                    2 ** attempt
                )

                time.sleep(wait_time)

            attempt += 1

        raise RuntimeError(
            "Assistant retries exceeded."
        )


def persistent_send(
    send_func,
    prompt
):

    while True:

        try:
            return send_func(prompt)

        except Exception as e:

            print(e)

            time.sleep(5)