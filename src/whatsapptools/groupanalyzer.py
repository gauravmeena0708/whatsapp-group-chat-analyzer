import re, regex, nltk, emoji
from datetime import datetime
import pandas as pd
from nltk.corpus import stopwords
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from calendar import day_name
import numpy as np
import plotly.express as px
import argparse
import os
import json

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

    def generate_wordcloud(self, text, stop_words, output_path): # Added output_path
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
        # plt.show() # Removed
        plt.savefig(output_path) # Added
        plt.close() # Close the figure to free memory
        return output_path # Added
        
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
        
    def create_plotly_fig(self, data,x,y,sortby,asc=False,count=True):
        if count:
            grouped_data =data.groupby(x,as_index=False)[y].count()
        else:
            grouped_data =data.groupby(x,as_index=False)[y].sum()
        if sortby!=0:
            grouped_data = grouped_data.sort_values(sortby, ascending=asc)
        
        fig = px.line(
            x=list(grouped_data[x]),
            y=list(grouped_data[y]),
            title= 'Number of '+y+ ' by '+x,
            labels={
                'x': x,
                'y': 'Number of '+y
            }
          )
          # Show the figure.
        return fig #.show()

    def get_basic_stats(self, df):
        """Calculates basic statistics from the cleaned chat DataFrame."""
        if df.empty:
            return {
                "total_users": 0,
                "total_messages": 0,
                "total_media_messages": 0,
                "total_links_shared": 0,
                "error": "DataFrame is empty."
            }
        
        stats = {
            "total_users": df['name'].nunique() if 'name' in df.columns else 0,
            "total_messages": len(df),
            "total_media_messages": int(df['mediacount'].sum()) if 'mediacount' in df.columns else 0,
            "total_links_shared": int(df['urlcount'].sum()) if 'urlcount' in df.columns else 0
        }
        return stats

    def get_top_emojis_global(self, df, top_n=20):
        """Extracts and counts top N emojis globally from the 'emoji' column."""
        if df.empty or 'emoji' not in df.columns or df['emoji'].apply(lambda x: isinstance(x, list) and len(x) == 0).all():
            return pd.DataFrame(columns=['emoji', 'count']) # Return empty DataFrame

        emojis_series = df['emoji'].explode().dropna()
        if emojis_series.empty:
            return pd.DataFrame(columns=['emoji', 'count'])

        emoji_counts = emojis_series.value_counts().head(top_n)
        emoji_df = emoji_counts.reset_index()
        # Ensure correct column names after reset_index for recent pandas versions
        if emoji_df.shape[1] == 2: # Check if reset_index produced two columns
             emoji_df.columns = ['emoji', 'count']
        else: # Fallback for older pandas or unexpected behavior
            emoji_df = pd.DataFrame({'emoji': emoji_counts.index, 'count': emoji_counts.values})
        return emoji_df

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze WhatsApp chat data and generate reports.")
    parser.add_argument("--input_file", required=True, help="Path to the input WhatsApp chat TXT file.")
    parser.add_argument("--output_dir", required=True, help="Directory to save generated files (plots, CSVs).")
    parser.add_argument(
        "--analyses",
        type=str,
        default="wordcloud,chat_data_csv",
        help="Comma-separated string of analyses to run (e.g., 'wordcloud,chat_data_csv,message_count_plot'). Default: 'wordcloud,chat_data_csv'."
    )

    args = parser.parse_args()

    # The script assumes output_dir exists, as per subtask instructions.
    # os.makedirs(args.output_dir, exist_ok=True) # Would be added for robustness

    analyzer = GroupAnalyzer(args.input_file)
    df_raw = analyzer.parse_chat_data()
    
    results = {}

    if not df_raw.empty:
        df_cleaned = analyzer.df_basic_cleanup(df_raw.copy()) # Use .copy()

        analyses_to_run = [analysis.strip() for analysis in args.analyses.split(',')]

        # 1. Generate Word Cloud (if requested)
        if "wordcloud" in analyses_to_run:
            if "message" in df_cleaned.columns and not df_cleaned["message"].empty:
                text_for_wordcloud = " ".join(df_cleaned["message"].astype(str).tolist())
                # Ensure nltk stopwords are available. 
                # For this subtask, we assume 'stopwords' corpus is available.
                # try:
                #     from nltk.corpus import stopwords
                # except LookupError:
                #     nltk.download('stopwords', quiet=True) # quiet=True to avoid verbose output
                #     from nltk.corpus import stopwords
                stop_words_list = stopwords.words('english') # Default English stopwords
                
                wordcloud_filename = "wordcloud.png"
                wordcloud_output_path = os.path.join(args.output_dir, wordcloud_filename)
                
                generated_wordcloud_path = analyzer.generate_wordcloud(
                    text_for_wordcloud, 
                    stop_words_list, 
                    wordcloud_output_path
                )
                results["wordcloud_image"] = generated_wordcloud_path
            else:
                results["wordcloud_image"] = None # Or an error message / empty string

        # 2. Save Cleaned DataFrame to CSV (if requested)
        if "chat_data_csv" in analyses_to_run:
            csv_filename = "chat_data.csv"
            csv_output_path = os.path.join(args.output_dir, csv_filename)
            df_cleaned.to_csv(csv_output_path, index=False)
            results["chat_data_csv"] = csv_output_path
        
        # Example for a Plotly figure (e.g., message count by user)
        
        # 3. Basic Statistics (if requested)
        if "basic_stats" in analyses_to_run:
            if not df_cleaned.empty:
                basic_stats_data = analyzer.get_basic_stats(df_cleaned)
                results["basic_stats_data"] = basic_stats_data
            else:
                results["basic_stats_data"] = {"error": "Cleaned DataFrame is empty, cannot generate basic stats."}

        # 4. Most Active Users Plot (if requested)
        if "most_active_users_plot" in analyses_to_run:
            if not df_cleaned.empty and 'name' in df_cleaned.columns and 'message' in df_cleaned.columns:
                try:
                    fig_active_users = analyzer.create_plotly_fig(
                        df_cleaned, 
                        x='name', 
                        y='message', 
                        sortby='message', 
                        asc=False, 
                        count=True
                    )
                    fig_active_users.update_layout(title_text="Most Active Users by Message Count")
                    plot_filename = "most_active_users.png"
                    plot_output_path = os.path.join(args.output_dir, plot_filename)
                    fig_active_users.write_image(plot_output_path) 
                    results["most_active_users_plot"] = plot_output_path
                except ImportError:
                     results["most_active_users_plot"] = "Skipped: kaleido package not installed, required for image export."
                except Exception as e:
                    results["most_active_users_plot"] = f"Error generating most_active_users_plot: {str(e)}"
            else:
                results["most_active_users_plot"] = "Skipped: Dataframe empty or missing 'name'/'message' columns."

        # 5. Most Active Day Plot (if requested)
        if "most_active_day_plot" in analyses_to_run:
            if not df_cleaned.empty and 'dayn' in df_cleaned.columns and 'message' in df_cleaned.columns:
                try:
                    # For specific day order (Mon-Sun), 'dayn' should be categorical with order.
                    # Example:
                    # days_ordered = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                    # df_cleaned['dayn'] = pd.Categorical(df_cleaned['dayn'], categories=days_ordered, ordered=True)
                    # Then, create_plotly_fig would need to respect this if sortby is not used or groups are pre-sorted.
                    # For now, default sort by count is used.
                    fig_active_day = analyzer.create_plotly_fig(
                        df_cleaned, 
                        x='dayn', 
                        y='message', 
                        sortby='message', # This will sort by count, not by day order
                        asc=False, 
                        count=True
                    )
                    fig_active_day.update_layout(title_text="Most Active Days of the Week by Message Count")
                    plot_filename = "most_active_day.png"
                    plot_output_path = os.path.join(args.output_dir, plot_filename)
                    fig_active_day.write_image(plot_output_path)
                    results["most_active_day_plot"] = plot_output_path
                except ImportError:
                     results["most_active_day_plot"] = "Skipped: kaleido package not installed, required for image export."
                except Exception as e:
                    results["most_active_day_plot"] = f"Error generating most_active_day_plot: {str(e)}"
            else:
                results["most_active_day_plot"] = "Skipped: Dataframe empty or missing 'dayn'/'message' columns."

        # 6. Top Emojis Global CSV (if requested)
        if "top_emojis_global_csv" in analyses_to_run:
            if not df_cleaned.empty and 'emoji' in df_cleaned.columns:
                try:
                    top_emojis_df = analyzer.get_top_emojis_global(df_cleaned, top_n=20)
                    if not top_emojis_df.empty:
                        csv_filename = "top_emojis_global.csv"
                        csv_output_path = os.path.join(args.output_dir, csv_filename)
                        top_emojis_df.to_csv(csv_output_path, index=False)
                        results["top_emojis_global_csv"] = csv_output_path
                    else:
                        results["top_emojis_global_csv"] = "Skipped: No emojis found or DataFrame was empty after processing."
                except Exception as e:
                    results["top_emojis_global_csv"] = f"Error generating top_emojis_global_csv: {str(e)}"
            else:
                results["top_emojis_global_csv"] = "Skipped: Dataframe empty or missing 'emoji' column."
        
        # --- Placeholder for message_count_plot (example from previous state) ---
        # This can be removed or adapted if it's one of the explicitly requested analyses.
        # For now, it's left as a non-default analysis.
        if "message_count_plot" in analyses_to_run: # This was an example, keeping it conditional
            if not df_cleaned.empty and 'name' in df_cleaned.columns and 'message' in df_cleaned.columns:
                try:
                    fig_message_count = analyzer.create_plotly_fig(df_cleaned, 'name', 'message', 'message', count=True)
                    fig_message_count.update_layout(title_text="Message Count by User (Example)")
                    plot_filename = "message_count_by_user_example.png" # Renamed to avoid conflict if it becomes a standard analysis
                    plot_output_path = os.path.join(args.output_dir, plot_filename)
                    fig_message_count.write_image(plot_output_path) 
                    results["message_count_plot_example"] = plot_output_path # Renamed key
                except ImportError:
                    results["message_count_plot_example"] = "Skipped example plot: kaleido not installed."
                except Exception as e:
                    results["message_count_plot_example"] = f"Error generating example message_count_plot: {str(e)}"
            else:
                results["message_count_plot_example"] = "Skipped example plot: Dataframe empty or missing 'name'/'message' columns."
    else:
        # Handle empty raw dataframe (e.g. if file was empty or parsing failed)
        results["error"] = "Input file could not be parsed or was empty."
        # Initialize keys for requested analyses to None if df_raw is empty or processing failed early
        requested_analyses_list = args.analyses.split(',') if args.analyses else ["wordcloud","chat_data_csv"]
        default_keys_if_empty_df = {
            "wordcloud_image": None,
            "chat_data_csv": None,
            "basic_stats_data": {"error": "Input file could not be parsed or was empty."},
            "most_active_users_plot": "Skipped: Input file could not be parsed or was empty.",
            "most_active_day_plot": "Skipped: Input file could not be parsed or was empty.",
            "top_emojis_global_csv": "Skipped: Input file could not be parsed or was empty."
        }
        for key in requested_analyses_list:
            # map analysis name to result key if different
            # e.g. if analysis name is 'most_active_users' and key is 'most_active_users_plot'
            # This is a simplified mapping for now.
            mapped_key = key 
            if key == "most_active_users": mapped_key = "most_active_users_plot"
            if key == "most_active_day": mapped_key = "most_active_day_plot"
            if key == "top_emojis_global": mapped_key = "top_emojis_global_csv"

            if mapped_key not in results and mapped_key in default_keys_if_empty_df:
                 results[mapped_key] = default_keys_if_empty_df[mapped_key]


    # Print the JSON object to stdout
    print(json.dumps(results, indent=2)) # indent for readability if viewed directly