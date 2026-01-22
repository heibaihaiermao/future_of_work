from itertools import islice, chain
class embedding_model():
    def __init__(self, pyenv_path="../py.env"):
        from openai import OpenAI
        from dotenv import load_dotenv
        from os import getenv
        from functools import partial
        from operator import attrgetter
        from json import load as jload


        load_dotenv(pyenv_path)
        endpoint = "https://futureofwork-aifoundry-resource.services.ai.azure.com/openai/v1/"
        deployment_name = "embed-v-4-0"
        
        client = OpenAI(
            base_url = endpoint,
            api_key = getenv("AZURE_EMBEDDING_API_KEY"))
        
        #response = client.embeddings.create(
        #    input = iter(["How do I use Python in VS Code?",
        #                  "hello world"]),
        #    model = deployment_name
        #)
    
        self.embedding_call = partial(client.embeddings.create,
                                      model=deployment_name)

        self.get_embedding = attrgetter("embedding")

        #with open("embed_memory.json", 'r') as fil:
        #    self.memory = jload(fil)



    def embed(self, input_iterable, max_N=96):

        # IMPLEMENT CACHE FROM MEMORY HERE.

        iterable_batch = islice(input_iterable, max_N)
        response = self.embedding_call(input=iterable_batch)
        while len(response.data) > 0:
            yield from map(self.get_embedding, response.data)

            iterable_batch = islice(input_iterable, max_N)
            try:
                first_item = next(iterable_batch)

            except StopIteration:
                break

            iterable_batch = prepend(first_item, iterable_batch)
            response = self.embedding_call(input=iterable_batch)
        #yield from response.data
        #return response

        #print(response.data[0].embedding)

def prepend(xi, x_iter):
    yield from chain.from_iterable(([xi], x_iter))

if __name__ == "__main__":
    embedder = embedding_model()
    vecs = embedder.embed(["hello", "world"])

