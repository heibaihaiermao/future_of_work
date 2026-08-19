import numpy as np
import pandas as pd
from itertools import starmap, chain

#from persistent_embedding_0731 import collect_embeddings

def cosine_similarity(column_matrix, row_matrix):
    column_norm = np.matrix(np.linalg.norm(column_matrix, axis=1))
    row_norm = np.matrix(np.linalg.norm(row_matrix, axis=1))

    cosine_similarity_matrix = (row_matrix * column_matrix.T) / (row_norm.T * column_norm)
    return cosine_similarity_matrix

def create_cosine_similarity_df(column_series, row_series):
    column_matrix = np.matrix(np.vstack(column_series))
    row_matrix = np.matrix(np.vstack(row_series))

    cosine_similarity_matrix = cosine_similarity(column_matrix, row_matrix)

    cosine_similarity_df = pd.DataFrame(cosine_similarity_matrix,
                                        columns=column_series.index,
                                        index=row_series.index)

    return cosine_similarity_df


def get_top_resources(name, series, N=10):
    return (name, series.sort_values(ascending=False)[:N].to_dict())

def get_recommendations(score_df):
    recommends_per_col = starmap(get_top_resources, score_df.items())
    return dict(recommends_per_col)


def find_most_recommended(recommends):
    resource_keys = (ki.keys() for ki in recommends.values())
    resource_keys = list(chain.from_iterable(resource_keys))

    resource_counts = [(resource_keys.count(ki), ki) for ki in set(resource_keys)]
    resource_counts.sort()
    return resource_counts

def order_recommends_by_self_similarity(resource_embeddings, recommends):
    recommendation_embeddings = resource_embeddings[recommends.keys()]
    embedded_recommendations_matrix = np.matrix(np.vstack(recommendation_embeddings))

    recommendations_similarity = cosine_similarity(embedded_recommendations_matrix,
                                                   embedded_recommendations_matrix)

    # DEV: Arguably the 1's along the diagonal should be removed..
    mean_similarities = np.mean(recommendations_similarity, axis=0)
    similarity_order = np.argsort(mean_similarities)[::-1]

    ordered_recommendations = recommendation_embeddings.iloc[similarity_order.flat]
    return ordered_recommendation






if __name__ == "__main__":
    from sys import argv
    import json
    import os

    #lr_dir = "data/0731_inputs/learning-resources"
    with open("data/0732_embeddings/learning-resources/csps_-_embedding_memory.json", 'r', encoding="utf-8") as fil:
        lre = json.load(fil)

    lr_metadata = pd.DataFrame.from_dict(
            {k:v["data"] for k,v in lre.items()},
            orient="index"
        )
    lrdf = pd.DataFrame.from_dict(lre).T["vec"].apply(np.array)

    gaps_path = argv[1]
    with open(gaps_path, 'r', encoding="utf-8") as fil:
        ge = json.load(fil)
    #ge = collect_embeddings(gaps_dir, key_attribute="development area")
    gdf = pd.DataFrame.from_dict(ge).T["vec"].apply(np.array)

    cdf = create_cosine_similarity_df(gdf, lrdf)


    standard_recommendations = get_recommendations(cdf)

    lr_normalized_recommendations = get_recommendations((cdf.T / cdf.mean(axis=1)).T)

    # Removed least-similar half in each column.
    gap_mean_similarity = cdf.mean(axis=0)
    upper_half = np.maximum(0, cdf - gap_mean_similarity)

    # Restore most-similar half to original value.
    upper_half = upper_half + np.sign(upper_half)*gap_mean_similarity

    # Normalize remaining items by average similarity to all gaps.
    upper_half_normalized = (upper_half.T / cdf.mean(axis=1)).T

    # Get recommendations.
    upper_half_normalized_recommends = get_recommendations(upper_half_normalized)

    # Possible other metrics
    #   - Probability of higher-rank elsewhere
    #     This promotes those elements that are unusally similar to a particular gap,
    #     relative to its ranking on all other gaps.
    #       -> Worth investigating other statistical measure of outliers.
    #
    #   - Posterior probability as calculated by Bayes.

    output_path = gaps_path.replace("0732_embeddings", "0733_recommendations").replace(os.altsep+"gaps", "")
    output_path = output_path.split("_-_proposed_updates_-_embedding_memory.json")[0] + "_-_recommendations.json"

    # output_recommendations = {k:list(v.keys()) for k,v in standard_recommendations.items()}
    
    output_recommendations = {}

    for gap_name, resources in standard_recommendations.items():

        output_recommendations[gap_name] = []

        for resource_title, score in resources.items():

            metadata = lre[resource_title]["data"]

            output_recommendations[gap_name].append({
                "score": float(score),
                **metadata
            })

    with open(output_path, 'w', encoding="utf-8") as fil:
        json.dump(output_recommendations,
                 fil,
                 ensure_ascii=False,
                 indent=4)
#
