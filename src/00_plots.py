
#%% scatter plot elon musk tweets 

# import data
#df = pd.read_csv('musk_timeline.csv', index_col=0)

fig, ax = plt.subplots(figsize=(15,8))
sns.scatterplot(data=df, x='created_at', y='retweet_count', hue='quote_count', size='reply_count', sizes=(100, 1000), ax=ax)

# add text
for row in df.iterrows():
    if row[1]['retweet_count'] > 153968 and row[1]['text'].startswith('meme') == False or row[1]['reply_count'] > 142168 :
        text = row[1]['text']
        # if wordcount > 8 add new line
        text = text.split()
        text = [t for t in text if t.startswith('http') == False]

        if len(text) > 8:
           
            text = text[0:8] + ['\n'] + text[8:]
            # remove urls 
            
        text = ' '.join(text)


        ax.text(row[1]['created_at'], row[1]['retweet_count']+10000, text, fontsize=15)

# xticks
ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m'))

#legend to the left
plt.legend( loc='upper left')


plt.xticks(rotation=45)
plt.title('Elon Musk Tweets')
plt.xlabel('Date')
plt.ylabel('Retweet Count')
plt.savefig('elon_musk_tweets.png', dpi=300)



# %%
