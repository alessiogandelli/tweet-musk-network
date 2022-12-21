#%%
import torch
import transformers
from transformers import pipeline


# %%
sentiment_analysis = pipeline("sentiment-analysis")

#%%
pos_text = "today it is raining "
neg_text = "I do not hate chocolate"

result = sentiment_analysis(pos_text)[0]
print("Label:", result['label'])
print("Confidence Score:", result['score'])
print()
result = sentiment_analysis(neg_text)[0]
print("Label:", result['label'])
print("Confidence Score:", result['score'])
# %%

summaries = pipeline("summarization")
summaries(tweets[0], max_length=100, min_length=30, do_sample=False)
# %%
