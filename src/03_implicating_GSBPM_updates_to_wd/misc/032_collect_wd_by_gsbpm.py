import json
from operator import itemgetter

with open("all.json", 'r', encoding="utf8") as fil:
    data = json.load(fil)

id_getter = itemgetter("id")

key = "implicated phases and sub-processes"
phases_getter = itemgetter(key)

get_wd_ids = lambda x: (
    x['title'],
    [item['id'] for item in phases_getter(x)]
)

wd_ids = dict(map(get_wd_ids, data))

all_ids = set()
all_ids.update(*wd_ids.values())

ids_with_phases = {}
for id_i in sorted(all_ids):
    ids_with_phases[id_i] = [
        wd for wd in wd_ids if id_i in wd_ids[wd]
    ]

# PRINT RESULTS
print(json.dumps(ids_with_phases, indent=2))

# SAVE TO FILE 
with open("ids_with_phases.json", "w", encoding="utf8") as f:
    json.dump(ids_with_phases, f, indent=2)