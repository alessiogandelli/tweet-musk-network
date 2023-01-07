
i have used search recent tweets but it is not working properly 

i extracted 400k tweets with the field conversation_id =  the one of the poll, at the moment of scraping twitter the comments were 399k 

trying to build a conversation tree i discovered that not all the tweets were in the dataset 


There are 188636 tweets that were directly replying to the poll, but there are 210364 tweets that were replying to a tweet that was replying to the poll. 

in df_first there are the tweet that are replying to the original tweet and that have at least one reply

There are 5163 tweet that were replying to a reply to the first level reply, there are 76457 tweet at the second level let's see how they are distributed 

in df_second there are all the tweets that are replying to a tweet from df_first

of these 5163 we only have data for 4724 

so we have 4724 level 2 replies with 18234 replies 
