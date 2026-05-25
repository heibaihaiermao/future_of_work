from itertools import filterfalse, combinations, starmap, tee, repeat, chain
from operator import itemgetter
from functools import partial
from collections import defaultdict
from json import load, dump, dumps, loads, JSONDecodeError
from tqdm import tqdm
from threading import Thread

from assistant import Assistant, persistent_send


    
    # Reorder by gaps, rather than by updates.
    # Find overlapping skills among updates.
    #   - Suggest phrasing of skills that best captures all items.

    # [After] map to standard cases.

    ## ALT:
    #    - Map all gaps to standard skills.
    #    - Collect highest scoring skills.

    ## ALT:
    #  - reformat gaps into similar format.
    #  - Apply embedding, perform vector distance.
    #     - Provides matching, or first filter.

def flatten_json(d):
    for update_i in d:
        non_list_items = filterfalse(lambda k: type(update_i[k]) == list,
                                     update_i.keys())

        non_list_items = set(non_list_items)

        d_i = {k: update_i[k] for k in non_list_items}

        for element_i in update_i["affected work-description elements"]:
            non_list_items = filterfalse(
                                lambda k: type(element_i[k]) == list,
                                element_i.keys())
    
            non_list_items = set(non_list_items)
            d_j = {k: element_i[k] for k in non_list_items}
            d_ij = d_j.__or__(d_i)
            for gap_i in element_i["gaps"]:
                #d_ijk = d_ij.__or__(gap_i)
                d_ijk = gap_i.__or__(d_ij)

                #l.append(d_ijk)
                yield d_ijk



reshape_dict = lambda ddijk: {"name": ddijk["name"],
                              "type": ddijk["type"],
                              "description": ddijk["description"],
                              "causes": [
                                    {"affected": ddijk["element"],
                                     "update": ddijk["update description"],
                                     "impact": ddijk["element update reasoning"]}],
                              "justification": {"since": ddijk["justification"],
                                                "therefore": ddijk["element update reasoning"]}}

 
