### Required packages

 - Make
 - jq
 - Bash
 - sed
 - Python 
 - Powershell
 - Microsoft Office (ideally)
 - Pandoc

#### Required Python packages
 - dotenv
 - openai
 - numpy
 - pandas
 - [if local] transformers
 - [if local] sentence-transformers


### Required AI
 - Coding-capable LLM (for generating code to standardize schema, "072_.../merge_schema.py"

 - Embedding model (such as)
    - Access through Azure API ("embedding.env")
        - Cohere Embed 4.0
            - API KEY
            - Endpoint

    - Locally on The Zone, such as
        - Qwen3 embedding 4B or 0.6B.
            - Need weights from HuggingFace
            - Install transformers and/or "sentence-transformers" python packages.

