import tweepy

import pymongo
from credentials import *
consumer_key = a_key
consumer_secret = a_secret
access_key = c_key
access_secret = c_secret
print tweepy.models.Status.parse

def get_all_tweets(screen_name):
	#Twitter only allows access to a users most recent 3240 tweets with this method

	#authorize twitter, initialize tweepy
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_key, access_secret)
	api = tweepy.API(auth)

	#initialize a list to hold all the tweepy Tweets
	alltweets = []

	#make initial request for most recent tweets (200 is the maximum allowed count)
	new_tweets = api.user_timeline(screen_name = screen_name,count=200)

	#save most recent tweets
	alltweets.extend(new_tweets)

	#save the id of the oldest tweet less one
	oldest = alltweets[-1].id - 1

	#keep grabbing tweets until there are no tweets left to grab
	while len(new_tweets) > 0:
		print "getting tweets before %s" % (oldest)

		#all subsiquent requests use the max_id param to prevent duplicates
		new_tweets = api.user_timeline(screen_name = screen_name,count=200,max_id=oldest)

		#save most recent tweets
		alltweets.extend(new_tweets)

		#update the id of the oldest tweet less one
		oldest = alltweets[-1].id - 1

		print "...%s tweets downloaded so far" % (len(alltweets))

	#transform the tweepy tweets into a 2D array that will populate the csv

        outtweets = [{"timeline":tweet.user.name,"in_reply_to_screen_name":tweet.in_reply_to_screen_name,"in_reply_to_user_id":tweet.in_reply_to_user_id, "id":tweet.id_str,"created_at":tweet.created_at, "data":tweet.text.encode("utf-8")} for tweet in alltweets]


        return outtweets


def download_and_save(screen_name,collection):
        newTweets=pymongo.MongoClient()['polsent'][collection]
        newTweets.remove({})
        for t in get_all_tweets(screen_name):
            newTweets.insert(t)
import sys
if __name__=="__main__":
    arg=sys.argv
    download_and_save(arg[1],arg[1])

