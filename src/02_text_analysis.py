#%%
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import nltk
import pandas as pd
import fasttext
from nltk import ngrams
from sklearn.feature_extraction.text import TfidfVectorizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import numpy as np
import pickle
import gsdmm
from gsdmm import MovieGroupProcess
from textblob import TextBlob
import mgp 
from mgp import MovieGroupProcess


path ='/Users/alessiogandelli/dev/uni/tweet-musk-network/data/resign_replies.csv'
path_to_pretrained_model = '/Users/alessiogandelli/dev/uni/tweet-musk-network/data/models/lid.176.bin'
stop_words_path = '/Users/alessiogandelli/dev/uni/tweet-musk-network/src/stopwords.txt'

# model for language detection
fmodel = fasttext.load_model(path_to_pretrained_model)

# workers 
lemmatizer = nltk.WordNetLemmatizer()
analyzer = SentimentIntensityAnalyzer()
vectorizer = TfidfVectorizer()

#load stop words 
with open(stop_words_path, 'r') as f:
    stop_words = eval(f.read())

# make a word cloud 
def make_wordcloud(text, filename, freq=False):
    wordcloud = WordCloud(width = 800, height = 800,
                    background_color ='white',
                    min_font_size = 10)

    if freq:
        wordcloud.generate_from_frequencies(text)
    else:
        wordcloud.generate(text)

    # plot the WordCloud image
    plt.figure(figsize = (8, 8), facecolor = None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad = 0)

    return plt.savefig('/Users/alessiogandelli/dev/uni/tweet-musk-network/imgs/'+filename, dpi=300)


#%%

df = pd.read_csv(path, index_col=0)


'''###################################### PREPROCESSING ######################################'''
# extract hastags and put in a new field and remove them from the text
# hastags and mentions x 
# urls and punctuation
# to lower case
# remove stop words
# tokenize


'''CLEANING'''
# extract hastags and mentions and urls thia can be useful later 
df = df.assign(urls = df['text'].str.findall(r"http\S+"))
df = df.assign(mentions = df['text'].str.findall(r"@(\w+)"))
df = df.assign(hashtags = df['text'].str.findall(r"#(\w+)"))

# replace and removal 
df['text'] = df['text'].str.replace(r"#(\w+)", "", regex=True)          # hastags
df['text'] = df['text'].str.replace(r"@(\w+)", "", regex=True)          # mentions 
df['text'] = df['text'].str.replace(r"http\S+", "", regex=True)         # urls
df['text'] = df['text'].str.replace(r"[^\w\s]", "", regex=True)         # punctuation
df['text'] = df['text'].str.lower()                                     # to lower case
df['text'] = df['text'].str.replace(r"\n", "", regex=True)              # new line 
df['text'] = df['text'].str.replace(r"(no+)+", "no", regex=True)        # replace multiple no with no
df['text'] = df['text'].str.replace(r"dont", "do not", regex=True)      # replace dont with do not
df['text'] = df['text'].str.replace(r"cant", "can not", regex=True)     # replace cant with can not
df['text'] = df['text'].str.replace(r"didnt", "did not", regex=True)    # replace didnt with did not
df['text'] = df['text'].str.replace(r"doesnt", "does not", regex=True)  # replace doesnt with does not


df = df[df['text'].str.contains(r"[a-z]", regex=True)]      # remove lines with no characters a-z
df['text'] = df['text'].str.strip()                         # trim all the text



# get the max of positive neutral and negative and and label the tweet 
'''TOKENIZATION AND LEMMATIZATION'''
# remove stop words
df['tokens'] = df['text'].apply(lambda x: ' '.join([word for word in x.split() if word not in (stop_words)]))
# tokenize and #lemmatize
df['tokens'] = df['tokens'].apply(lambda x: nltk.word_tokenize(x))
df['tokens'] = df['tokens'].apply(lambda x: [lemmatizer.lemmatize(word) for word in x])

# create bigrams 
df['bigrams'] = df['tokens'].apply(lambda x: list(ngrams(x, 2)))
df['bigrams'] = df['bigrams'].apply(lambda x: ['_'.join(i) for i in x])







