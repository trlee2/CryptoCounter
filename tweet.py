import tweepy
import sys
from TwitterAPI import TwitterPager
import TwitterAPI
import datetime
import time

#pip install TwitterAPI

consumer_key = '6toOrdLOCWsNo9sg5qgsQm9uX'
consumer_secret = 'MHFMWgq73xgCPISejy0Xnp6mXdz65hbRnMTzmb8Ur7kIhVCpRl'
access_token = '983406965626998784-enX8B14U6aEgDsXFRvhpzpNTJ98YCFE'
access_token_secret = 'INOYCQC3FmWsO3qMPkygVIMKhFywDKudFlviqHxBNfrpj'
class tweet():
	def getTweetCount(q, p=False, debug=False):
		auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
		auth.set_access_token(access_token, access_token_secret)

		api = TwitterAPI.TwitterAPI(consumer_key, consumer_secret, access_token, access_token_secret)

		#today's info
		a = time.time()
		timeStamp = datetime.datetime.utcnow().date()
		tDay = timeStamp.day
		tMonth = timeStamp.strftime("%b")

		api = TwitterAPI.TwitterAPI(consumer_key, consumer_secret, access_token, access_token_secret)
		count = 0
		r = TwitterPager(api, 'search/tweets', {'q':q, 'count':100})
		for item in r.get_iterator(wait=6):
			time_stamp = item['created_at']			
			day = int(time_stamp[8:10])
			if(tDay != day and tDay-1 != day):
				break
			if 'message' in item and item['code'] == 88:
				print('SUSPEND, RATE LIMIT EXCEEDED: %s' % item['message'])
				break
			if(tDay-1 == day):
				count +=1
				if(p):
					print("Term: "+q+" on "+item["created_at"])

		if(debug):
			b = time.time()
			c = int(b-a)
			print("\nThis took " + str(round(c/60,2)) + " minutes")
			
		return count
		
#res = tweet.getTweetCount("qwertyuiop", False,True)
#print(res)