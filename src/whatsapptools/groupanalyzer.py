import re, regex, nltk, emoji
from datetime import datetime
import pandas as pd
from nltk.corpus import stopwords
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from calendar import day_name
import numpy as np

"""
from groupanalyzer import GroupAnalyzer
analyzer = GroupAnalyzer("data/WhatsApp_Chat3.txt")
df = analyzer.parse_chat_data()
df.head()
analyzer.generate_wordcloud(df["message"].str.cat(sep=" "), [])
"""
class GroupAnalyzer:
    URL_PATTERN      = r'(https?://\S+)'
    YOUTUBE_PATTERN  = r'(https?://youtu(\.be|be\.com)\S+)'
    def __init__(self, file_path):
        self.file_path = file_path
        self.youtube_pattern = self.YOUTUBE_PATTERN
        self.url_pattern     = self.URL_PATTERN

    def parse_chat_data(self):
        with open(self.file_path, "r", encoding="utf-8") as file:
            chat_lines = file.readlines()

        chat_data = []
        for line in chat_lines:
            match = re.match(r'(\d{2}\/\d{2}\/\d{2}, \d{1,2}:\d{2} [apm]{2}) - (.*?): (.*)', line)
            if match:
                timestamp, sender, message = match.groups()
                date_obj = datetime.strptime(timestamp, '%d/%m/%y, %I:%M %p')
                chat_data.append({"t":date_obj,'name':sender,'message': message})

        return pd.DataFrame(chat_data)


    def chunk_column(self, column_name, max_item_length=2500):
        chunks = []
        current_chunk = ""
        current_item_length = 0

        for value in self.df[column_name]:
            value_str = str(value)
            item_length = len(value_str)

            if current_item_length + item_length > max_item_length:
                chunks.append(current_chunk)
                current_chunk = ""
                current_item_length = 0

            current_chunk += value_str + " "
            current_item_length += item_length

        # Add the last chunk if it's not empty
        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def generate_wordcloud(self, text, stop_words):
        text = re.sub(r"<Media omitted>", "", text)
        text = re.sub(r"https", "", text)

        wordcloud = WordCloud(
            width=1600,
            height=800,
            stopwords=stop_words,
            background_color="black",
            colormap="rainbow",
        ).generate(text)

        plt.figure(figsize=(32, 18))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.show()
        
    def get_emojis(self, text):
        emoji_list = []
        data = regex.findall(r'\X', text)
        for word in data:
            if any(char in emoji.EMOJI_DATA for char in word):
                emoji_list.append(word)
        return emoji_list

    def get_urls(self, text):
        url_list = regex.findall(self.url_pattern, text)
        return url_list

    def get_yturls(self, text):
        url_list = re.findall(self.youtube_pattern, text)
        return url_list
    
    def df_basic_cleanup(self, df):
        df['date_time'] = pd.to_datetime(df['t'], format='%d/%m/%y, %I:%M %p')
        df['date']      = pd.to_datetime(df['date_time']).dt.date
        df['year']      = pd.to_datetime(df['date_time']).dt.year
        df['month']     = pd.to_datetime(df['date_time']).dt.month.astype(str).str.zfill(2)
        df['day']       = pd.to_datetime(df['date_time']).dt.day

        df['dayn']      = pd.to_datetime(df['date_time']).dt.day_name().astype('category')
        df['monthn']    = pd.to_datetime(df['date_time'],format='%d/%m/%y, %I:%M %p').dt.month_name()

        df['doy']       = pd.to_datetime(df['date_time']).dt.day_of_year
        df['dow']       = pd.to_datetime(df['date_time']).dt.day_of_week
        df['woy']       = pd.to_datetime(df['date_time']).dt.isocalendar().week
        df['time']      = pd.to_datetime(df['date_time']).dt.time
        df['hour']      = pd.to_datetime(df['date_time']).dt.hour
        df['min']       = pd.to_datetime(df['date_time']).dt.minute
        df['hm']        = df['hour'] + round(df['min']/60,2)

        df['ym']        = df['year'].astype(str)   +'-'+ df['month'].astype(str)
        df['yw']        = df['year'].astype(str)   +'-'+ df['woy'].astype(str)
        df['yd']        = df['year'].astype(str)   +'-'+ df['doy'].astype(str)
        df['md']        = df['monthn'].astype(str) +'-'+ df['date'].astype(str)

        df['mlen']      = df['message'].str.len()

        df["emoji"]     = df["message"].apply(self.get_emojis)
        df["emojicount"]= df["emoji"].str.len()

        df['urls']      = df["message"].apply(self.get_urls)
        df['urlcount']  = df["urls"].str.len()

        df['yturls']      = df["message"].apply(self.get_yturls)
        df['yturlcount']  = df["yturls"].str.len()
        
        df["mediacount"] = np.where(df["message"] == "<Media omitted>", 1, 0)
        df["editcount"]  = np.where(df["message"].str.contains("<This message was edited>"), 1, 0) 
        df["deletecount"]  = np.where(((df["message"] == "This message was deleted") | (df["message"] == "You deleted this message")),1, 0) 

        df.drop('t', inplace=True, axis=1)
        df = df[[ 'date_time','date','year','month','monthn','day','dayn',
                  'woy', 'doy','dow',
                  'ym','yw','yd','md',
                  'time','hour','min', 'hm',
                  'name',
                  'message','mlen',
                  'emoji','emojicount',
                  'urls','urlcount',
                  'yturls','yturlcount','mediacount','editcount','deletecount'
                ]]
        return df
        """
        from nltk.corpus import stopwords
        from nltk.tokenize import word_tokenize

        def calculate_word_frequency(string):
          stopwords_list = set(stopwords.words("english"))
          tokens = word_tokenize(string.lower())
          filtered_tokens = [token for token in tokens if token not in stopwords_list]
          word_counts = {}
          for token in filtered_tokens:
            if token not in word_counts:
              word_counts[token] = 0
            word_counts[token] += 1
          return word_counts

        # Example usage
        string = "This is a string with stopwords that we want to remove."
        word_counts = calculate_word_frequency(string)

        # Print the word frequencies
        for word, count in word_counts.items():
          print(f"{word}: {count}")


        """