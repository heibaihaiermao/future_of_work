from itertools import filterfalse, combinations, starmap, tee, repeat, chain
from operator import itemgetter
from functools import partial
from collections import defaultdict
from json import load as jload, dumps, loads, JSONDecodeError
from pickle import load

from assistant import Assistant, persistent_send
import networkx as nx


def get_set_of_skills(det_history):
    set_of_skills = (s.split(" + ") for s in det_history.keys())
    set_of_skills = chain.from_iterable(set_of_skills)
    set_of_skills = set(set_of_skills)
    return set_of_skills


def get_connected_skills(det_history):
    connected_skills = filter(lambda k: check_det(k[1]),
                              det_history.items())
    yield from connected_skills


split_id = partial(str.split, sep=" + ")
def make_graph(det_history, set_of_skills):
    G = nx.Graph()

    for si in set_of_skills:
        G.add_node(si)


    connected_skills = filter(lambda k: check_det(k[1]),
                              det_history.items())

    for uid, v in connected_skills:
        s1, s2 = split_id(uid)
        G.add_edge(s1, s2)

    return G


def check_det(det):
    try:
        s = det["determination"]

    except TypeError:
        s = det

    return s.upper().__contains__("COULD BE COMBINED")


make_id = lambda s1, s2: " + ".join(sorted((s1, s2)))
def get_all_connections(cluster, G):
    connections = set()
    for si in cluster:
        for sj in G[si].keys():
            uid = make_id(si, sj)
            connections.update({uid})
    return connections


def define_subgraph(cluster, G):
    subG = nx.Graph()
    for si in cluster:
        subG.add_node(si)

    connections = get_all_connections(cluster, G)
    for pair in connections:
        s1, s2 = sorted(pair.split(" + "))
        subG.add_edge(s1, s2)

    return subG


def yield_cluster(G, s1, cluster=set()):
    '''Recursively search through a graph to find \
       all items that belong to an isolated sub-graph.
       Produces a generator that yields the nodes.'''

    yield s1
    cluster.update({s1})
    novel_items = filterfalse(cluster.__contains__,
                              G[s1].keys())

    for si in novel_items:
        yield from yield_cluster(G, si, cluster=cluster)


def check_clusters(cluster_list, si):
    return not any((cluster_i.__contains__(si) for cluster_i in cluster_list))



if __name__ == "__main__":

    with open('comparer_history.json', 'r') as fil:
        det_history = jload(fil)

    ss = sorted(set(get_set_of_skills(det_history)))
    G = make_graph(det_history, ss)

    clusters = []
    for si in ss:
        if check_clusters(clusters, si):
            cluster_i = list(yield_cluster(G, si))
            clusters.append(cluster_i)



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
