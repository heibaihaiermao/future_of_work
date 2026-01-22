import numpy as np
import pandas as pd

from sys import path
path.append("../0X_update_work_descriptions/")
from distill_skill_gaps import flatten_json, reshape_dict as format_gap_skill

#from sys import path
#path.append("../0X_update_work_descriptions/")
#from distill_skills_gaps import flatten_json
from json import load as jload, loads as jloads, dumps as jdumps, dump as jdump
from csv import DictReader
#from assistant import Assistant
from embedding_model import embedding_model
from itertools import islice, tee, chain
from operator import itemgetter

def read_tb_skills():
    with open("../0X_update_work_descriptions/data/GC_Digital_Talent_-_All_skills.csv", 'r', encoding='utf-8-sig') as fil:
        yield from fil

def label_tb_skills():
    csv_lines = read_tb_skills()
    runt_header = next(csv_lines)

    # instead yield full header
    yield '"ID","name_en","category_en","skillFamilies_en","description_en","name_fr","category_fr","skillFamilies_fr","description_fr"'

    yield from csv_lines

def get_tb_skills():
    labeled_csv_lines = label_tb_skills()
    tb_skills_dict = DictReader(labeled_csv_lines)
    yield from tb_skills_dict

def format_tb_skill(tbi):
    return {"name": tbi["name_en"],
            "category": tbi["category_en"],
            "skillFamilies": tbi["skillFamilies_en"],
            "description": tbi["description_en"]}

#def format_gap_skill(gsi):
#    return {"name": gsi["name"],
#            "type": gsi["type"],

def get_sc_skills():
    t = pd.read_excel("Talent_bank_glossary_-_banque_de_talents_gloassaire.xlsx")

    rows = t.iterrows()
    rows = chain.from_iterable(rows)
    rows = islice(rows, 1, None, 2)
    rows = map(dict, rows)
    yield from rows


def format_sc_tb_row(row):
    return {"name": row["Skills"],
            #"category": row["category_en"],
            "skillFamilies": row["Category"],
            "description": row["Definition"]}





if __name__ == "__main__":
    with open("../0X_update_work_descriptions/data/updated_wd_with_skills/Economist_-_Sociologist_2_-_proposed_updates.json", 'r') as fil:
        d = jload(fil)
    d = flatten_json(d)
    d = map(format_gap_skill, d)
    d = map(jdumps, d)
    d_labels, d_inputs = tee(d, 2)


    #tb_skills = get_tb_skills()
    #tb_skills = map(format_tb_skill, tb_skills)
    #tb_skills = map(jdumps, tb_skills)

    #with open("tb_embedding_memory.json", 'r') as fil:
    #    tb_skills_embed = jload(fil)

    
    #embed = embedding_model()
    #tb_skills_embed = embed.embed(tb_skills)
    #l = []
    #for tbi in tb_skills_embed:
    #    l.append(tbi)




    ## SC SKILLS ##
    #sc_skills = get_sc_skills()
    #sc_skills = map(format_sc_tb_row, sc_skills)
    #sc_skills = map(jdumps, sc_skills)
    #sc_labels, sc_inputs = tee(sc_skills, 2)

    #embed = embedding_model()
    #sc_skills_embed = embed.embed(sc_inputs)
    #sc_skills_embed = zip(sc_labels, sc_skills_embed)
    #sc_skills_embed = dict(sc_skills_embed)

    #with open("sc_skills_memory.json", 'w') as fil:
    #    jdump(sc_skills_embed, fil)

    with open("sc_skills_memory.json", 'r') as fil:
        sc_skills_embed = jload(fil)



    with open("gap_skills_memory.json", 'r') as fil:
        gap_skills = jload(fil)

    # Get embedding of LLM skills.
    #embed = embedding_model()
    #gap_skills = embed.embed(d_inputs)
    #gap_skills = zip(d_labels, gap_skills)
    #gap_skills = dict(gap_skills)

    #with open("gap_skills_memory.json", 'w') as fil:
    #    jdump(gap_skills, fil)


    
    #tb_skills_embed = gap_skills
    tb_skills_embed = sc_skills_embed

    # Comparison matrix.
    tb_skill_vecs = np.array(list(tb_skills_embed.values()), dtype=float)
    gap_skill_vecs = np.array(list(gap_skills.values()), dtype=float)

    similarity_matrix = np.matmul(tb_skill_vecs,
                                  gap_skill_vecs.T)

    # Normalize similarity matrix
    #   (Each skill gap has a total of "1" point to allocate)
    #similarity_matrix -= np.mean(similarity_matrix, axis=0)
    ##similarity_matrix /= np.std(similarity_matrix, axis=0)
    #similarity_matrix /= np.max(np.abs(similarity_matrix), axis=0)

    #similarity_matrix /= 2
    #similarity_matrix += 0.5


    # score by rank
    similarity_matrix = np.argsort(np.argsort(similarity_matrix, axis=0), axis=0)
    similarity_matrix = np.float64(similarity_matrix)
    #similarity_matrix -= np.mean(similarity_matrix, axis=0)

    similarity_matrix /= np.sum(similarity_matrix, axis=0)



    get_name = itemgetter("name")

    # Construct similarity dataframe.
    inds = map(jloads, tb_skills_embed.keys())
    inds = map(get_name, inds)

    cols = map(jloads, gap_skills.keys())
    cols = map(get_name, cols)

    similarity_df = pd.DataFrame(similarity_matrix, index=inds, columns=cols)

    # Identify top 10 skills per skill-gap.
    top10_per_gap = {k: v.sort_values(ascending=False).iloc[:10].to_dict() for k,v in similarity_df.items()}

    
    print_table = lambda v: print(pd.DataFrame(v.items(), columns=("SC Talent Bank Skill", "Top 10 Similarity Scores")).to_markdown(index=False))

    print("\nEconomist/Sociologist EC-02\n")
    print_table(similarity_df.sum(axis=1).sort_values(ascending=False).iloc[:10].to_dict())
    print("\n")


