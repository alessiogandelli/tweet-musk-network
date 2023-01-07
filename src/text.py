#%%
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import nltk
import pandas as pd
import fasttext
from nltk import ngrams
from sklearn.feature_extraction.text import TfidfVectorizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

path ='/Users/alessiogandelli/dev/uni/tweet-musk-network/data/resign_replies.csv'
path_to_pretrained_model = '/Users/alessiogandelli/dev/uni/tweet-musk-network/data/lid.176.bin'
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

'''SENTIMENT ANALYSIS'''
df['sentiment_vader'] = df['text'].apply(lambda x: analyzer.polarity_scores(' '.join(x))['compound'])




'''TOKENIZATION AND LEMMATIZATION'''
# remove stop words
df['text'] = df['text'].apply(lambda x: ' '.join([word for word in x.split() if word not in (stop_words)]))
# tokenize and #lemmatize
df['text'] = df['text'].apply(lambda x: nltk.word_tokenize(x))
df['text'] = df['text'].apply(lambda x: [lemmatizer.lemmatize(word) for word in x])

# create bigrams 
df['bigrams'] = df['text'].apply(lambda x: list(ngrams(x, 2)))
df['bigrams'] = df['bigrams'].apply(lambda x: ['_'.join(i) for i in x])

# save to csv

vectors = vectorizer.fit_transform(df['text'].apply(lambda x: ' '.join(x))).sum(axis=0)
vocab = vectorizer.vocabulary_
#%%
'''WORDCLOUDS'''

text = ' '.join(df['text'].apply(lambda x: ' '.join(x)))
bigrams = ' '.join(df['bigrams'].apply(lambda x: ' '.join(x)))
word_tfidf = {word: vectors[0, idx] for word, idx in vocab.items()}# compute tdidf and sum the vectors

make_wordcloud(text, 'text_wordcloud.png')
make_wordcloud(bigrams, 'bigrams_wordcloud.png')
make_wordcloud(word_tfidf, 'tf_idf_wordcloud.png', freq=True)


'''TOPIC MODELLING'''






# %%
