import re
import yaml
import json
import textwrap
import pandas as pd
from collections import deque



path = "2025-09-23_-_updated_descriptions.json"
#path = "f7_phases1-3_-_implicated_updates.json"
with open(path,'r',encoding='utf-8') as fil:
    js = json.load(fil)

dsub = pd.DataFrame((d_i.values() for d_i in js), columns=js[0].keys())
#dsub = d[d['id'].apply(float) < 4]

def process(s):
    processed_string = re.sub(r"\\u....", "-", s.replace(r"\n", '\n    ').replace("\n    \\","").replace(r"\ "," "))

    processed_string = processed_string.replace("update application to description reasoning", "update reasoning")
    return processed_string


def line_wrap(s_i, line_length=80):
    if s_i.__contains__(":"):
        zfill = s_i.index(":") + 2

    elif s_i.__contains__("  - "):
        zfill = len(s_i) - len(s_i.lstrip()) + 2

    else:
        zfill = len(s_i) - len(s_i.lstrip())

    wrap_budget = line_length - zfill
    whitespace = " " * zfill

    first_line = textwrap.fill(s_i, line_length).splitlines()[0]
    yield first_line

    # Wrap additional lines with whitespace.
    new_lines = textwrap.fill(s_i[len(first_line):], wrap_budget)
    new_lines_iter = iter(new_lines.splitlines())
    #yield next(new_lines_iter)
    for raw_line in new_lines_iter:
        #line = raw_line.lstrip(" ")
        line = whitespace + raw_line.lstrip(" ")
        zline = line.zfill(line_length)
        padded_line = line + " " * (len(zline) - len(line))

        # DEV additional (3rd and above) may require removing
        #     one space.
                             
        yield padded_line


has_stuff = lambda s: bool(s.strip())
line_join = "\n".join
#def wrap_lines(s_l, line_length=80):
#    line_iterators = filter(has_stuff, s_l.splitlines())
#    line_iterators = map(line_wrap, line_iterators)
#    line_iterators = map(line_join, line_iterators)
#    return line_iterators

def yield_attributes_slices(full_string, delim=":"):
    lines = list(filter(has_stuff, full_string.splitlines()))
    attribute_lines = filter(lambda x: bool(x.__contains__(delim)),
                             lines)

    attribute_indices = map(lines.index, attribute_lines)

    slice_indices = deque([0], maxlen=2)

    #try:
    ind = next(attribute_indices)
    #except RuntimeError:
    if ind == 0:
        ind = next(attribute_indices)

    slice_indices.append(ind)
    #yield slice(*slice_indices)
    yield lines[slice(*slice_indices)]
    for ind in attribute_indices:
        slice_indices.append(ind)
        yield lines[slice(*slice_indices)]
        #yield slice(*slice_indices)

    yield lines[slice_indices[-1]:]


def grab_sections(full_string):
    g = yield_attributes_slices(full_string, delim=":")
    for g_i in g:
        try:
            gl = yield_attributes_slices("\n".join((g_i)),
                                         delim="  - ")
            gl = ["\n".join(line_wrap("".join(x))) for x in gl]
        except RuntimeError:

            gl = list(line_wrap(" ".join("".join(g_i).split())))



        yield gl
        #"\n".join(gl) 
            

def process_sections(full_string):
    g = grab_sections(full_string)
    g = map(line_join, g)
    return line_join(g)

from functools import partial
wrap = partial(textwrap.fill, width=120)

def wrap_lines(s, whitespace="  "):
    lines = wrap(s).splitlines()
    padded_lines = map(whitespace.__add__, lines)
    return "\n".join(padded_lines)

def add_point(s):
    full_length = len(s)

    s = s.lstrip(" ")
    unwrapped_length = len(s)

    zfill = full_length - unwrapped_length - 2
    return " "*zfill + "- " + s


def _process_json(obj):
    for k,v in obj.items():
        v_str = str(v)
        k_str = str(k)
        whitespace = "  "
        if len(v_str) + len(k_str) > 80:
            k_str = f"{whitespace}{k}:\n"
            if v_str.__contains__("\n- "):
                vl = filter(lambda x: bool(x.lstrip()),
                            v_str.split("\n- "))

                vl = (wrap_lines(vl_i, whitespace="    ") for vl_i in vl)
                #vl = map(wrap_lines, vl)

                vl = map(add_point, vl)
                v_str = "  " + "\n  ".join(vl)
            else:
                v_str = wrap_lines(v_str, whitespace="    ")
        else:
            
            k_str = f"{whitespace}{k}: "

        yield k_str + v_str

    
double_join = "\n\n".join
def process_json(objs):
    string = map(_process_json, objs)
    string = map(double_join, string)
    return "\n\n---\n\n".join(string)

from copy import deepcopy
def dup_line(df_line):
    df_i = deepcopy(df_line).to_dict()
    ups = df_i["implicated updates"]
    for upd in list(ups):
        df_i["implicated updates"] = [upd]
        yield tuple(df_i.values())

def _xjoin(df):
    for i in range(len(df)):
        yield from dup_line(df.iloc[i,:])

def xjoin(df):
    lines = _xjoin(df)
    columns = df.keys()
    new_df = pd.DataFrame(lines, columns=columns)
    return new_df


dsub = xjoin(dsub)
dsub["implicated updates"] = dsub["implicated updates"].apply(process_json)

excel_path = path.split(".")[0] + ".xlsx"
1/0
dsub.to_excel(excel_path, index=False)
#line_join = "\n".join
#a = dsub['implicated updates'].iloc[0]

#dsub['yaml'] = dsub['implicated updates'].apply(yaml.safe_dump).apply(process).apply(process_sections)
#g = grab_sections(a)
#i1 = next(g)
#g1 = next(g)
#i2 = next(g)
#g2 = next(g)
#i3 = next(g)
#g3 = next(g)
#i4 = next(g)
#g4 = next(g)
#i5 = next(g)
#g5 = next(g)
#g = map(line_join, g)
#print(line_join(g))


