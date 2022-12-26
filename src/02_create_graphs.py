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

def explore_tree(g,n, df_n, total_reply):

    print('al livello ',n ,df_n.shape[0],'reply')
    total_reply += df_n.shape[0]# count total replies 

    if(df_n.shape[0] > 0):
        
        df_n = df_n[df_n['reply_count'] > 0] # filter only the ones that have replies
        print('al livello ',n ,df_n.shape[0], 'reply con reply') 
        print('biggest thread',df_n.value_counts('reply_count').tail(1).index.tolist()[0])
        df_n = df[df['replied_to'].isin(df_n.index)] # take from the main dataset the ones that replied to the ones in df_n
        edges = []

        nodes = []
        #append all edges for this level 
        for tweet_id, tweet in df_n.iterrows():
            # add vertex attribute level 
            nodes.append(str(tweet_id))
        
            edges.append((str(tweet_id), str(tweet['replied_to'])))

        print('nodes',len(nodes))
        g.vs.select(name_in = nodes )['level'] = n
        g.add_edges(edges) # add edges to the graph
    
        return explore_tree(g, n+1, df_n, total_reply)
    else:
        return total_reply



''' returns a tree of replies to a tweet'''
def create_reply_tree(musk_resig):

    g = ig.Graph(directed=True)

    edges = []

    g.add_vertex(str(musk_resig))

    # add all nodes and first level edges to the graph
    for tweet_id, tweet in df.iterrows():
        g.add_vertex(str(tweet_id), **tweet.to_dict())

        if tweet['replied_to'] == musk_resig:             # if the tweet is a reply to musk's tweet
            edges.append((str(tweet_id), str(musk_resig)))

    g.add_edges(edges)


    # recursively explore the tree and fill the graph
    df_first = df[df['replied_to'] == musk_resig] # filter the ones that replied to musk's tweet
    total_reply = 0
    explore_tree(g, 1, df_first, total_reply)

    # remove nodes with no edges that are missing, further investigation later 
    g.vs['degree'] = g.degree()
    excluded = g.vs.select(degree = 0)
    excluded['name'].to_csv('excluded.csv')
    g.delete_vertices(excluded)

    # fix levels 
    g.vs['levels'] = [1 if l == None else l+1 for l in g.vs['levels']]
    g.vs.select(0)['levels'] = 0

    # save the graph 
    del g.vs['id']
    g.write_gml('resign_complete.gml', ids="no-such-attribute")
    
    return g



'''returns the tree without leaves (42837, 16980)'''
def prune_tree(g):
    g_replied = g.vs.select( reply_count_ne = 0 ).subgraph()
    g_replied.write_gml('resign_nozero.gml', ids="no-such-attribute")

    g_replied.vs['indegree'] = g_replied.indegree()

    #del g_replied.vs['id'] # if you have problems 
    g_replied.write_gml('resign_tweet.gml', ids="no-such-attribute")

    return g_replied


def plot_graph(g):
    fig, ax = plt.subplots(figsize=(100,100))
    ig.plot(g_replied, 
        target = ax,
        vertex_size= [r/100 for r in g_replied.vs['indegree']],
        #vertex_label = [r[:5] for r in g_replied.vs['text']],
        vertex_color='lightblue', 
        edge_color='grey', 
        edge_length=50,
        layout='reingold_tilford')



# %%

g = create_reply_tree(musk_resig)
#prune leaves
g_replied = prune_tree(g)
# %%
