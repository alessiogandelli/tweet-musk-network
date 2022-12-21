
#%% scatter plot elon musk tweets 

fig, ax = plt.subplots(figsize=(20,10))
sns.scatterplot(data=df, x='created_at', y='retweet_count', hue='quote_count', size='reply_count', sizes=(100, 1000), ax=ax)

# add text
for row in df.iterrows():
    if row[1]['retweet_count'] > 153968 and row[1]['text'].startswith('meme') == False or row[1]['reply_count'] > 142168 :
        ax.text(row[1]['created_at'], row[1]['retweet_count']+10000, row[1]['text'], fontsize=15)

# xticks
ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m'))

plt.xticks(rotation=45)
plt.title('Elon Musk Tweets')
plt.xlabel('Date')
plt.ylabel('Retweet Count')
plt.show()



# %%
