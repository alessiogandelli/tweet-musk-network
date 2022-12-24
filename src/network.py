#%%
import os
import igraph as ig
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import pandas as pd
import re

# read csv first column as index 
df = pd.read_csv('/Users/alessiogandelli/dev/uni/tweet-musk-network/data/resign_tweet.csv', index_col=0)
df = df.sort_values('created_at')


musk_id = 44196397
musk_resig = 1604617643973124097
# %%



def explore_tree(n, df_n, total_reply):

    print('al livello ',n ,df_n.shape[0],'reply')
    total_reply += df_n.shape[0]# count total replies 

    if(df_n.shape[0] > 0):
        
        df_n = df_n[df_n['reply_count'] > 0] # filter only the ones that have replies
        print('al livello ',n ,df_n.shape[0], 'reply con reply') 
        print('biggest thread',df_n.value_counts('reply_count').tail(1).index.tolist()[0])
        df_n = df[df['replied_to'].isin(df_n.index)] # take from the main dataset the ones that replied to the ones in df_n
        edges = []

        #append all edges for this level 
        for tweet_id, tweet in df_n.iterrows():
            edges.append((str(tweet_id), str(tweet['replied_to'])))

        g.add_edges(edges) # add edges to the graph
    
        return explore_tree(n+1, df_n, total_reply)
    else:
        return total_reply


''' g contains all the nodes and all the direct answer to musk's tweet (400001, 188636) '''

g = ig.Graph(directed=True)
mentions = []
edges = []
# distance 1 from musk
g.add_vertex(str(musk_resig))

for tweet_id, tweet in df.iterrows():
    g.add_vertex(str(tweet_id), **tweet.to_dict())

    if tweet['replied_to'] == musk_resig:
       edges.append((str(tweet_id), str(musk_resig)))

# distance 2 from musk

g.add_edges(edges)



df_first = df[df['replied_to'] == musk_resig]
total_reply = 0
explore_tree(1, df_first, total_reply)

#levels 






'''g_replied contains all the nodes that have at least one reply, 
the only edges are between the ones that replied to musk's tweet (42837, 16980)'''
g_replied = g.vs.select( reply_count_ne = 0 ).subgraph()


g_replied1 = g_replied.vs.select( reply_count_ne = 1 ).subgraph() # more than 1 reply



''' g_ego contains all the nodes that are connected to musk (5164 5163)''',
g_replied['degree'] = g_replied.degree()
g_ego = g_replied.vs.select( degree_ne = 0 ).subgraph()

# %%
#plot graph 
fig, ax = plt.subplots(figsize=(100,100))
ig.plot(g_replied1, 
    target = ax,
    vertex_size=0.5, 
    vertex_color='blue', 
    edge_color='grey', 
    layout='fr')

# %%

# ffilter nodes based on an attribute
# get type of the attribute
# https://igraph.org/python/doc/api/igraph.VertexSeq-class.html 
g.vs['degree'] = g.degree()

# get longest path

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

# %%
#remove attribute from graph
g_replied1.vs['text'] = ''
# %%

#write gml file
# %%
#del g_replied1.vs['id']
g_replied1.write_gml('resign_tweet.gml', ids="no-such-attribute")

# %%
