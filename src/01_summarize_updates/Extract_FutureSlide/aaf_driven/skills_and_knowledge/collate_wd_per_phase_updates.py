from json import load as jload, dump as jdump
from operator import itemgetter

def validate_all_desc_equal(l, key="description"):
    l = iter(l)
    first_item = next(l)
    eq_test = first_item[key].__eq__
    key_getter = itemgetter(key)

    key_values = map(key_getter, l)
    desc_eq = map(eq_test, key_values)
    assert all(desc_eq)

phases = ['2', '2.1','2.2', '4.4', '5.8', '7.1']



class common_item_collector():
    def __init__(self, data, gsbpm_wd_updates):
        self.data = data
        self.gsbpm_wd_updates = gsbpm_wd_updates

    def collate_all_reasoning_and_updates(self, sub_data, key="description"):
        phases_iter = iter(phases)
        desc = sub_data[0][key]
    
        validate_all_desc_equal(sub_data, key=key)
    
        for li in sub_data:
            li.pop(key)
    
            phase_i = next(phases_iter)
            #li["element"] = phase_i
    
            gsbpm_prop = list(filter(lambda x: phase_i.__eq__(x["id"]),
                                             self.gsbpm_wd_updates["implicated phases and sub-processes"]))
            li["element"] = gsbpm_prop[0]



        # Sort keys
        sl = map(sorted, (li.items() for li in sub_data))
        sl = map(dict, sl)
        sl = list(sl)
        return {key: desc, "updates": sl}



    def collect_common_items(self, wd_attribute="Key Activities"):
        ka_getter = itemgetter(wd_attribute)
        ka = map(ka_getter, self.data)
        
        # order for each key-activity is aligned 
        ka_phases = zip(*ka)
        
        updates = map(self.collate_all_reasoning_and_updates, ka_phases)
    
        return (wd_attribute, list(updates))



def collate_data(data, gsbpm_wd_update):
    collector = common_item_collector(data, gsbpm_wd_update)
    for k in data[0].keys():
        print(k)
        if type(data[0][k]) == list:
            reordered_element = collector.collect_common_items(wd_attribute=k)
    
        elif type(data[0][k]) == dict:
            #asr_key = "technical activities, skills, responsibilities, or efforts"
            asr_getter = itemgetter(k)
            activities_skills_resps = map(asr_getter, data)
            activities_skills_resps  = list(activities_skills_resps)
            
            sub_collector = common_item_collector(activities_skills_resps, gsbpm_wd_update)
            ordered_asr = map(sub_collector.collect_common_items,
                              asr_getter(data[0]).keys())
            
            ordered_asr = dict(ordered_asr)
            reordered_element = (k, ordered_asr)

        elif type(data[0][k]) == str:
            reordered_element = (k, data[0][k])
    
        yield reordered_element


if __name__ == "__main__":
    wd_updates_path = "Metadata_prod_and_dissem_officer.json"
    
    with open(wd_updates_path, 'r', encoding="utf-8") as fil:
        data = jload(fil)

    with open("../direct_mapping_-_updates_to_work-descriptions/all.json", 'r', encoding='utf-8') as fil:
        gsbpm_updates = jload(fil)
    gsbpm_wd_updates = gsbpm_updates[-2]

    compressed_data = collate_data(data, gsbpm_wd_updates)
    compressed_data = dict(compressed_data)

    #for cd_ele in [compressed_data["Key Activities"],
    #               compressed_data['technical activities, skills, responsibilities, or efforts']]:
    #    for i in range(len(cd_ele)):

    #        phases_iter = iter(phases)
    #        for wd_update_i in cd_ele[i]["updates"]:
    #            phase_i = next(phases_iter)
    #            gsbpm_prop = list(filter(lambda x: phase_i.__eq__(x["id"]),
    #                                     gsbpm_wd_updates["implicated phases and sub-processes"]))
    #            wd_update_i["element"] = gsbpm_prop[0]

    with open("reordered_"+wd_updates_path, 'w', encoding="utf-8") as fil:
        jdump(compressed_data, fil, indent=4)
