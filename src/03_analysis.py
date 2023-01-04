#%%
import os
import igraph as ig
import seaborn as sns
import re
import nltk



graph_path = '/Users/alessiogandelli/dev/uni/tweet-musk-network/data/resign_complete.gml'

g = ig.Graph.Read_GML(graph_path)

stop_words = set(nltk.corpus.stopwords.words("english"))

stemmer = nltk.PorterStemmer()
lemmatizer = nltk.WordNetLemmatizer()

# %%
hashtags = [word for sentence in g.vs['text'] for word in sentence.split() if word.startswith("#")]
sentence = " ".join([word for sentence in g.vs['text'] for word in sentence.split() if not word.startswith("#")])

#extracting mentions and remove them from the sentence
mentions = [word for sentence in g.vs['text'] for word in sentence.split() if word.startswith("@")]
sentence = " ".join([word for sentence in g.vs['text'] for word in sentence.split() if not word.startswith("@")])






# %%
tokens = nltk.word_tokenize(sentence)
filtered  = [t for t in tokens if t.casefold() not in stop_words]

# %%
#word cloud 
from wordcloud import WordCloud
import matplotlib.pyplot as plt

wordcloud = WordCloud(width = 800, height = 800,
                background_color ='white',
                stopwords = stop_words,
                min_font_size = 10).generate(sentence)

# plot the WordCloud image
plt.figure(figsize = (8, 8), facecolor = None)
plt.imshow(wordcloud)

# %%

# select only level one nodes
g1 = g.vs.select(levels = 1).subgraph()
# %%
hashtags = [word for sentence in g1.vs['text'] for word in sentence.split() if word.startswith("#")]
sentence = " ".join([word for sentence in g1.vs['text'] for word in sentence.split() if not word.startswith("#")])

#extracting mentions and remove them from the sentence
mentions = [word for sentence in g1.vs['text'] for word in sentence.split() if word.startswith("@")]
sentence = " ".join([word for sentence in g1.vs['text'] for word in sentence.split() if not word.startswith("@")])

# %%
