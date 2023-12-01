import re
from datetime import datetime
import pandas as pd
import nltk
from nltk.corpus import stopwords
from wordcloud import WordCloud
import matplotlib.pyplot as plt

"""
from groupanalyzer import GroupAnalyzer
analyzer = GroupAnalyzer("data/WhatsApp_Chat3.txt")
df = analyzer.parse_chat_data()
df.head()
analyzer.generate_wordcloud(df["message"].str.cat(sep=" "), [])
"""
class GroupAnalyzer:
    def __init__(self, file_path):
        self.file_path = file_path

    def parse_chat_data(self):
        with open(self.file_path, "r", encoding="utf-8") as file:
            chat_lines = file.readlines()

        chat_data = []
        for line in chat_lines:
            match = re.match(r'(\d{2}\/\d{2}\/\d{2}, \d{1,2}:\d{2} [apm]{2}) - (.*?):(.*)', line)
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