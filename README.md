# Whatsapp Tools

## Web Application Interface

This project also includes a web-based interface for analyzing WhatsApp chat files.

### Setup

Follow these steps to set up and run the web application on your local machine.

#### Prerequisites

*   **Node.js and npm:** Ensure you have Node.js (which includes npm) installed. You can download it from [nodejs.org](https://nodejs.org/).
*   **Python 3 and pip:** Ensure you have Python 3 and pip (Python's package installer) installed. You can download Python from [python.org](https://python.org/).

#### Backend Setup

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```
2.  **Install Node.js dependencies:**
    ```bash
    npm install
    ```
    This will install Express.js, multer, cors, and other necessary packages.

#### Python Environment Setup

1.  **Navigate to the project root directory** (if you are in the `backend` directory, use `cd ..`).
2.  **Create a Python virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    ```
3.  **Activate the virtual environment:**
    *   On macOS and Linux:
        ```bash
        source venv/bin/activate
        ```
    *   On Windows:
        ```bash
        venv\Scripts\activate
        ```
4.  **Install Python dependencies:**
    Make sure you are in the project root directory where `requirements.txt` is located.
    ```bash
    pip install -r requirements.txt
    ```
5.  **Download NLTK stopwords corpus (one-time setup):**
    If this is your first time using NLTK or this specific corpus, you'll need to download it. Run the following in a Python interpreter:
    ```python
    import nltk
    nltk.download('stopwords')
    ```
    You can exit the Python interpreter after the download is complete.

### Running the Application

1.  **Start the Backend Server:**
    *   Navigate to the backend directory:
        ```bash
        cd backend
        ```
    *   Run the server:
        ```bash
        node index.js
        ```
        Alternatively, if you have `nodemon` installed, you can use `nodemon index.js` for automatic restarts on file changes.
    *   The backend server will typically start on `http://localhost:3000`. You should see a confirmation message in your terminal.

2.  **Access the Frontend:**
    *   Open the `frontend/index.html` file directly in your web browser (e.g., by navigating to its location on your filesystem and double-clicking it, or using your browser's "Open File" option).
    *   **Usage:**
        1.  Click "Choose WhatsApp Chat File (.txt)" to select your exported WhatsApp chat file.
        2.  Select the analyses you want to perform using the checkboxes.
        3.  Click the "Upload and Analyze" button.
        4.  Wait for the processing to complete. Results (statistics, plots, download links) will be displayed on the page.

## install

```bash
pip install -e git+https://github.com/gauravmeena0708/whatsapp-tools#egg=whatsapp-tools
pip install emoji wordcloud
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
analyzer.create_plotly_fig(df1,'name','emojicount','emojicount')
analyzer.create_plotly_fig(df1,'name','urlcount','urlcount')
analyzer.create_plotly_fig(df1,'name','yturlcount','yturlcount')
analyzer.create_plotly_fig(df1,'name','mediacount','mediacount',count=False)
analyzer.create_plotly_fig(df1,'name','editcount','editcount',count=False)
fig = analyzer.create_plotly_fig(df1,'name','deletecount','deletecount',count=False)
fig.write_image("./data/figure_3.png")
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

## Using plotnine.ggplot

```python

import numpy as np
import pandas as pd
from plotnine import *

%matplotlib inline
#df1
#ggplot(df1, aes(x='month', y='mlen')) + geom_point()

import pandas as pd 
from plotnine import ggplot, aes, facet_grid, labs, geom_col 
  
# reading dataset 
xd, yd, color = "day","mlen", 'day'
#+ facet_grid(facets="~year")
#p1.save(filename="./data/figure_1.png", quiet=True)
#plot = ggplot(df1, aes(x=xd, y=yd, fill=color)) + labs( x=xd, y=yd) + geom_col()
#plot = ggplot(df1, aes(x='date_time')) + geom_line(stat='count', color='blue') 
#plot = ggplot(df1, aes(x='dow', y='mlen')) + geom_line(stat='sum', color='blue') 
#plot = ggplot(df1, aes(x='dow', y='mlen')) + geom_bar(stat='sum')
#plot = ggplot(df1, aes(x='month', y='mlen',color='mlen')) + geom_point() 
#plot = ggplot(df1, aes(x='emojicount')) + geom_histogram(binwidth=1, fill='blue', color='black', alpha=0.7) 
#plot = ggplot(df1, aes(x='monthn', y='editcount')) + geom_boxplot()
#plot = ggplot(df1, aes(x='dow', y='hour')) + geom_tile(aes(fill='mlen'), color='white') + scale_fill_gradient(low='white', high='blue') 
#plot = ggplot(df1, aes(x='day')) + geom_bar(stat='count', fill='green') + coord_flip()
#plot = ggplot(df1, aes(x='month')) +geom_bar(stat='count', fill='green') + coord_flip()
#plot = ggplot(df1, aes(x='mlen')) +geom_histogram(binwidth=10, fill='orange', color='black', alpha=0.7) 

#plot = (ggplot(df1, aes(x="hour", y="emojicount", color="ym")) +geom_point() +facet_wrap("~year") +labs(x="Hour of Day", y="Emoji Count", title="Emojis by Hour and Month"))
plot = (ggplot(df1, aes(x="hour", y="emojicount", color="ym")) +geom_point() +facet_wrap('~ym') +labs(x="Hour of Day", y="Emoji Count", title="Emojis by Hour and Month"))
plot = (ggplot(df1, aes(x="mlen")) + geom_histogram(bins=30) +labs(x="Message Length", y="Count", title="Distribution of Message Lengths"))
plot = (
    ggplot(df1, aes(x="mlen", color="dow")) +
    geom_histogram(bins=30) +
    facet_wrap('~dow') +
    labs(x="Message Length", y="Count", title="Message Length Distribution by Name")
)

print(plot)
```

```python
from plotnine import ggplot, geom_point, aes, stat_smooth, facet_wrap
from plotnine.data import mtcars

(ggplot(mtcars, aes("wt", "mpg", color="factor(gear)"))
 + geom_point()
 + stat_smooth(method="lm")
 + facet_wrap("~gear"))
```

## Inspiration

1. [https://github.com/TJMusiitwa/FabFamilyWhatsappChatAnalysis](https://github.com/TJMusiitwa/FabFamilyWhatsappChatAnalysis)
