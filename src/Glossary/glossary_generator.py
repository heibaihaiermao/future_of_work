import json

from openai import AzureOpenAI

from config import SYSTEM_PROMPT


class GlossaryGenerator:

    def __init__(
        self,
        endpoint,
        api_key,
        api_version,
        deployment_name,
    ):

        self.client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version,
        )

        self.deployment_name = deployment_name

    def generate_entry(self, record):

        user_prompt = f"""
Skill Gap:
{record["development area"]}

Description:
{record["description"]}

Change To Work:
{record["change to work"]}

Justification:
{record["justification"]}
"""

        response = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )

        content = response.choices[0].message.content

        return json.loads(content)