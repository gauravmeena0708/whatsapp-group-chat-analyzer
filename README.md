# Whatsapp Tools

## install

```bash
pip install -e git+https://github.com/gauravmeena0708/whatsapp-tools#egg=whatsapp-tools
```

### Example Use

```python

from whatsapptools import GroupAnalyzer
analyzer = GroupAnalyzer("data/WhatsApp_Chat3.txt")
df = analyzer.parse_chat_data()
df.head()

```

```python

df1 = analyzer.df_basic_cleanup(df)
df1.head()

```

```python

from nltk.corpus import stopwords

custom_stopwords = {"Bhai", "<Media omitted>", "Media omitted", "Media","omitted", "bro", 'would', 'ye', 'ke', 'ko', 'doge', 'aap', 'tum', 'hai'
                    }
stop_words1 = set(stopwords.words('english'))
stop_words2 = set(stopwords.words('english')).union(custom_stopwords)
analyzer.generate_wordcloud(df["message"].str.cat(sep=" "), stop_words1)
analyzer.generate_wordcloud(df["message"].str.cat(sep=" "), stop_words2)

```

```python

analyzer.create_plotly_fig(df,'name','message','message')
analyzer.create_plotly_fig(df,'ym','message','ym',True)
#create_plotly_fig(df,'dt','message','dt',True)
analyzer.create_plotly_fig(df,'day','message','day',False)
analyzer.create_plotly_fig(df,'yd','message','yd',True)
analyzer.create_plotly_fig(df,'name','emojicount','emojicount',True,False)
analyzer.create_plotly_fig(df,'name','urlcount','urlcount',True,False)


#to get emojicount visualization
fig1 = analyzer.create_plotly_fig(df1,'name','emojicount','emojicount')
fig1.show()

#to get urlcount visualization
fig1 = analyzer.create_plotly_fig(df1,'name','urlcount','urlcount')
fig1.show()

#to get yturlcount visualization
fig1 = analyzer.create_plotly_fig(df1,'name','yturlcount','yturlcount')
fig1.show()

#to get mediacount visualization
fig1 = analyzer.create_plotly_fig(df1,'name','mediacount','mediacount',count=False)
fig1.show()

#to get editcount visualization
fig1 = analyzer.create_plotly_fig(df1,'name','editcount','editcount',count=False)
fig1.show()


#to get deletecount visualization
fig1 = analyzer.create_plotly_fig(df1,'name','deletecount','deletecount',count=False)
fig1.show()
```


## ToDo
    GroupChat Analysis

other task yet to accomplish are : 

    basicStats : It will return some basic stats of group. Such as total users, total messages, total media messages and total link shared.
    wordCloud : It will create a word cloud, through which we can easily understand the most frequent words used in chat.
    mostActiveUsers : It will create a bar chart for the top-10 most active members in the group.
    mostActiveDay : It will create a bar chart to show traffic on whatsapp group at each weekdays.
    topMediaContributor : It will create bar chart to show top-10 media contributers in the group.
    maxWordContributers : It will create bar chart which will show top-10 authors who used max no. of words in their messages.
    maxURLContributers : It will create bar chart to show top-10 url contributers in the group.
    mostActiveTime : It will create bar chart to show the time at which group was highly active.
    mostSuitableHours : It will create a bar chart to show the best time span at which there may be high chances getting responce from other group members.
    wordCloud_in : It will create word cloud of particular individual. You need to just pass user name.
    highlyActiveDates : It will create a bar chart to show highly active top-15 dates.
    timeseriesAnalysis : It will plot user interactive time-series plot on traffic at each day.
    activeMonthsB : It will create a bar chart to show most active months on which group was highly active.
    maxEmojiUsers : This will plot a bar chart to show top-15 users who used max no. of emojis in group.
    trafficPerYear : It will plot a bar chart to show traffic on group per year.
    activeMonthsT : This will create a timeseries plot to show traffic on group per month.
    weekdaysTraffic : It will create heat map to show the weekdays traffic along with time span.
    topEmojis_G : It will return pandas dataframe of top-20 emojis used by users.
    topEmojis_I : It will return top-10 emjois used by individual user.
    saveDatframe : It will save the preprocessed data as csv file.

