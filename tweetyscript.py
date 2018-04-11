import tweepy

consumer_key = "6toOrdLOCWsNo9sg5qgsQm9uX"
consumer_secret = "MHFMWgq73xgCPISejy0Xnp6mXdz65hbRnMTzmb8Ur7kIhVCpRl"
access_token = "983406965626998784-enX8B14U6aEgDsXFRvhpzpNTJ98YCFE"
access_token_secret = "INOYCQC3FmWsO3qMPkygVIMKhFywDKudFlviqHxBNfrpj"
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

public_tweets = api.home_timeline()
for tweet in public_tweets:
    print (tweet.text)