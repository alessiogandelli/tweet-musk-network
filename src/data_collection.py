#%%
import tweepy
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import datetime
from time import sleep
import dotenv 
import os
import igraph as ig
#%%

dotenv.load_dotenv()

consumer_key = os.environ['API_key'] #Your API/Consumer key 
consumer_secret = os.environ['API_key_secret'] #Your API/Consumer Secret Key
access_token = os.environ['access_token']   #Your Access token key
access_token_secret = os.environ['access_token_secret'] #Your Access token Secret key
bearer =  os.environ['bearer']


#Pass in our twitter API authentication key
auth = tweepy.OAuth1UserHandler(
    consumer_key, consumer_secret,
    access_token, access_token_secret
)

#Instantiate the tweepy API
api = tweepy.API(auth, wait_on_rate_limit=True)
client = tweepy.Client(bearer_token=bearer)
# %%



# parameters of the search
musk_id = 44196397
start_date = datetime.datetime(2022, 10, 13)

# paginator is used to get all the tweets using different calls since the API only returns 100 tweets at a time
paginator = tweepy.Paginator(
    client.get_users_tweets,               # The method you want to use
    musk_id,                               # The user id
    exclude=['retweets', 'replies'],       # Exclude retweets and replies
    start_time=start_date,                 # The start date
    max_results=100,                       # How many tweets per page
    tweet_fields=['created_at', 'text', 'author_id', 'conversation_id', 'in_reply_to_user_id', 'context_annotations', 'public_metrics'], # Which tweet fields to return                         
)




# %%

# generate graph 
df = pd.DataFrame()

g = ig.Graph(directed=True)
for page in paginator.flatten():
    args = {'created_at': page['created_at'], 
            'text': page['text'],
            'author_id': page['author_id'],
            'conversation_id': page['conversation_id'],
            'in_reply_to_user_id': page['in_reply_to_user_id'],
            'context_annotations': page['context_annotations'],
            'retweet_count': page['public_metrics']['retweet_count'],
            'reply_count': page['public_metrics']['reply_count'],
            'like_count': page['public_metrics']['like_count'],
            'quote_count': page['public_metrics']['quote_count'],
            }
    pd.concat(df, args)
    #get retweet count


    # add vertice with attributes 
    g.add_vertex(page.data['id'] ,**args)

#%%
#plot graph
fig, ax = plt.subplots(figsize=(40,10))
ig.plot(
    g28,
    target=ax,
    layout="tree", # print nodes in a circular layout
    vertex_size=[v['retweet_count'] /50000 for v in g.vs], # size of nodes proportional to retweet count
    vertex_label=[v['created_at'] if v['retweet_count'] > 253968 else '' for v in g.vs], # label nodes with tweet text
    vertex_label_size=20,
)

18-11-2022

28-10-2022

#%%
#fget nodes of 28 october 
nodes = [v for v in g.vs if v['created_at'].date() == datetime.date(2022, 10, 28)]

g28 = g.subgraph(nodes)


# %%
