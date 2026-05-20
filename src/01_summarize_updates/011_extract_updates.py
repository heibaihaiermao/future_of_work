"""
Step 011: Extract Updates from PowerPoint

Pipeline:
1. Load prompt + GSBPM
2. Upload PPT to vector store
3. Run assistant with file_search
4. Extract updates
5. Save JSON output
"""

import json
from openai import AzureOpenAI
from dotenv import load_dotenv
from os import getenv
from hashlib import md5


# Helpers
def load_file(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return f.read()


def make_file_id(file_stream):
    content = file_stream.read()
    file_stream.seek(0)
    return "assistant-" + md5(content).hexdigest()



# Main
if __name__ == "__main__":

    # Load environment
    load_dotenv(".env")

    api_key = getenv("AZURE_OPENAI_API_KEY")
    endpoint = getenv("AZURE_OPENAI_ENDPOINT")
    api_version = getenv("AZURE_OPENAI_API_VERSION")

    assert api_key, "API key NOT loaded"
    assert endpoint, "Endpoint NOT loaded"
    assert api_version, "API version NOT loaded"

    deployment = "gpt-4.1"

    # Load inputs
    prompt_path = "prompts/01_extract_updates.txt"
    gsbpm_path = "data/input/GSBPM_v5_2.json"

    prompt_text = load_file(prompt_path)
    gsbpm_text = load_file(gsbpm_path)

    full_prompt = (
        "You are an expert analyst.\n"
        "Extract ALL update points from the PowerPoint.\n"
        "Treat each distinct point as an update.\n\n"
        "IMPORTANT:\n"
        "- Do NOT ask clarifying questions\n"
        "- Do NOT add explanations\n"
        "- Return ONLY valid JSON\n\n"
        "JSON schema:\n"
        "{\n"
        '  "updates": [\n'
        "    {\n"
        '      "id": <int>,\n'
        '      "description": <string>\n'
        "    }\n"
        "  ]\n"
        "}\n\n"
        "GSBPM Context:\n"
        "```json\n"
        + gsbpm_text +
        "\n```\n\n"
        "Instructions:\n"
        + prompt_text
    )



    # File Setup
    ppt_path = "data/raw/1. A glimpse of the future - Tier 2 Committee Visions for the future of the agency (2) - Copy.pptx"
    file_stream = open(ppt_path, "rb")

    # Azure Client
    with AzureOpenAI(
        api_version=api_version,
        azure_endpoint=endpoint,
        api_key=api_key
    ) as client:
        # Create vector store
        vs = client.vector_stores.create()

        client.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vs.id,
            files=[file_stream]
        )

        file_stream.close()

        # Create assistant
        assistant = client.beta.assistants.create(
            name="Update Extractor",
            instructions=full_prompt,
            model=deployment,
            tools=[{"type": "file_search"}],
        )

        assistant = client.beta.assistants.update(
            assistant_id=assistant.id,
            tool_resources={"file_search": {"vector_store_ids": [vs.id]}}
        )

        # Run pipeline
        thread = client.beta.threads.create()

        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content="Extract updates from the uploaded PowerPoint."
        )

        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant.id
        )

        messages = client.beta.threads.messages.list(
            thread_id=thread.id,
            run_id=run.id
        )

        response_text = messages.data[0].content[0].text.value

        print("\n===== MODEL OUTPUT =====")
        print(response_text)

        # Save output
        try:
            parsed = json.loads(response_text)

            with open("data/output/deck_updates.json", "w") as f:
                json.dump(parsed, f, indent=4)

            print(" JSON saved successfully")

        except Exception:
            print(" Output is not valid JSON — saving raw text")

            with open("data/output/deck_updates_raw.txt", "w") as f:
                f.write(response_text)