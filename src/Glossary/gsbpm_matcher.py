from sklearn.metrics.pairwise import cosine_similarity
from openai import AzureOpenAI
import numpy as np

from config import EMBEDDING_MODEL
from config import TOP_GSBPM_MATCHES


class GSBPMMatcher:

    def __init__(
        self,
        endpoint,
        api_key,
        api_version,
        embedding_model
    ):

        self.client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version
        )

        self.embedding_model = embedding_model

    def get_embedding(self, text):

        print("Endpoint:", self.client._azure_endpoint)
        print("Embedding deployment:", self.embedding_model)

        response = self.client.embeddings.create(
            model=self.embedding_model,
            input=text
        )

        return response.data[0].embedding

    def build_gsbpm_index(self, gsbpm_data):

        self.gsbpm_embeddings = []

        for item in gsbpm_data:

            text = self._build_gsbpm_text(item)

            embedding = self.get_embedding(text)

            self.gsbpm_embeddings.append(
                (item, embedding)
            )
    
    def _build_skill_gap_text(
        self,
        record
    ):

        return f"""
        {record.get("development area", "")}

        {record.get("description", "")}

        {record.get("change to work", "")}

        {record.get("justification", "")}
        """

    def _build_gsbpm_text(
        self,
        gsbpm_item
    ):

        return f"""
        {gsbpm_item.get("gsbpm_name", "")}

        {
            gsbpm_item.get(
                "change_summary",
                {}
            ).get(
                "description",
                ""
            )
        }

        {
            gsbpm_item.get(
                "future_expectation",
                {}
            ).get(
                "description",
                ""
            )
        }

        {
            gsbpm_item.get(
                "operational_implications",
                {}
            ).get(
                "description",
                ""
            )
        }
        """

    def find_matches(
        self,
        record,
    ):

        skill_text = self._build_skill_gap_text(
            record
        )

        skill_embedding = self.get_embedding(
            skill_text
        )

        scored_matches = []

        for item, gsbpm_embedding in self.gsbpm_embeddings:

            similarity = cosine_similarity(
                [skill_embedding],
                [gsbpm_embedding]
            )[0][0]

            scored_matches.append(
                (
                    similarity,
                    item
                )
            )

        scored_matches.sort(
            reverse=True,
            key=lambda x: x[0]
        )

        return [
            item
            for _, item
            in scored_matches[
                :TOP_GSBPM_MATCHES
            ]
        ]