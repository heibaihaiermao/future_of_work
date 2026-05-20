##
# This file does a simple re-organization of a data product,
# Beginning with a list of GSBPM phases/sub-process updates,
# then grouping by implicated work-descriptions.

import json
from operator import itemgetter
from collections import defaultdict
from datetime import date

class dictgetter():

    def __init__(self, *keys):
        self.keys = keys
        self.getter = itemgetter(*keys)

    def __call__(self, d):
        return {k: d[k] for k in self.keys}


def today():
    return date.today().isoformat()

if __name__ == "__main__":
    with open("../03_implicating_GSBPM_updates_to_wd/data/results/mapping_results/2025-10-01_-_direct_mapping_-_GSBPM_updates_to_work-descriptions.json", 'r', encoding="utf-8") as fil:
        gsbpm_updates = json.load(fil)
    
    
    # Init getters.
    get_common_update_elements = dictgetter("title", "id", "description") 
    get_wd_specific_elements = dictgetter("justification") 
    
    
    # Init. output element
    wd_summary = defaultdict(list)
    
    for update_i in gsbpm_updates:
        update_elements = get_common_update_elements(update_i)
    
        for wd_i in update_i["implicated work-descriptions"]:
    
            # collect essential items from work-description
            wd_elements = get_wd_specific_elements(wd_i)
    
            # Attribute these into a the list of relevant updates, according
            # to the work-description  title.
            update_implication = update_elements.__or__(wd_elements)
    
            # Ensure correct ordering.
            update_implication = {key: update_implication[key] for key in ("title", "id", "description", "justification")}
    
            # attribute by title
            wd_title = wd_i["title"]
            wd_summary[wd_title].append(update_implication)
    
    
    
        
    
    # Save results
    with open(f"data/results/{today()}_-_work_descriptions_-_with_implicated_GSBPM_updates.json", 'w', encoding="utf-8") as fil:
        json.dump(wd_summary, fil)