'''###################################### ANALYSIS ######################################'''


'''PREDICT LANGUAGE'''

df['lang'] = df['text'].apply(lambda x: fmodel.predict(x)[0][0].replace('__label__', ''))

# clean errors
df.loc[(df['text'].str.contains(r"no",      regex=True)) & (df['lang'] == 'pt'), 'lang'] = 'en' # word no in portuguese
df.loc[(df['text'].str.contains(r"do it",   regex=True)) & (df['lang'] == 'pt'), 'lang'] = 'en' # do it 
df.loc[(df['text'].str.contains(r"dont",    regex=True)) & (df['lang'] == 'fr'), 'lang'] = 'en' # dont in frencht
df.loc[(df['text'].str.contains(r"bro",     regex=True)) & (df['lang'] == 'pt'), 'lang'] = 'en' # bro in portuguese
df.loc[(df['text'].str.contains(r"hell no", regex=True)) & (df['lang'] == 'es'), 'lang'] = 'en' # hell no in spanish

# take only english 
df = df[df['lang'] == 'en']







# save to csv



#%%


# we can see two spikes at -0.2960 and 0.4019 which corresponds respectively to the words no and yes


#%%
'''WORDCLOUDS'''

# vectorization for TF-IDF
vectors = vectorizer.fit_transform(df['tokens'].apply(lambda x: ' '.join(x))).sum(axis=0)
vocab = vectorizer.vocabulary_

text = ' '.join(df['tokens'].apply(lambda x: ' '.join(x)))
bigrams_list = [item for sublist in df['bigrams'].tolist() for item in sublist]
bigrams = pd.Series(bigrams_list).value_counts().to_dict()
word_tfidf = {word: vectors[0, idx] for word, idx in vocab.items()}# compute tdidf and sum the vectors

make_wordcloud(text, 'text_wordcloud.png')
make_wordcloud(bigrams, 'bigrams_wordcloud.png', freq=True)
make_wordcloud(word_tfidf, 'tf_idf_wordcloud.png', freq=True)

#%%

'''SENTIMENT ANALYSIS'''
# import textblob

df['sentiment_vader'] = df['text'].apply(lambda x: analyzer.polarity_scores(x)['compound'])

df['sentiment_vader'].hist(bins=50)

no = -0.2960
yes = 0.4019

df['sentiment'] = df['sentiment_vader'].apply(lambda x: 'positive' if x >= yes else ('negative' if x <= no else 'neutral'))
# add annotation at 0.4019, 200000
plt.text(0.38, 22000, 'yes')
plt.text(-0.32, 55000, 'no')
plt.title('Sentiment Analysis - VADER')
plt.xlabel('Sentiment Score')
plt.ylabel('Number of Tweets')
plt.savefig('sentiment_hist.png', dpi=300)

#%%
#bigrams list but only of the one with sentiment > 0 
pos_list = [item for sublist in df[df['sentiment_vader'] >= yes]['tokens'].tolist() for item in sublist]
neg_list = [item for sublist in df[df['sentiment_vader'] <= no]['tokens'].tolist() for item in sublist]
neu_list = [item for sublist in df[(df['sentiment_vader'] > no) & (df['sentiment_vader'] < yes)]['tokens'].tolist() for item in sublist]

pos_dict = pd.Series(pos_list).value_counts().to_dict()
neg_dict = pd.Series(neg_list).value_counts().to_dict()
neu_dict = pd.Series(neu_list).value_counts().to_dict()

pos_dict.pop('not')
neg_dict.pop('not')

make_wordcloud(pos_dict, 'text_pos_wordcloud.png', freq=True)
make_wordcloud(neg_dict, 'text_neg_wordcloud.png', freq=True)
make_wordcloud(neu_dict, 'text_neu_wordcloud.png', freq=True)




# twitter shaped wordcloud



# %%
'''TOPIC MODELLING'''



#%%
# merge all df['text'] into a single list of lists 
docs = df['tokens'].tolist()

