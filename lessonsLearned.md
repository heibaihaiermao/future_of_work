
## Conversion of content.

- When converting through Foxit PDF (no longer available)

                PDF -> DOCX -> Markdown

  is cleaner than

                PDF -> HTML -> Markdown

## Vector store

The vector store in Azure Foundry gives agentic ability to an assistant to search through chunks extracted from documents in the vector store. The major issues with this are:

  - Only a subset of chunks will be included, regardless of how many documents are in the vector-store.
  - The process of chunking is undocumented, unverifiable, and uncontrollable.
  - As a user, one has no control of when, and to what degree comparisons are done.

A more reliable method of comparison is to use an embedding model, then script the comparison of documents / chunks, and prompt. Then identified content can be returned into context for LLM inference
