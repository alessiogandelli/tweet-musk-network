#%%
import tweepy
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import datetime
from time import sleep
import dotenv 
import os

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



musk_tweets = client.get_users_tweets(musk_id, start_time = end_date , exclude=['replies', 'retweets'])


next_token = musk_tweets[3]['next_token']
client.get_users_tweets(musk_id, start_time = end_date , exclude=['replies', 'retweets'], pagination_token=next_token)


musk_df = pd.DataFrame(musk_tweets)



# %%
musk_id = 44196397
start_date = datetime.datetime(2022, 10, 13)

paginator = tweepy.Paginator(
    client.get_users_tweets,               # The method you want to use
    musk_id,                            # Some argument for this method      # Some argument for this method
    exclude=['retweets', 'replies'],       # Some argument for this method
    start_time=start_date,     # Some argument for this method
    max_results=100,                       # How many tweets per page                               # How many pages to retrieve
)

tweets = []
for page in paginator.flatten():
    tweets.append(page)

# %%
