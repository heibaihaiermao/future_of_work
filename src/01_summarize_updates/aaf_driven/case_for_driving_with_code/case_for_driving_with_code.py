import numpy as np
import matplotlib.pyplot as plt

from json import load as jload
from operator import itemgetter
from collections import defaultdict

from matplotlib.ticker import MaxNLocator


## Decreasing reasoning with context

with open("2025-09-23_-_extracted_updates_with_reasoning.json",
          'r',
          encoding="utf-8") as fil:
    r = jload(fil)

# remove useless "update" wrapper
get_update = itemgetter("update")
r = map(get_update, r)
r = list(r)

# calc. length of reasoning for each update
get_reasoning = itemgetter("phase distribution reasoning")
reasonings  = map(get_reasoning, r)
reasoning_lengths = map(len, reasonings)
reasoning_lengths = list(reasoning_lengths)

# calc. trend
def get_lin_fit(reasoning_lengths):
    lin_input = np.matrix(np.dstack((np.ones_like(reasoning_lengths),
                                     np.arange(len(reasoning_lengths)))))
    
    coeffs, *_  = np.linalg.lstsq(lin_input,
                                  np.matrix(reasoning_lengths).T)
    
    fit = (lin_input*coeffs).tolist()
    return fit

reasoning_trend = get_lin_fit(reasoning_lengths)

# Scatter plot reasoning-lengths with trend line.
ax = plt.figure().gca().yaxis.set_major_locator(MaxNLocator(integer=True))
plt.title("Length of reasoning on \"how to apply update\" per update")
plt.xlabel("Update index")
plt.ylabel("Number of characters")
plt.scatter(range(len(reasoning_lengths)),
            reasoning_lengths,
            label="observed")
plt.plot(reasoning_trend, "--", label="trend")
plt.legend()
plt.savefig("length_of_reasoning_trend_per_update.png")
plt.show()
plt.close()


####

# Plot updates per slide

updates_by_slide = defaultdict(list)
for u in r:
    updates_by_slide[u["slide number"]].append(u)

n_updates_per_slide = zip(updates_by_slide.keys(),
                          map(len,updates_by_slide.values()))

slide_numbers = list(map(str, updates_by_slide.keys()))
n_updates_per_slide = list(map(len,updates_by_slide.values()))


plt.close()
#plt.figure()
ax = plt.figure().gca().yaxis.set_major_locator(MaxNLocator(integer=True))
plt.title("Updates identified per slide")
plt.xlabel("Slide number")
plt.ylabel("Number of updates")
plt.bar(slide_numbers, n_updates_per_slide)
plt.savefig("updates_extracted_trend_per_slide_-_possible_one-shot.png")
plt.show()
plt.close()


###

# Phase implicated per update.
implicated_phases_per_update = [len(u_i['implicated phases and subphases']) for u_i in r]

implications_trend = get_lin_fit(implicated_phases_per_update)

plt.close()
#plt.figure()
ax = plt.figure().gca().yaxis.set_major_locator(MaxNLocator(integer=True))
plt.title("Implicated Phases/Sub-Processes by Extracted Update")
plt.xlabel("Update index")
plt.ylabel("Number of implicated phases/sub-proc.")
plt.scatter(np.arange(len(implicated_phases_per_update)),
            implicated_phases_per_update,
            label="observed")
plt.plot(implications_trend, "--", label="trend")
plt.legend()
plt.savefig("implicated_phases_or_sub-process_trend_per_extracted_update.png")
plt.show()
plt.close()

###

# Phase/sub-proc. Implicated work-descriptions

mappings_path = "implicated_work-descriptions_-_t2.json"

with open(mappings_path, 'r', encoding='utf-8') as fil:
    w = jload(fil)


implicated_wd = [len(w_i['implicated work-descriptions']) for w_i in w]

plt.close()
ax = plt.figure().gca().yaxis.set_major_locator(MaxNLocator(integer=True))
plt.title("Number of work-descriptions implicated by phase/sub-proc")
#plt.title("Work-descriptions by phase/sub-proc.")
plt.xlabel("Phase/sub-proc. index")
plt.ylabel("Implicated Work-descriptions.")
plt.scatter(range(len(implicated_wd)),
            implicated_wd,
            label="observed")

implications_trend = get_lin_fit(implicated_wd)
plt.plot(implications_trend,
         "--",
         label="trend")
plt.legend()
plt.savefig("implicated_work-descriptions_trend_per_phase_or_sub-process.png")
plt.show()

###

# Update - Implicated work-descriptions (EC-02)
mappings_path = "direct_mapping_-_updates_to_work-descriptions/2025-10-01_-_direct_mapping_-_GSBPM_updates_to_work-descriptions.json"
with open(mappings_path, 'r', encoding='utf-8') as fil:

    w = jload(fil)

implicated_wd = [len(w_i['implicated work-descriptions']) for w_i in w]

plt.close()
#plt.figure()
ax = plt.figure().gca().yaxis.set_major_locator(MaxNLocator(integer=True))
plt.title("Number of EC-02 work-descriptions implicated by update")
#plt.title("Work-descriptions by Update")
plt.xlabel("Update index")
plt.ylabel("Implicated Phases/sub-proc.")
plt.scatter(range(len(implicated_wd)),
            implicated_wd,
            label="observed")

implications_trend = get_lin_fit(implicated_wd)
plt.plot(implications_trend,
         "--",
         label="trend")
plt.legend()
plt.savefig("implicated_EC02_work-descriptions_trend_per_update.png")
plt.show()
