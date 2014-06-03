Medisas Code Challenge
======================


  Use Twitter's streaming API to show the top 10 retweeted tweets in a rolling window of time, where the window's start   is n minutes ago (where n is defined by the user) and the window's end is the current time.


#Requirements

python 2.x
virtualenv
mongodb (default settings)

#Setup Part 1: Twitter API Credentials

1. Go to dev.twitter.com and set up an app
2. edit the ```retweet_steam.py``` file and fill in the necessary Twitter API values

#Setup Part 2: MongoDB

1. install MongoDB (see http://www.mongodb.org/downloads for more details)
2. Start mongoDB on your computer with the default configuration

#Setup Part 3: Python Environment

1. create a new Python virutalenv
2. activate your virtualenv and use it from here on
3. install the listed packages in requirements.txt ```pip install -r requirements.txt```

#Running the code

1. from your terminal run ```python retweet_stream.py```
2. Type into the console a single number follow by the return key.

#Notes

When you first start retweet_stream.py a background process will start scraping
the Twitter API (statuses/sample.json&filter_level=medium). If the scraper sees 
a tweet with retweet_count > 0 it saves that tweet into MongoDB. However, in my
brief time testing the scraper, I rarely ever see tweets with retweet_count > 0.
I'd guess that 99% of tweets are not retweeted. I can't seem to find the
streaming API that allows me to filter by retweets.