if __name__ == "__main__":

    wd_file_name = "Junior_Evaluation_Officer_-_proposed_updates.json"
    input_file_path = "../05_forecast_skill_gaps_of_wd/data/updated_wd_with_skills/" + wd_file_name

    with open(input_file_path, 'r') as fil:
        d = load(fil)

   
    flat_gaps = flatten_json(d)
    #flat_gaps = pd.DataFrame.from_dict(flat_gaps)
    flat_gaps = map(reshape_dict, flat_gaps)
    
    with open("comparer_history.json", 'r') as fil:
        try:
            det_history = load(fil)

        except JSONDecodeError:
            det_history = {}

    
    def make_id(s1, s2):
        unique_id = sorted((s1, s2))
        unique_id = " + ".join(unique_id)
        return unique_id
                            

    skill_pairs = combinations(flat_gaps, 2)
    skill_pairs = filterfalse(
            lambda x: det_history.__contains__(make_id(x[0]["name"],
                                                       x[1]["name"])),
            skill_pairs)

    skill_pair_iter, messages_iter = tee(skill_pairs)

    # Init comparer, make and send messages.
    make_pair_dict = lambda x, y: {"skill1": x, "skill2": y}
    messages_iter = starmap(make_pair_dict, messages_iter)
    messages_iter = map(dumps, messages_iter)

    with open("comparer_prompt.txt", 'r') as fil:
        comparison_prompt = fil.read()


    #n_threads = 3
    #comparers = [Assistant(comparison_prompt) for i in range(n_threads)]

    #for comparer_i in comparers:
    #    comparer_i.proc_thread = Thread(target=comparer_i.send_message, 
    #                             args=(next(messages_iter), ))
    #    comparer_i.proc_thread.start()


    #comparers_iter = chain.from_iterable(repeat(comparers))
    #for message_i in tqdm(messages_iter, total=791):
    #    is_taken = False

    #    while is_taken is False:

    #        #for comparer_i in comparers:
    #        comparer_i = next(comparers_iter)
    #        if not comparer_i.proc_thread.is_alive():

    #            comparer_i.proc_thread = Thread(target=comparer_i.persistent_send, 
    #                                       args=(message_i, ))
    #            comparer_i.proc_thread.start()

    #            is_taken = True



    #make_comparer = partial(Assistant, comparison_prompt)
    #threads = [Thread(target=make_comparer) for i in range(n_threads)]

    # Create reponse iterater.
    comparer = Assistant(comparison_prompt)
    #send_message = partial(persistent_send, comparer.send_message)
    #send_message = partial(comparer.send_fresh, comparer.send_message)
    determinations = map(comparer.send_fresh, messages_iter)

    # Grab names from skills.
    get_names = itemgetter('name')
    get_tuple_names = partial(map, get_names)
    skill_name_pairs = map(get_tuple_names, skill_pair_iter)
    skill_name_pairs = map(list, skill_name_pairs)

    # Get name from each item, in each tuple (pair).
    skill_names = chain.from_iterable(skill_pair_iter)
    skill_names = map(get_names, skill_names)
    skill_name_pairs = (
            (a["name"], b["name"])
            for a, b in skill_pair_iter
        )


    # bundle pair with response.
    labeled_determinations = zip(skill_name_pairs, determinations)

    # combos: dict to collect which pairs should be linked.
    combos = defaultdict(list)

    # io memory.
    saved_determinations = []
    errors = []

    # skills set, memory for set of skills.
    skills_set = set()
    for all_items in tqdm(labeled_determinations, total=276):   # total = num of skills choose 2
        print(all_items)
        (s1, s2), determination = all_items
        skills_set.update({s1, s2})
        if determination.startswith("json"):
            determination = determination[4:].strip("```")

        elif determination.startswith('```'):
            determination = determination.strip("```")
            if determination.startswith("json"):
                determination = determination[4:]

        try:
            determination = loads(determination)

        except JSONDecodeError:
            errors.append(make_id(s1, s2))
            determination = {"determination": determination}


        if determination["determination"] == "COULD BE COMBINED":
            # symmetric update to combos.
            combos[s1].append(s2)
            combos[s2].append(s1)

        saved_determinations.append(all_items)

    # Add determinations to det_history.
    for (s1, s2), det_raw in saved_determinations:
        det = det_raw.strip("```")

        if det.startswith("json"):
            det = det[4:].strip("```")

        unique_id = sorted((s1, s2))
        unique_id = " + ".join(unique_id)

        try:
            det_history[unique_id] = loads(det)

        except JSONDecodeError:
            det_history[unique_id] = det

    # Write determination history to file
    history_file_path = "det_history-" + wd_file_name + ".json"
    with open(history_file_path, 'w', encoding='utf-8') as fil:
            dump(det_history, fil, indent=2, ensure_ascii=False)


#class cluster():
#
#    def parse_cluster(G, cluster=set()):
#        for s1, s2 in G.edges():
#            novel_items = filterfalse(cluster.__contains__,
#                                      chain.from_iterable(G[s1].keys(),
#                                                          G[s2].keys()))
#
#            while novel_items:
#                pass

    def yield_cluster(G, s1, cluster=set()):
        yield s1
        cluster.update(s1)
        novel_items = filterfalse(cluster.__contains__,
                                  G[s1].keys())

        for si in novel_items:
            yield from yield_cluster(G, si, cluster=cluster)

    def check_clusters(cluster_list, si):
        return not any((cluster_i.__contains__(si) for cluster_i in cluster_list))








#            map(parse_cluster, novel_items)
#            for si in novel_items:
#                cluster.update(si)
#



#    from itertools import repeat
#    class strumer():
#        def __init__(self, actors):
#            self.actors = actors
#
#        def send_message(self, message):
#
#            is_taken = False
#            takers_iter = repeat(actors)
#
#            while is_taken is False:
#                actor_i = next(takers_iter)
#                if not actor_i.thread.is_alive():
#                    
#                    actor_i.send_message(message_i)
#
#
#
#                    actor_i.thread = Thread(target=actor_i.send_message
#                                            args=(message_i, ))
#                    actor_i.thread.start()
#
#                    is_taken = True
#
#
