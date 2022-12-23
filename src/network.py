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

#%%
# filter df to get only the tweets that replied to musk's tweet and have some replies 
df_first = df[df['replied_to'] == musk_resig]
df_first = df_first[df_first['reply_count'] > 0]

# extract from df only rows that have replied to the previous ones, in particolar people that replies to a reply 
df_second = df[df['replied_to'].isin(df_first.index)]
edges2 = []

for tweet_id, tweet in df_second.iterrows():
    edges2.append((str(tweet_id), str(tweet['replied_to'])))


df_third = df_second[df_second['reply_count'] > 0]
df_third = df[df['replied_to'].isin(df_second.index)]

df_4 = df_third[df_third['reply_count'] > 0]
df_4 = df[df['replied_to'].isin(df_third.index)]

df_5 = df_4[df_4['reply_count'] > 0]
df_5 = df[df['replied_to'].isin(df_4.index)]

#%%
# recoursive function to explore the tree of replies


df_first = df[df['replied_to'] == musk_resig]
total_reply = 0

def explore_tree(n, df_n, total_reply):

    print('al livello ',n ,df_n.shape[0],'reply')
    total_reply += df_n.shape[0]

    if(df_n.shape[0] > 0):
        
        df_n = df_n[df_n['reply_count'] > 0]
        print('al livello ',n ,df_n.shape[0], 'reply con reply')
        print('biggest thread',df_n.value_counts('reply_count').tail(1).index.tolist()[0])
        df_n = df[df['replied_to'].isin(df_n.index)]
        edges = []
        for tweet_id, tweet in df_n.iterrows():
            edges.append((str(tweet_id), str(tweet['replied_to'])))

        g.add_edges(edges)
    
        return explore_tree(n+1, df_n, total_reply)
    else:
        return total_reply


explore_tree(1, df_first, total_reply)

#levels 




#%%
vs = g.vs['name']


for tweet_id, tweet in df.iterrows():
    if(str(tweet['replied_to'] in vs)): 
        edges.append((str(tweet_id), str(tweet['replied_to'])))

g.add_edges(edges)

#export graph to gml
g.write_gml('resign_tweet.gml')



'''g_replied contains all the nodes that have at least one reply, 
the only edges are between the ones that replied to musk's tweet (42837, 5163)'''
g_replied = g.vs.select( reply_count_ne = 0 ).subgraph()




''' g_ego contains all the nodes that are connected to musk (5164 5163)''',
g_replied['degree'] = g_replied.degree()
g_ego = g_replied.vs.select( degree_ne = 0 ).subgraph()

# %%
#plot graph 
fig, ax = plt.subplots(figsize=(100,100))
ig.plot(g_ego, 
    target = ax,
    vertex_size=0.1, 
    vertex_color='blue', 
    edge_color='grey', 
    layout='circular')

# %%

# ffilter nodes based on an attribute
# get type of the attribute
# https://igraph.org/python/doc/api/igraph.VertexSeq-class.html 
g.vs['degree'] = g.degree()

# get longest path
