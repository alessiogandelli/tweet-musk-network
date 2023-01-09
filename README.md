# tweet-musk-network
First i have scraped all the tweet of elon musk to have an overview of its twitter presence during his hourney as ceo, then i want to focus on one or more discussion on some selected tweets, for example the poll where he ask if he should resign

# extract the data using twitter api with tweepy 
in the file 01_data_collection.py there is the twitter scraping part, the file have been saved into files 


- get api keys from twitter developer platform 
- get elon musk profile id (44196397)
- select a start data (13-10-22) (the acquisition have been actualized on 28th October)

Since there are limits to the api call we can do there are some things we have to do:
- wait_on_rate_limit=True  when creating the client so it waits by itself without the need to run the script every 15 minutes 

- use a paginator to get more than 100 results
the first parameter is the method we want to use, i.e. the data we want to get and the other parameters are the parameters of this function, since we are scraping tweets we have to choose the fields we want to retrieve and the one we do not want  



paginator = tweepy.Paginator(
    client.get_users_tweets,               # The method you want to use
    musk_id,                               # The user id
    exclude=['retweets', 'replies'],       # Exclude retweets and replies
    start_time=start_date,                 # The start date
    max_results=100,                       # How many tweets per page
    tweet_fields=['created_at', 'text', 'author_id', 'conversation_id', 'in_reply_to_user_id', 'context_annotations', 'public_metrics'], # Which tweet fields to return                         
)


## get all tweet of elon musk 

I extracted 411 tweet of elon musk, the first one is from 2022-10-12 and the last one is from 2023-01-03

i have used the method get_users_tweets that allows you to extract all the tweet of a user, and luckily is not limited to the previous week 

then these tweets have been saved in a csv file named musk_timeline 

## get all tweet in reply to the poll of elon musk about resigning as ceo of twitter 

This was not easier as the previous task because there is not a specific api call to get the replies to a tweet, so i have to use the search api call with the constraint that the field conversation_id is equal to the one of the poll.

I extracted 400k tweets and saved in a file named resign_replies.csv



# conversation tree 

The conversation under a tweet can be seen as a tree of replies since there are tweets that reply to the poll but there are also tweets that reply to these replies. Building a tree is useful to have a clear structure of the conversations, we can devide it in layers starting from the poll and going down to the replies to the replies to the replies to the poll.

I use Igraph for performing the analysis because under the hood it uses C so it is more efficent for big graphs. 

To populate the Tree i use a recoursive approach with a  Breadth First Search (BFS) algorithm, this mean that i'm going layer by layer 

Then for the porpuse of the graph i have pruned it removing all the leaves ( the tweets with no replies) to save space and time. 

The graph then have been saved in a file named resign_graph.gml 


## problems 

Since i have used the search api call i did not get all the replies, even if at the moment of the scrape there was 399k replies 

[here](https://stackoverflow.com/questions/72016766/tweepy-only-lets-me-get-100-results-how-do-i-get-more-ive-read-about-paginati) i stated that many developers had consinstency problem in getting elon musk data 

after filling the tree there were 107k tweets without edges, so that weren't replying to any tweet, and this should not happen so it is obvious that there is some data that is missing, i saved the id of these tweets in a csv file named excluded.csv for further investigation 




# text analysis 

## preprocessing
extract mentions and hastaghs and put in a separate column
remove punctuation and url and to lower case

cleaned words ( noooo/nonono -> no, cant -> can not, etc)

- create a custom stopwords list
created starting from the most common words in the dataset and avoiding the negative words 

### language detection 
install fasttext to detectthe language of the tweets, if you have problem with wheel probably the problem is that you have to set env variables
 
```export CPLUS_INCLUDE_PATH=/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Headers```
```export C_INCLUDE_PATH=/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Headers```

fast text is used to detect the language of the tweet in order to obtain a better understanding of the conversation, i used this library that use a pretrained model to classify text because is way faster than using the traditional one 10 seconds for 400k tweets vs 13 sec for 1000 tweets using langdetect

from the 400k tweets i removed hastaghs and mentions url punctuation and all to lower case, then i removed all the lines with no characters a-z  

now the df has 377692 rows of which 312452 are english, 39959 portoguese and  5081 french 

but there is a problem in fact when there is the word dont it is classified as french while no is classfied as portoguese 

many classifies as italian contains nooooo with many o

after cleaning the english tweets are 355892

then changed the cant to can not  et similar 



- removed stopwords 
- tokenization
- lemmatization
- create bigrams 


## wordcloud 
i did a wordcloud both on single words and bigrams 


## tfidf 
i used tfidf to get the most important words in the conversation, i used the english tweets only

and i generated a wordcloud also starting from it 

## sentiment analysis 
to get the sentiment analysis of the tweet i decided to use two different models vader and pattern, i used it before removing the stopwords and lemmatization because it is designed to analyz the sentiment of the tweet as it is including slang and emoticons



## topic modeling
 topic modeling is used blabla and i do not use lda but sttm because it is more efficient for short text
 Therefore, most STTM techniques make the initial assumption that a short text comes from only one topic, reducing the overlapping topics that we see with LDA. This is a good assumption for short texts, but not for long texts.


ibbs Sampling Dirichlet Mixture Model (GSDMM) which is a modified LDA 
 https://dl.acm.org/doi/10.1145/2623330.2623715

 https://arxiv.org/pdf/1904.07695.pdf



 https://pub.towardsai.net/tweet-topic-modeling-part-3-using-short-text-topic-modeling-on-tweets-bc969a827fef