# remove no from docs
docs = [[word for word in doc if word != 'no'] for doc in docs]
docs = [[word for word in doc if word != 'not'] for doc in docs]
docs = [[word for word in doc if word != 'twitter'] for doc in docs]
# %%
mgp = MovieGroupProcess(K=4, alpha=0.1, beta=0.1, n_iters=30)
vocab = set(x for doc in docs for x in doc)
n_terms = len(vocab)
y = mgp.fit(docs, n_terms)

#%%
# save model
with open('4clustersnonotw.model', 'wb') as f:
    pickle.dump(mgp, f)
    f.close()

#%%
# load model
with open('/Users/alessiogandelli/dev/uni/tweet-musk-network/data/models/10clusters.model', 'rb') as f:
    mgp10 = pickle.load(f)
    f.close()

# dict with docs and y 
# add y to dataframe 
df['topic_clean'] = y

# max rows
pd.set_option('display.max_rows', 1000)
# %%

# helper functions
def top_words(cluster_word_distribution, top_cluster, values):
    '''prints the top words in each cluster'''
    for cluster in top_cluster:
        sort_dicts =sorted(mgp.cluster_word_distribution[cluster].items(), key=lambda k: k[1], reverse=True)[:values]
        print('Cluster %s : %s'%(cluster,sort_dicts))
        print(' ??? ??? ??? ??? ??? ??? ??? ??? ???')

def cluster_importance(mgp):
    '''returns a word-topic matrix[phi] where each value represents
    the word importance for that particular cluster;
    phi[i][w] would be the importance of word w in topic i.
    '''
    n_z_w = mgp.cluster_word_distribution
    beta, V, K = mgp.beta, mgp.vocab_size, mgp.K
    phi = [{} for i in range(K)]
    for z in range(K):
        for w in n_z_w[z]:
            phi[z][w] = (n_z_w[z][w]+beta)/(sum(n_z_w[z].values())+V*beta)
    return phi

def topic_allocation(df, docs, mgp, topic_dict):
    '''allocates all topics to each document in original dataframe,
    adding two columns for cluster number and cluster description'''
    topic_allocations = []
    for doc in tqdm(docs):
        topic_label, score = mgp.choose_best_label(doc)
        topic_allocations.append(topic_label)

    df['cluster'] = topic_allocations

    df['topic_name'] = df.cluster.apply(lambda x: get_topic_name(x, topic_dict))
    print('Complete. Number of documents with topic allocated: {}'.format(len(df)))

def get_topic_name(doc, topic_dict):
    '''returns the topic name string value from a dictionary of topics'''
    topic_desc = topic_dict[doc]
    return topic_desc


#%%

doc_count = np.array(mgp.cluster_doc_count)
print('Number of documents per topic :', doc_count)
print('*'*20)# topics sorted by the number of documents they are allocated to
top_index = doc_count.argsort()[-10:][::-1]
print('Most important clusters (by number of docs inside):',   
       top_index)
print('*'*20)# show the top 5 words in term frequency for each cluster 
topic_indices = np.arange(start=0, stop=len(doc_count), step=1)
top_words(mgp.cluster_word_distribution, topic_indices, 10)
# %%

# get correlation between topic and sentiment

#get tweets that contains tom in text 
df_tom = df[df['text'].str.contains('tom')]

# %%
contingency_table = pd.crosstab(df['topic'], df['sentiment'])

from scipy.stats import chi2_contingency

# Calculate the chi-squared statistic and p-value
p= chi2_contingency(contingency_table)

# Print the p-value
print(p)
# %%
from scipy.stats import ttest_ind, f_oneway

# For the t-test, you need to split the data into groups based on the topic
pos = df[df['topic_clean'] == 1]['sentiment']
neg = df[df['topic_clean'] == 3]['sentiment']


# Use the t-test to test for a difference in means between the two groups
t, p = ttest_ind(pos, neg)

# For ANOVA, you can use the f_oneway function from scipy.stats
f, p = f_oneway(pos, neg)