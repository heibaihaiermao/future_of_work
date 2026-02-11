import os
import json
import atexit
import numpy as np
import pandas as pd

from itertools import tee, filterfalse
from operator import itemgetter
from openai import RateLimitError
from dotenv import load_dotenv
load_dotenv("embedding.env")

from embedding_model import embedding_model
def read_json_files(input_dir):
    input_files = os.listdir(input_dir)
    input_files = map(lambda s: input_dir+"/"+s, input_files)
    for path in input_files:
        with open(path, 'r', encoding="utf-8-sig") as fil:
            input_data = map(json.loads, fil)
            yield from input_data



class embedding_collector():
    def __init__(self, lr_dir, key_attribute="title"):
        self.lr_dir = lr_dir
        self.memory_path = f"{self.lr_dir.split(os.altsep)[-1]}_memory.json"
        self.key_attribute = key_attribute

        self.recommender = embedding_model()
        atexit.register(self.recommender.client.close)


    def load_memory(self):
        try:
            with open(self.memory_path, 'r', encoding="utf-8-sig") as fil:
                self.lr_memory = json.load(fil)

        except FileNotFoundError:
            self.lr_memory = {}


    def filter_unseen(self, lr_data):
        try:
            previous_keys = self.lr_memory.keys()

        except AttributeError:
            self.load_memory()
            previous_keys = self.lr_memory.keys()

        previously_embedded = previous_keys.__contains__
        lr_data = filterfalse(lambda d: previously_embedded(d[self.key_attribute]),
                              lr_data)
        yield from lr_data


    def load_unseen(self, lr_dir): #, memory_path=None):
        lr_data = read_json_files(lr_dir)
    
        #if memory_path is None:
        #    memory_path = f"{self.lr_dir.split(os.altsep)[-1])}_memory.json"
    
        lr_data = self.filter_unseen(lr_data) #, self.memory_path)
        yield from lr_data


    def embed_JSONs(self, lr_json):
        #recommender = embedding_model()
        #atexit.register(recommender.client.close)
    
        lr_str = map(json.dumps, lr_json)
        lr_embed = self.recommender.embed(lr_str)
        yield from lr_embed
    
    
    def generate_unseen_embeddings(self, lr_dir):
        lr_data = self.load_unseen(lr_dir)
        lr_j , lr_label = tee(lr_data, 2)
        lr_embed = self.embed_JSONs(lr_j)
        
        lr_dict = zip(lr_label, lr_embed)
        lr_dict = ((j[self.key_attribute], {"data": j, "vec": v}) for j,v in lr_dict)
        yield from lr_dict


    def persistent_embed(self, lr_dir):
        lr_embeddings = self.generate_unseen_embeddings(lr_dir)
    
        self.lr_dict = {}
        while True:
            try:
                k, d = next(lr_embeddings)

            except StopIteration:
                break

            except RateLimitError:
        
                #self.lr_memory = self.lr_memory.__or__(self.lr_dict)
                self.lr_memory.update(self.lr_dict)
                with open(self.memory_path, 'w', encoding="utf-8") as fil:
                    json.dump(self.lr_memory, fil)
        
                break

            self.lr_dict[k] = d 


get_vec = itemgetter("vec")

#def collect_embeddings

lr_dir = "data/input/learning-resources"
embbeder = embedding_collector(lr_dir, key_attribute="title")
embbeder.persistent_embed(lr_dir)
lre = embbeder.lr_memory

lrdf = pd.DataFrame.from_dict(lre).T["vec"]

lrm = np.matrix(list(map(get_vec, lre.values())))
lrkl = list(lre.keys())

gaps_dir = "data/input/gaps"
embbeder = embedding_collector(gaps_dir, key_attribute="development area")
embbeder.persistent_embed(gaps_dir)
ge = embbeder.lr_memory

gdf = pd.DataFrame.from_dict(ge).T["vec"]

gm = np.matrix([ge[k]["vec"] for k in ge.keys()])
#gkl = list(ge.keys())

def create_cosine_similarity_df(column_series, row_series):
    column_matrix = np.matrix(np.vstack(column_series))
    column_norm = np.matrix(np.linalg.norm(column_matrix, axis=1))

    row_matrix = np.matrix(np.vstack(row_series))
    row_norm = np.matrix(np.linalg.norm(row_matrix, axis=1))

    cosine_similarity_matrix = (row_matrix * column_matrix.T) / (row_norm.T * column_norm)

    cosine_similarity_df = pd.DataFrame(cosine_similarity_matrix,
                                        columns=column_series.index,
                                        index=row_series.index)

    return cosine_similarity_df

    


# Define comparison matrix.
cdf = pd.DataFrame(np.matrix(np.vstack(lrdf))*np.matrix(np.vstack(gdf)).T,
                   columns = gdf.index,
                   index=lrdf.index)
comparison = lrm*gm.T 
compn = comparison / (np.matrix(np.linalg.norm(lrm, axis=1)).T* np.matrix(np.linalg.norm(gm, axis=1)))

# Scale so that each course is has equal mean similarity.
comparison2 = comparison / np.mean(comparison, axis=1)

# Remove bottom half before scaling.
comparison[np.array(np.argsort(np.mean(comparison, axis=1).T)[:,:len(gkl)//2])[0]] = 0

def get_recommendations_from_comps(comps):
    rank_order = np.argsort(comps, axis=0)
    ranked_indices = np.arange(len(lrm))[rank_order]
    top_indices = ranked_indices[-10:, :][::-1]
    
    #recommendations = {gap_k: [lrkl[j]
    recommendations = {gkl[i]: [{lrkl[j]:comps[j,i]} for j in gap_10_recommends] for i, gap_10_recommends in enumerate(top_indices.T)}
    return recommendations
    
#with open("preliminary_recommendations.json", 'w', encoding="utf-8") as fil:
#    json.dump(recommendations, fil, ensure_ascii=False, indent=4)



#def cosine_similarity(u, v):
#    mag_u = np.sqrt(np.vecdot(u, u))
#    mag_v = np.sqrt(np.vecdot(v, v))
#
#    num = np.vecdot(u,v)
#    return num / mag_u / mag_v
