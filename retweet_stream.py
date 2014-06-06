import os
import sys
import twitter 
import pymongo
import datetime
import threading
from multiprocessing import Process

OAUTH_TOKEN = ''
OAUTH_SECRET = ''
CONSUMER_KEY = ''
CONSUMER_SECRET = ''


class PrintTweets(threading.Thread):
    def __init__(self, event, mins_ago):
        threading.Thread.__init__(self)
        self.stopped = event
        self.mins_ago = mins_ago
        client = pymongo.MongoClient()
        self.db = client.medisas_challenge

       
    def run(self):
        while not self.stopped.wait(1):
            self.print_top_retweets(self.mins_ago)

    def print_top_retweets(self, mins_ago):
        mins_ago_dt = datetime.datetime.utcnow() -\
            datetime.timedelta(minutes=mins_ago)

        pipline = [
            {'$match': {'created_at': {'$gte': mins_ago_dt}}}, 
            {'$group': {'_id': '$tweet_id', 'count': {'$sum':1}}},
            {'$sort': {'count': -1} },
            {'$limit': 10}
        ]

        rt_window = self.db.rt_count.aggregate(pipline)['result']

        top_10 = []
        for index, item in enumerate(rt_window):
            tweet_id = item['_id']
            tweet_text = self.db.tweets.find_one({'tweet_id': tweet_id})['text']
            top_10.append('%d. # Retweets: %d tweet: "%s"' % (index+1,
                item['count'], tweet_text))

        os.system('clear')

        for item in top_10:
            print item

def scrape_twitter():
    auth = twitter.OAuth(OAUTH_TOKEN, OAUTH_SECRET,
        CONSUMER_KEY, CONSUMER_SECRET)
    stream = twitter.TwitterStream(auth=auth)
    samples = stream.statuses.sample(filter_level='medium')

    client = pymongo.MongoClient()
    db = client.medisas_challenge
    rt_count = db.rt_count
    tweets = db.tweets

    for tweet in samples:
        try:
            if tweet['retweeted_status']:
                original_tweet = tweet['retweeted_status']
                created_at = datetime.datetime.strptime(
                    tweet['created_at'],'%a %b %d %X +0000 %Y')
                original_created_at = datetime.datetime.strptime(
                    original_tweet['created_at'],'%a %b %d %X +0000 %Y')
                original_text = original_tweet['text']
                tweet_id = original_tweet['id']
                data = {'tweet_id':tweet_id, 'text': original_text,\
                    'created_at':original_created_at }
                db.tweets.update({'tweet_id':tweet_id}, data, upsert=True)
                
                db.rt_count.insert({'tweet_id': tweet_id, 'created_at': created_at}) 

        except KeyError:
            # Given tweet isn't a RT, ignore it
            pass


if __name__ == '__main__':
    scraper = Process(target=scrape_twitter)
    scraper.start()

    stop_flag = threading.Event()

    print "Enter a number X to see the top 10 retweets in the past X minutes"

    while sys.stdin:
        num = raw_input()
        try:
            mins_ago = int(num)
            print 'Here are the top 10 retweets from the last %d minutes' % mins_ago
            printer = PrintTweets(stop_flag, mins_ago)
            printer.run()
        except:
            #input wasn't a number. Ignore it
            pass

            

