# Embedded Mapping of Skill Gaps to Learning Resources

After skill gaps have been determined and selected, we require a high-throughput method for identifying learning resources that best target the
identified skill-gaps. In previous iterations of mapping in this project, LLMs have been prompted to compare items, justify reasoning and make determinations one which inputs "map" to which outputs. With a large number of skill-gaps identified and a large number of learning resources, individual comparisons become prohibitively slow. Therefore, we will use an "embedding model" as a pre-cursor for efficient numerical comparison. 


## Embedding models.

<ASK LLM>

## Workflow overview(note: implements identifying broad vs width)
1) (as best as possible) standardize format, structure, and character of skill-gaps
2) (as best as possible) standardize format, structure, content and character of skill-gaps, while providing sufficient context for recommendations.
3) Embedded Mapping
    3.1) Calculate embeddings for each skill-gap and learning-resource
    3.2) Calculate cosine similarity for each possible pairing of learning-resource to skill gap.
    3.3) (Optional...) filtering or post-processing cosine similarities
    3.5) Ranking of skill-gap + learning-resource pairs by cosine similarity (per skill-gap) and selecting top "N" results.


## Procedure.
In sequence, enter each sub-directory of "07_..." and execute "make" from command-line.

## Requirements

### Required data
 - Classification of learning-resources (from "generate-course-profiles")
 - Raw data for learning-resources (for looping-in learning-resource descriptions.)
 - Skill-gaps


### Required packages

 - Make
 - jq
 - bash
 - sed
 - Python 

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

