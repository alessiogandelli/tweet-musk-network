#%%

''' scrape twitter data of elon musk and save it to a csv file'''
import tweepy
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import datetime
from time import sleep
import dotenv 
import os
import igraph as ig
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker


#%%
'''SETUP'''

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
client = tweepy.Client(bearer_token=bearer, wait_on_rate_limit=True)

link = 'https://www.searchenginejournal.com/elon-musks-twitter-takeover-a-timeline-of-events/470927/#close'


# %%
'''GET TWEETS of elon musk'''
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



# generate graph  and dataframe
df = pd.DataFrame()
data = {}
g = ig.Graph(directed=True)

# loop over all the tweets
for page in paginator.flatten():

    args = {'created_at': page['created_at'], 
            'text': page['text'],
            'id': page['id'],
            'author_id': page['author_id'],
            'conversation_id': page['conversation_id'],
            'in_reply_to_user_id': page['in_reply_to_user_id'],
            'context_annotations': page['context_annotations'],
            'retweet_count': page['public_metrics']['retweet_count'],
            'reply_count': page['public_metrics']['reply_count'],
            'like_count': page['public_metrics']['like_count'],
            'quote_count': page['public_metrics']['quote_count'],
            }
    
    #store args in dict
    data[page['id']] = args

    # add vertice with attributes 
    g.add_vertex(page.data['id'] ,**args)



# data to dataframe 
df = pd.DataFrame(data).T
df['created_at'] = df['created_at'].apply(lambda x: x - timedelta(hours=7))
df['text'] = df['text'].apply(lambda x: 'meme' if x.startswith('https') else x)






# %% build conversation for elin musk resign 
'''GET all REPLIES to elon musk resign poll'''

conv = 1604617643973124097
start_date = datetime.datetime(2022, 12, 19)


paginator = tweepy.Paginator(
    client.search_recent_tweets,              # The method you want to use
    query='conversation_id:' + str(conv), # The user id,
    max_results=100,                       # How many tweets per page
    tweet_fields=['created_at', 'text', 'author_id', 'conversation_id', 'in_reply_to_user_id','referenced_tweets', 'public_metrics'], # Which tweet fields to return                         
)


df_resign = pd.DataFrame()

data = {}
i = 0

time = datetime.datetime.now()

for page in paginator.flatten():
    i += 1

    if i % 10000 == 0:
        print(i, datetime.datetime.now() - time )
    args = {'created_at': page['created_at'], 
            'text': page['text'],
            'id': page['id'],
            'author_id': page['author_id'],
            'conversation_id': page['conversation_id'],
            'replied_to': page['referenced_tweets'][0]['id'],
            'in_reply_to_user_id': page['in_reply_to_user_id'],
            'retweet_count': page['public_metrics']['retweet_count'],
            'reply_count': page['public_metrics']['reply_count'],
            'like_count': page['public_metrics']['like_count'],
            'quote_count': page['public_metrics']['quote_count'],
           
            }
    
    #get retweet count
    data[page['id']] = args

    
    if i%400000 == 0:
        break # only get 400k tweets



    # add vertice with attributes 
   # g.add_vertex(page.data['id'] ,**args)

df_resign = pd.DataFrame(data).T
df_resign['created_at'] = df_resign['created_at'].apply(lambda x: x - timedelta(hours=7))
df_resign['text'] = df_resign['text'].apply(lambda x: 'meme' if x.startswith('https') else x)

df_resign.to_csv('resign_tweet.csv')


# %%
