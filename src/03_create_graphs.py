#%%
import os
import igraph as ig
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import pandas as pd
import re
import pickle
import datetime



# 

# read csv first column as index 
#df = pd.read_csv('/Users/alessiogandelli/dev/uni/tweet-musk-network/data/resign_tweet.csv', index_col=0)




musk_id = 44196397
musk_resig = 1604617643973124097

#%%
# read dataframe with text mined and add missing nodes
with open('df', 'rb') as f:
    df = pickle.load(f)

replied = set(df['replied_to'].tolist())
ids = set(df.index.tolist())

missing = list(replied - ids)
# create rows in df  with nan in all columns except id and replied_to musk_resig
df_missing = pd.DataFrame(index=missing, columns=df.columns)
df_missing['replied_to'] = musk_resig
df_missing['id'] = missing
# set created at to 2020 to be able to sort
df_missing['created_at'] = '2020-12-22 09:36:56+00:00'

df = pd.concat([df, df_missing])
df = df.sort_values('created_at')



# find ones in replied that are not in the index




# %%

def explore_tree(g,n, df_n, total_reply):

    print('al livello ',n ,df_n.shape[0],'reply')
    total_reply += df_n.shape[0]# count total replies 

    if(df_n.shape[0] > 0):
        
        df_n = df_n[df_n['reply_count'] > 0] # filter only the ones that have replies
        print('al livello ',n ,df_n.shape[0], 'reply con reply') 
        # print('biggest thread',df_n.value_counts('reply_count').tail(1).index.tolist()[0])
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
        return g



''' returns a tree of replies to a tweet'''
def create_reply_tree(musk_resig):
    edges = []

    g = ig.Graph(directed=True)
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
    g = explore_tree(g, 1, df_first, total_reply)

    # remove nodes with no edges that are missing, further investigation later 
    # g.vs['degree'] = g.degree()
    # excluded = g.vs.select(degree = 0)
    # #excluded['name'].to_csv('excluded.csv')
    # g.delete_vertices(excluded)

    # fix levels 
    # g.vs['levels'] = [1 if l == None else l+1 for l in g.vs['levels']]
    # g.vs.select(0)['levels'] = 0

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
    g_replied.write_gml('resign_replies.gml', ids="no-such-attribute")

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
g.vs['indegree'] = g.indegree()
g.vs['outdegree'] = g.outdegree()
g.vs['betweenness'] = g.betweenness()
g.vs['closeness'] = g.closeness()
g.vs['eigenvector'] = g.eigenvector_centrality()

# %%
g.vs['level'] = [1 if l == None else l+1 for l in g.vs['level']]
g.vs.select(0)['level'] = 0

# mean outdegree per level
g.vs['outdegree'].groupby(g.vs['level']).mean()

#%%

# from g to dataframe
df_g = pd.DataFrame(g.vs['name'], columns=['id'])
df_g = df_g.set_index('id')
df_g['indegree'] = g.vs['indegree']
df_g['outdegree'] = g.vs['outdegree']
df_g['betweenness'] = g.vs['betweenness']
df_g['closeness'] = g.vs['closeness']
df_g['eigenvector'] = g.vs['eigenvector']
df_g['level'] = g.vs['level']
df_g['reply_count'] = g.vs['reply_count']
df_g['retweet_count'] = g.vs['retweet_count']
df_g['like_count'] = g.vs['like_count']
df_g['text'] = g.vs['text']
df_g['topic'] = g.vs['topic']
df_g['sentiment'] = g.vs['sentiment']
df_g['sentiment_vader'] = g.vs['sentiment_vader']
df_g['replied_to'] = g.vs['replied_to']




#%%
# get the tweets replint to 1605372724800393216
# plot g but only the ones eith indegree > 100
mini = g.vs.select( indegree_gt = 100 ).subgraph()
# make it undirected
mini.to_undirected()


# use layout_reingold_tilford_circular layout for a circular graph
fig, ax = plt.subplots(figsize=(100,100))
ig.plot(mini.to_undirected(),
    target = ax,
    vertex_size= 1,
    #vertex_label = [r[:5] for r in g_replied.vs['text']],
    vertex_color='lightblue',
    edge_color='grey',
    layout='reingold_tilford_circular')

                    



# %%
save_graph(g, 'resign_complete_plus.gml')