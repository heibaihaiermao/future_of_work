from lxml import etree
from operator import attrgetter, itemgetter
from itertools import islice, accumulate, groupby, chain, takewhile, dropwhile
from functools import partial
from collections import deque
from time import sleep

import pandas as pd

def read_html(path):
    with open(path, 'r', encoding="utf-8") as fil:
        cont = fil.read()
    return cont


def iterate_down_tree(obj):
    yield obj

    children = obj.iterchildren()
    for child in children:
        yield from iterate_down_tree(child)

def dig_for_text(table_obj):
    obj_text = table_obj.text
    if obj_text is None or obj_text == "\n":
        for child in table_obj.iterchildren():
            yield from dig_for_text(child)

    else:
        yield obj_text

def dig_for_obj_with_text(table_obj):
    obj_text = table_obj.text
    if obj_text is None or obj_text == "\n":
        for child in table_obj.iterchildren():
            yield from dig_for_obj_with_text(child)

    else:
        yield table_obj


        #yield from map(dig_for_text, table_obj.getchildren())

def _dig_up_headers(h):
    proficiency_levels = map(dig_for_text, h.getchildren()[0].iterchildren())
    proficiency_levels = map(next, proficiency_levels)
    yield from proficiency_levels

def _dig_up_contents(b):
    #b_tr = b.
    # DEV: MODIFY TO WORK FOR MULTIPLE ROWS
    proficiency_indicators= map(dig_for_text, b.getchildren()[0].iterchildren())
    proficiency_indicators = map(list, proficiency_indicators)
    yield from proficiency_indicators


def set_groups(g):
    for a,b in g:
        yield (a, list(b))

acc_join = lambda x,y: ", ".join((x,y))
def variable_permutations(itr, max_len, min_len=1):
    itr = map(str, itr)

    init = islice(itr, max_len-1)
    window = deque(init, maxlen=max_len)

    shift_window = window.append
    for x in itr:
        shift_window(x)
        permutations = accumulate(window, func=acc_join)
        acceptable_permuations = islice(permutations, min_len-1, max_len)
        yield from acceptable_permuations

    window_length = window.__len__
    while window_length() > min_len:
        try:
            window.popleft()

        except IndexError:
            break

        permutations = accumulate(window, func=acc_join)
        acceptable_permuations = islice(permutations, min_len-1, max_len)
        yield from acceptable_permuations

def sliding_window(itr, N):
    #itr = iter(itr)
    itr = map(str, itr)
    init = islice(itr, N-1)
    window = deque(init, maxlen=N)

    shift_window = window.append
    for x in itr:
        shift_window(x)
        yield ", ".join(window)
        #yield list(window)

def growing_window(itr, min_len, max_len):
    for width in range(min_len, max_len):
        yield from sliding_window(itr, width)

def take_first(x):
    yield from islice(x, 1)

def condense(itr, keyfunc=None):
    if keyfunc is None:
        groups = groupby(itr)
    else:
        groups = groupby(itr, key=keyfunc)

    groups = set_groups(groups)
    #items = chain.from_iterable(map(take_first, groups))
    yield from groups




def sort_dict(d):
    sorted_keys = sorted(d, key=d.get)
    sorted_dict = {k:d[k] for k in sorted_keys}
    return sorted_dict


if __name__ == "__main__":
    parser = etree.HTMLParser()

    contents = read_html("data/data_science_functional_group_competency_profile_draft.html")
    html_root = etree.fromstring(contents, parser)
    html_tree = iterate_down_tree(html_root)

    get_tag = attrgetter("tag")
    is_table = lambda o: get_tag(o).__eq__("table")
   
    tables = filter(is_table, html_tree)
    tables = list(tables)

    t = tables[-7]
    c, h, b = t.getchildren()


    proficiency_levels = _dig_up_headers(h)
    proficiency_indicators  = _dig_up_contents(b)
    proficiencies = zip(proficiency_levels, proficiency_indicators)


