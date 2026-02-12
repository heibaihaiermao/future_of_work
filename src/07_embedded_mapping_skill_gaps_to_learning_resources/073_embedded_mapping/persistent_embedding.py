import os
import json
import atexit
import numpy as np
import pandas as pd

from time import sleep
from itertools import tee, filterfalse, starmap
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
            #except RateLimitError, StopIteration:
        
                #self.lr_memory = self.lr_memory.__or__(self.lr_dict)
                self.lr_memory.update(self.lr_dict)
                with open(self.memory_path, 'w', encoding="utf-8") as fil:
                    json.dump(self.lr_memory, fil)
        
                break

            self.lr_dict[k] = d 


def collect_embeddings(dir_path, key_attribute="title"):

    embedder = embedding_collector(dir_path, key_attribute=key_attribute)
    embedder.persistent_embed(dir_path)

    backoff_wait_time = 1
    while bool(embedder.lr_dict):
        print(len(embedder.lr_memory))
        embedder.persistent_embed(dir_path)
        backoff_wait_time *=2
        sleep(backoff_wait_time)



    lre = embedder.lr_memory
    return lre
