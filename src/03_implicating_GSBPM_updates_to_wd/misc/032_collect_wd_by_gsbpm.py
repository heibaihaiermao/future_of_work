import json
from operator import itemgetter
# Work need to work on: all.json
with open("all.json", 'r', encoding="utf8") as fil:
    data = json.load(fil)

id_getter = itemgetter("id")

 #find the first dectionaly element of data, get the keys of the first element(dictionary), then find the last key from that dict
key = list(data[0].keys())[-1] 
phases_getter = itemgetter(key)
#phases_getter = itemgetter('implicated phases and sub-processes')
get_wd_ids = lambda x: (x['title'],
                        list(map(id_getter, phases_getter(x))))

wd_ids = map(get_wd_ids, data)
wd_ids = dict(wd_ids)

all_ids = set([])
all_ids.update(*wd_ids.values())

# identify which wd are implicated with which elements
ids_with_phases = {}
for id_i in sorted(all_ids):
    ids_with_phases[id_i] = list(filter(lambda x: wd_ids[x].__contains__(id_i),
                                        wd_ids.keys()))



#all_elements = (wd_i['implicated phases and sub-processes'] for wd_i in data)