# def identify patterns
    #siblings = list(t.itersiblings())
    parent = t.getparent()
    siblings = parent.getchildren()
    pattern_elements = ((x.tag, list(dig_for_text(x))) for x in siblings)
    pattern_elements = filter(all, pattern_elements)
    pattern_elements= list(pattern_elements)

    pattern_array = ((pattern_elements.count(pat), *pat) for pat in pattern_elements)



    #pat_tags = [p[0] for p in pattern_elements]
    #tagged_elements = zip(pattern_array, pat_tags)
    take_two = itemgetter(0,1)
    condensed_elements = condense(pattern_array, keyfunc=take_two)
    condensed_elements= list(condensed_elements)

    first = itemgetter(0)
    pattern_instances = variable_permutations(map(first, condensed_elements),
                                              7,
                                              min_len=3)
    pattern_instances = list(pattern_instances)


    # Find most common pattern instances
    count_pattern_instances = pattern_instances.count
    pattern_occurances = {pat: count_pattern_instances(pat) for pat in set(pattern_instances)}

    pattern_occurances = sort_dict(pattern_occurances)


    # Apply criteria.

    # Must have more than one hit.
    candidates = filter(lambda x: x[1]>3, pattern_occurances.items())

    # Must have elements with more than one occurance
    #def filter_for_multiple_occurances(s, min_occ=4):
    #    elements = eval(s[0])
    #    element_instances = map(take_first, elements)
    #    element_instances = chain.from_iterable(element_instances)
    #    
    #    mappable_le = partial(map, min_occ.__le__)
    #    acceptable_instances = map(mappable_le, element_instances)
    #    return bool(sum(acceptable_instances))



    # Filter for substrings.
    
    candidates = dict(candidates)
    df = pd.DataFrame(candidates.items(), columns=("pat", "occ"))
    pats = deque(df['pat'].to_numpy().tolist())
    pat_i = pats.pop()

    not_substring = []
    for i in range(len(pats)):
        pats.append(pat_i)
        
        pat_i = pats.popleft()
        str_i = pat_i.strip("[]")
        is_sub_i = any((pat_j.__contains__(str_i) for pat_j in pats))
        if not is_sub_i:
            #not_substring.append((pat_i, is_sub_i))
            not_substring.append(pat_i)

    
    df = df[df["pat"].isin(not_substring)]


    def snip_repeating_piece(l):
        rep_start_ind = -1
        
        ## DEV: WHAT IF MULTIPLE REPEATS?
        if l.count(l[rep_start_ind]) == 1:
            return l
        # if there is repetition, iterate looking for non-duplicated piece
        while l.count(l[rep_start_ind]) > 1:
            rep_start_ind -= 1

        return l[:rep_start_ind+1]

    first = itemgetter(0)
    second = itemgetter(1)
    def process(s):
        s = eval(s)
        s = list(s)
        s = snip_repeating_piece(s)

        #s = sorted(s, key=second)
        # Evaluate mis-ordered patterns..
        start = min(s, key=second)
        start_ind = s.index(start)
        s = s[start_ind:] + s[:start_ind]
        s = str(s).strip("[]")
        return s

    df["proc"] = df["pat"].apply(process)

    # Find most common pattern
    grouper = df.groupby("proc")
    group_occ = {k:sum(grouper.get_group(k)["occ"]) for k in df["proc"].drop_duplicates()}
    pattern, _ = max(group_occ.items(), key=second)


    # DEV: Identify pattern length + 1, when common patterns all begin, and end with
    #      same items.


    # If pat_i[0] == pat_i[-1],
    # then pat_i.pop()

    # start = min(pat_i, key=second)
    # start_ind = pat_i.index(start)
    # fin_pat_i = np.roll(pat_i, -start_ind, axis=0)
    instances = []
    icandidates = []

    titles = []

    patl =list(eval(pattern))
    conde = iter(condensed_elements)
    conde_tag = None

    while True:
        conde = dropwhile(lambda x: patl[0].__ne__(first(x)), conde)
    
    
        instance_candidate = islice(conde, len(patl))
        i = 0
        instance = []

        if conde_tag == patl[0]:
            i += 1
        else:
            conde_tag, instance_items = next(conde)

        titles.append((conde_tag, instance_items))
        while i < len(patl) and conde_tag == patl[i]:
            instance.append((conde_tag, instance_items))
    
            i+=1
            conde_tag, instance_items = next(conde)
    
        if i == len(patl):
            instances.append(instance)

        icandidates.append(instance)

        print(instances)
        sleep(1)
        









