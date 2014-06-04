import sys
import twitter 
import pymongo
import datetime
from multiprocessing import Process

OAUTH_TOKEN = ''
OAUTH_SECRET = ''
CONSUMER_KEY = ''
CONSUMER_SECRET = ''


def print_top_retweets(mins_ago):
    print 'Here are the top 10 retweets from the last %d minutes' % mins_ago
    
    client = pymongo.MongoClient()
    db = client.medisas_challenge
    collection = db.retweets

    mins_ago_dt = datetime.datetime.utcnow() -\
        datetime.timedelta(minutes=mins_ago)

    res = collection.find({"created_at": {"$gte": mins_ago_dt}})\
            .sort("retweet_count", pymongo.DESCENDING)\
            .limit(10)

    for index, item in enumerate(res):
        print '%d. # Retweets: %d tweet: "%s"' % (index+1,
            item['retweet_count'], item['text'])


def scrape_twitter():
    auth = twitter.OAuth(OAUTH_TOKEN, OAUTH_SECRET,
        CONSUMER_KEY, CONSUMER_SECRET)
    stream = twitter.TwitterStream(auth=auth)
    samples = stream.statuses.sample(filter_level='medium')

    client = pymongo.MongoClient()
    db = client.medisas_challenge
    collection = db.retweets

    for tweet in samples:
        try:
            if tweet['retweeted_status']:
                tweet = tweet['retweeted_status']
                #save to DB because it has been retweeted atleast once
                created_at = datetime.datetime.strptime(tweet['created_at'],
                    '%a %b %d %X +0000 %Y')
                text = tweet['text']
                retweet_count = tweet['retweet_count']
                id = tweet['id']
                data = {'id':id, 'text': text, 'retweet_count': retweet_count,
                    'created_at': created_at}
                collection.update({'id': id}, data, upsert=True)
        except KeyError:
            pass


if __name__ == '__main__':
    scraper = Process(target=scrape_twitter)
    scraper.start()

    print "Enter a number X to see the top 10 retweets in the past X minutes"

    while sys.stdin:
        num = raw_input()
        try:
            mins_ago = int(num)
            print_top_retweets(mins_ago)
            print '\n'
        except:
            pass

