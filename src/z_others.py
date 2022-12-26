
# %%

import os
import json
import igraph as ig


def ig_to_json(graph, path):
    assert isinstance(graph, ig.Graph)
    nodes = []
    edges = []

    if not 'layout' in graph.attributes():
        graph['layout'] = graph.layout_auto()

    for v, coords in zip(graph.vs, graph['layout']):
        v_id = str(v.index)
        v_attributes = v.attributes()
        v_label = v_attributes.pop('label', None)
        if not v_label:
            v_label = v_id
        v_size = v_attributes.pop('size', None)
        if v_size:
            v_size = float(v_size)
        v_x = coords[0]
        v_y = coords[1]
        node = dict(id=v_id, label=v_label, size=v_size, x=v_x, y=v_y, attributes=v_attributes)
        nodes.append(node)

    for e in graph.es:
        e_id = str(e.index)
        e_source = str(e.source)
        e_target = str(e.target)
        e_attributes = e.attributes()
        e_size = e_attributes.pop('size', None)
        if e_size:
            e_size = float(e_size)
        edge = dict(id=e_id, source=e_source, target=e_target, size=e_size, attributes=e_attributes)
        edges.append(edge)

    data = dict(nodes=nodes, edges=edges)
    with open(path, 'w') as f:
        json.dump(data, f, ensure_ascii=False)
    return os.path.exists(path)





#%%
import torch
import transformers
from transformers import pipeline


# %%
sentiment_analysis = pipeline("sentiment-analysis")

#%%
pos_text = "today it is raining "
neg_text = "I do not hate chocolate"

result = sentiment_analysis(pos_text)[0]
print("Label:", result['label'])
print("Confidence Score:", result['score'])
print()
result = sentiment_analysis(neg_text)[0]
print("Label:", result['label'])
print("Confidence Score:", result['score'])
# %%

summaries = pipeline("summarization")
summaries(tweets[0], max_length=100, min_length=30, do_sample=False)
# %%