"""
===============================================================================
File: assistant.py

Purpose:
    Provides a lightweight Azure OpenAI integration layer for future skills
    forecasting and workforce analysis workflows.

    This module encapsulates Azure OpenAI client creation, model interaction,
    retry handling, and resilient message submission using the Azure
    Responses API. It serves as the primary interface between the forecasting
    pipeline and GPT-based analytical models.

Classes:
    Assistant
        Manages communication with an Azure OpenAI deployment by submitting
        prompts, applying system-level instructions, and returning generated
        responses.

Functions:
    create_client(dotenv_path="./model.env")
        Loads Azure OpenAI configuration from environment variables and
        initializes an authenticated AzureOpenAI client instance.

    persistent_send(send_func, prompt, max_retries=5)
        Executes a message submission function with bounded retry logic to
        improve resilience against transient service, network, or API errors.

Author:
    Souroosh Memarian (Statistics Canada)

Created:
    2026-07-21

Last Modified:
    2026-07-28

Version:
    2.0.0

Dependencies:
    - os
    - time
    - dotenv
    - openai.AzureOpenAI
    - openai.RateLimitError

Environment Variables:
    AZURE_OPENAI_ENDPOINT
        Azure OpenAI service endpoint URL.

    AZURE_OPENAI_API_KEY
        Azure OpenAI service authentication key.

    AZURE_OPENAI_DEPLOYMENT
        Azure OpenAI deployment name used for inference requests.

Notes:
    - Uses the Azure OpenAI Responses API.
    - Designed for stateless analytical workloads where each business
      process update is evaluated independently.
    - System instructions are supplied during Assistant initialization and
      included in every model invocation.
    - Supports Azure-hosted GPT deployments including GPT-5 series models.
    - Optimized for long-running workforce planning, modernization, digital
      transformation, automation, and future-skills forecasting workflows.
    - Avoids Assistant/Thread/Run orchestration in favor of a simplified
      request-response architecture.

Error Handling:
    - Retries Azure rate-limit events using exponential backoff.
    - Retries transient execution failures through bounded retry logic.
    - Raises RuntimeError when maximum retry limits are exceeded.
    - Surfaces unrecoverable errors to the calling application for proper
      debugging and monitoring.

Workflow:
    1. Load Azure OpenAI credentials and deployment configuration.
    2. Create an authenticated AzureOpenAI client.
    3. Initialize an Assistant with forecasting instructions.
    4. Submit user prompts through the Azure Responses API.
    5. Receive and return generated model output.
    6. Retry transient failures when appropriate.
    7. Propagate unrecoverable failures to the calling workflow.

===============================================================================
"""

import os
import time

from dotenv import load_dotenv
from openai import (
    APIConnectionError,
    APITimeoutError,
    AzureOpenAI,
    InternalServerError,
    RateLimitError,
)


def create_client(
    dotenv_path="./model.env"
):

    load_dotenv(dotenv_path)

    client = AzureOpenAI(
        azure_endpoint=os.getenv(
            "AZURE_OPENAI_ENDPOINT"
        ),
        api_key=os.getenv(
            "AZURE_OPENAI_API_KEY"
        ),
        api_version="2025-03-01-preview"
    )

    return client


class Assistant:

    def __init__(
        self,
        system_prompt,
        dotenv_path="./model.env"
    ):

        self.system_prompt = (
            system_prompt
        )

        self.client = (
            create_client(
                dotenv_path
            )
        )

        self.model = os.getenv(
            "AZURE_OPENAI_DEPLOYMENT"
        )

    def send_message(
        self,
        user_prompt,
        max_retries=5
    ):

        print("Submitting request")

        attempt = 0

        while attempt < max_retries:

            try:

                response = (
                    self.client.responses.create(
                        model=self.model,

                        instructions=
                        self.system_prompt,

                        input=user_prompt
                    )
                )

                print("Response received")

                return (
                    response.output_text
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
    prompt,
    max_retries=5
):

    for attempt in range(max_retries):

        try:

            return send_func(prompt)

        except (
            RateLimitError,
            APIConnectionError,
            APITimeoutError,
            InternalServerError
              ) as e:

            print(
                f"Attempt {attempt + 1}/{max_retries} failed:"
            )

            print(e)

            time.sleep(5)

    raise RuntimeError(
        "Maximum retries exceeded."
    )
