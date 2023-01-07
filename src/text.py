#%%
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import nltk
import pandas as pd
import fasttext
from nltk import ngrams

path ='/Users/alessiogandelli/dev/uni/tweet-musk-network/data/resign_replies.csv'
path_to_pretrained_model = '/Users/alessiogandelli/dev/uni/tweet-musk-network/data/lid.176.bin'
stop_words_path = '/Users/alessiogandelli/dev/uni/tweet-musk-network/src/stopwords.txt'

# model for language detection
fmodel = fasttext.load_model(path_to_pretrained_model)

lemmatizer = nltk.WordNetLemmatizer()

#load stop words 
with open(stop_words_path, 'r') as f:
    stop_words = eval(f.read())


def make_wordcloud(txt):
    # word cloud
    wordcloud = WordCloud(  width = 800, height = 800,
                            background_color ='white',  
                            min_font_size = 10)

    wordcloud.generate(' '.join(txt.apply(lambda x: ' '.join(x))))
    # plot the WordCloud image
    plt.figure(figsize = (8, 8), facecolor = None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad = 0)
    plt.show()
#%%
df = pd.read_csv(path, index_col=0)


'''PREPROCESSING'''
# extract hastags and put in a new field and remove them from the text
# hastags and mentions x 
# urls and punctuation
# to lower case
# remove stop words
# tokenize

df = df.assign(urls = df['text'].str.findall(r"http\S+"))
df = df.assign(mentions = df['text'].str.findall(r"@(\w+)"))
df = df.assign(hashtags = df['text'].str.findall(r"#(\w+)"))

# remove hastags and mentions and urls and punctuation and to lower case
df['text'] = df['text'].str.replace(r"#(\w+)", "", regex=True) # hastags
df['text'] = df['text'].str.replace(r"@(\w+)", "", regex=True) # mentions 
df['text'] = df['text'].str.replace(r"http\S+", "", regex=True)# urls
df['text'] = df['text'].str.replace(r"[^\w\s]", "", regex=True)# punctuation
df['text'] = df['text'].str.lower() # to lower case
df['text'] = df['text'].str.replace(r"\n", "", regex=True) # new line
df['text'] = df['text'].str.replace(r"no+", "no", regex=True) #replace nooooo with no 
df['text'] = df['text'].str.replace(r"(no)+", "no", regex=True)# replace multiple nonono with no

# replace dont with do not
df['text'] = df['text'].str.replace(r"dont", "do not", regex=True)
df['text'] = df['text'].str.replace(r"cant", "can not", regex=True)
df['text'] = df['text'].str.replace(r"didnt", "did not", regex=True)
df['text'] = df['text'].str.replace(r"doesnt", "does not", regex=True)



df = df[df['text'].str.contains(r"[a-z]", regex=True)]#remove lines with no characters a-z
df['text'] = df['text'].str.strip()# trim all the text

# predict language
df['lang'] = df['text'].apply(lambda x: fmodel.predict(x)[0][0].replace('__label__', ''))


df.loc[(df['text'].str.contains(r"no", regex=True)) & (df['lang'] == 'pt'), 'lang'] = 'en'#  word no in portuguese
df.loc[(df['text'].str.contains(r"do it", regex=True)) & (df['lang'] == 'pt'), 'lang'] = 'en' # do it 
df.loc[(df['text'].str.contains(r"dont", regex=True)) & (df['lang'] == 'fr'), 'lang'] = 'en' # dont in frencht
df.loc[(df['text'].str.contains(r"bro", regex=True)) & (df['lang'] == 'pt'), 'lang'] = 'en' # bro in portuguese
df.loc[(df['text'].str.contains(r"hell no", regex=True)) & (df['lang'] == 'es'), 'lang'] = 'en' # hell no in spanish

# take only english 
df = df[df['lang'] == 'en']

# %%
# remove stop words
df['text'] = df['text'].apply(lambda x: ' '.join([word for word in x.split() if word not in (stop_words)]))
# tokenize
df['text'] = df['text'].apply(lambda x: nltk.word_tokenize(x))
#lemmatize
df['text'] = df['text'].apply(lambda x: [lemmatizer.lemmatize(word) for word in x])



df['bigrams'] = df['text'].apply(lambda x: list(ngrams(x, 2)))
df['bigrams'] = df['bigrams'].apply(lambda x: ['_'.join(i) for i in x])



#%%
# word cloud
make_wordcloud(txt=df['text'])
make_wordcloud(txt=df['bigrams'])




#%%



# tf-idf
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(df['text'].apply(lambda x: ' '.join(x)))
# %%
# count vectorizer
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(df['text'].apply(lambda x: ' '.join(x)))
# %%
# tf-idf transformer
transformer = TfidfTransformer()
X = transformer.fit_transform(X)

