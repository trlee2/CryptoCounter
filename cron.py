import requests
import json
import psycopg2
import sys
import CryptoSite.settings as settings
import datetime
import time
import pprint
from pytrends.request import TrendReq
from apscheduler.schedulers.blocking import BlockingScheduler
pytrends = TrendReq(hl='en-US', tz=360)
import praw
import prawcore
import tweet
'''
pip install requests
pip install apscheduler
pip install pytrends
pip install praw

To Test:
$ python -m unittest -v cron
'''

'''
This is the code for updaing the database with new information on 
the coins and ICO ran by cronjobs fround in the 
CryptoSite/settings.py file.
'''
numCoins = 10; #Top coins from coinMarketCap.com
trackedCoins = [] #coins currently being tracked
mode = []
historyDays = 184 #default is 6 months = 184 days
coinMarketCap = "https://api.coinmarketcap.com/v1/ticker/"
cryptoCompare = "https://min-api.cryptocompare.com/data/"
cryptoCompareList = "https://www.cryptocompare.com/api/data/"
icoWatchList = "https://api.icowatchlist.com/public/v1/" 
newsapi = "https://newsapi.org/v2/everything?q="
newsapi_keys = ["&apiKey=e9f31afd6dd54e14930244b5f52cdc45","&apiKey=7f9ed31f06e7459b8aa3121e437b30d3","&apiKey=4ff3432a39664cb0a21e24e63caef9bf","&apiKey=2df0257ef60d402c812c70d47c172612","&apiKey=8b211b2c69064b05a69b21989ee7e1ef","&apiKey=12ecd0af2710410dbb6a8b982cbe1f70","&apiKey=1f625b75875340b094da51d2b0c49d1a",
"&apiKey=5e37b20fc557425aaa9ab746931d28a3",
"&apiKey=221fb27d4dec45c09bed936b96e8255b",
"&apiKey=c2052cc3c5da4159a014d7ec2b386028",
"&apiKey=9cf2a84e2b864bae91ad09143833cced",
"&apiKey=acef470a1f0f4adbb8096611667951c2",
"&apiKey=456094da5e2f44198c1f7b0969a6b779",
"&apiKey=ffbcf0cb9b69498a8a37c7795e174bfc",
"&apiKey=adbfbb9684cb49f796edbe10636f2066",
"&apiKey=d8ae5b58e68c49a08d495994d468dee6",
"&apiKey=5795f2d93e5143a5b6168a7239249ab7",
"&apiKey=08b323fc912548428a5252f9d517b13c",
"&apiKey=0ae45a471f5847ff81bf0f9a96805cef",
"&apiKey=b543fcc6eb534eec9bfc0cd7832f91f8",
"&apiKey=1f064fa3aa2b4e9c9fc80b034f7e889a",

]
newsapi_key = 0

'''
A universal function that retrieves the JSON data from each of the
APIs we are using and returns the raw JSON Object.

@params String api
@returns	JSON Object	
'''
def getAPI(api):
	res = requests.get(api)
	#res.raise_for_status()
	data = res.json()
	return data

'''
A helper function to connect to the DB
@return conn
'''
def getConnected():
	db_info = settings.DATABASES["default"]
	try:
		conn = psycopg2.connect("dbname="+db_info["NAME"]+" user="+db_info["USER"]+" host="+db_info["HOST"]+" password="+db_info["PASSWORD"])
	except:
		print("I am unable to connect to the db")

	return conn;

'''
Pulls the list of coins currently being tracked from the database 
and puts them in the trackedCoins array

@returns	void
'''
def getTrackedCoins():
	conn = getConnected()
	cur = conn.cursor()
	
	cur.execute("SELECT * FROM cryptocounter_coin")
	row = cur.fetchall()

	#clear the entire global array for new data
	del trackedCoins[:]
	for i in range(0, len(row)):
		trackedCoins.append(row[i][2])

	conn.close()

'''
Scans the coinmarketcap API for the top numCoins and compares it 
with the list retrieved from getTrackedCoins(). If a coin is not 
found on the current list, add the new coin to both the database 
and the the list of searched coins.

@params		int numCoins
@returns	void	
'''
def setTrackedCoins():
	getTrackedCoins() #Make sure we have an updated list
	trackedLength = len(trackedCoins)

	#Use the list of tracked coins and compare with coinmarketcap
	conn = getConnected()
	cur = conn.cursor()
	market = getAPI(coinMarketCap+"?limit="+str(numCoins))
	for i in range(0, len(market)):
		if(market[i]["symbol"] not in trackedCoins):
			#TODO: find true blockchain
			cname = market[i]["name"]
			ticker = market[i]["symbol"]
			bc = market[i]["name"]
			terms = "[\""+market[i]["symbol"]+"\",\""+market[i]["name"]+"\"]"
			cur.execute("INSERT INTO cryptocounter_coin (coin_name, ticker, block_chain, search_terms) VALUES('{}','{}','{}','{}')".format(cname,ticker,bc,terms))

	conn.commit()
	getTrackedCoins() #Get updated list
	conn.close()

'''
Parse the JSON data from the cryptocompare API and return an array 
of current prices for each coin.

@params		String[] coinList
@returns	Array of coin:price
'''
def parseCurrentPrice(coinList):
	coins = ""
	for i in range(0, len(coinList)):
		if(coinList[i] == "MIOTA"):
			coins += "IOT"
		else:
			coins += coinList[i]
		if(i != len(coinList)-1):
			coins += ","

	data = getAPI(cryptoCompare+"pricemulti?fsyms="+coins+"&tsyms=USD")
	market = getAPI(coinMarketCap) #TODO:fix to include if rank is > 100

	prices = []
	for key in data.keys():
		want = {}
		for i in range(0, len(market)):
			if(key == "IOT" and market[i]["symbol"] == "MIOTA"):
				want = market[i]
				break
			elif(key == market[i]["symbol"]):
				want = market[i]
				break

		price = {}
		if(key == "IOT"):
			price["ticker"] = "IOTA"
		else:
			price["ticker"] = key
		price["price"] = data[key]["USD"]
		price["circ_supply"] = want["available_supply"]
		price["percent_change"] = want["percent_change_24h"]
		price["market_cap"] = want["market_cap_usd"]
		d = time.time()
		now = int(d-(d%86400)) #184
		price["date"] =  now #want["last_updated"]
		prices.append(price)

	return prices

'''
Parse the JSON data from the cryptocompare API and return an array 
of historical data for each coin on date. 

@params		String[] coinList, int date
@returns	Array of coin:price
'''
def parseHistoricalPrice(coinList, date):
	prices = []
	for i in range(0, len(coinList)):
		cList = coinList[i]
		if(coinList[i] == "MIOTA"):
			cList = "IOT"
		data = getAPI(cryptoCompare+"pricehistorical?fsym="+cList+"&tsyms=USD&ts="+str(date))
		market = getAPI(coinMarketCap) #TODO:fix to include if rank is > 100

		for key in data.keys():
			want = {}
			for j in range(0, len(market)):
				if(key == "IOT" and market[j]["symbol"] == "MIOTA"):
					want = market[j]
					break
				elif(key == market[j]["symbol"]):
					want = market[j]
					break

			price = {}
			if(key == "IOT"):
				price["ticker"] = "IOTA"
			else:
				price["ticker"] = key
			price["price"] = data[key]["USD"]
			price["circ_supply"] = want["available_supply"]
			price["percent_change"] = -1
			price["market_cap"] = want["market_cap_usd"]
			price["date"] = date
			prices.append(price)

			#wait some time to prevent abusing API
			#ten coins per second
			time.sleep(0.1)
	#if we have time, update percent_change
	return prices

'''
Parse the JSON data from the icowatchlist API and compare it with 
the ICO already in the database. Add any ICOs not in our database 
to our database.
		
@returns	String[]	
'''
def parseICO():
	data = getAPI(icoWatchList)

	ico_dict = []
	for ico in data.keys():
		for status in data[ico].keys(): 
			for i in range(0, len(data[ico][status])):
				ico_inner = {}
				ico_inner["ico_name"] = data[ico][status][i]["name"]
				ico_inner["search_terms"] = '["'+data[ico][status][i]["name"]+'"]' #TODO: update this with more terms, ticker if found
				ico_inner["start"] = data[ico][status][i]["start_time"]
				ico_inner["end"] = data[ico][status][i]["end_time"]
				ico_inner["description"] = data[ico][status][i]["description"]
				ico_dict.append(ico_inner)

	return ico_dict

'''
Retrive twitter count for given name in 24 hours

@params		String
@returns	int
'''	
def getTwitter(name):
	print("-> Working on getting twitter info: "+name)
	res = tweet.tweet.getTweetCount(name)
	return res
	
'''
Retrive reddit subs for given list

@params		String
@returns	int
'''
def getRedditSub(list):
	reddit = praw.Reddit(client_id='HPokGrej1cnYhg',
		client_secret='8afAIRDxAIGlGtrckbnkO0Dklzo',
		password='firerock285',
		user_agent='cryptocounter by /u/tomand285',
		username='tomand285')
	
	res = []
	for l in list:
		red = {}
		red["name"] = l
		try:
			sub = reddit.subreddit(l)			
			red["sub"] = sub.subscribers
		except (prawcore.NotFound, prawcore.Redirect, prawcore.Forbidden) as e:
			red["sub"] = -1
		res.append(red)
	if(len(res) < 1):
		return([{"error":-1}])
	else:
		return res

'''
Retive google trends info for given name

@params		String
@returns	JSON
'''		
def getGoogleTrends(name):
	print("-> Working on getting Google info: "+name)
	pytrends.build_payload([name], cat=0, timeframe='today 1-m', geo='', gprop='')
	resRaw = json.loads(pytrends.interest_over_time().to_json())
	if(len(resRaw) < 1):
		return -1
	res = resRaw[name]
	
	
	goog = []
	for k in res.keys():
		pg = {}
		pg["date"] = datetime.datetime.fromtimestamp(int(k)/1000).strftime('%Y-%m-%d %H:%M:%S')
		pg["trend"] = res[k]
		goog.append(pg)
	time.sleep(1) #to prevent error code 429
	return goog

	
'''
Retive Facebook likes for given name

@params		String
@returns	int
'''	
def getFacebook(name):
	num = -1
	#https://graph.facebook.com/oauth/access_token?client_id=428464434260566&client_secret=9264562884e62d1319b25bf125f6865d&grant_type=client_credentials
	at="EAACEdEose0cBADWgrZBKgZAa0bhx6Vqo9FgAozWHZCwd3DLIUubnl0vwAYyww35QedcZA6FvSynC58XViAEVit9tWZBcXx8imRdJ0rNI6YpHUezAtYhfCmvb1h1QGAUcVsciCheUgxSgvBLtirI3SGqfFL1d4e0pYl8992wm8ZBRAxbCf6RyEXgwe7ICZCQvIAZD"
	res = getAPI("https://graph.facebook.com/"+name+"/?fields=fan_count&access_token="+at)
	if("fan_count" in res.keys()):
		num = res["fan_count"]
	return num
	

'''
Loops through keys and retrives a good link for the news

@params		String
@returns	String[]
'''
def newsAPIAdv(data):
	global newsapi_key
	info = getAPI(newsapi+data+newsapi_keys[newsapi_key])
	ticker = 0
	while(info["status"] == "error"):
		newsapi_key = (newsapi_key+1)%len(newsapi_keys)
		info = getAPI(newsapi+data+newsapi_keys[newsapi_key])
		ticker += 1
		if(ticker > len(newsapi_keys)):
			print("ERROR: Ran out of newsapi keys, please add more or wait 6 hours to continue")
			sys.exit(1)
	return info
	
'''
Parse the general news of cryptocurrencies and return as array.

@returns	int	
'''
def parseGeneralNews(terms):
	#5 calls
	#terms = ["crypto","cryptocurrency","cryptocurrencies", "blockchain"]
	
	totalResults = 0;
	tr = []
	for t in terms:
		if(t not in tr):
			data = newsAPIAdv(t)			
			totalResults += data["totalResults"]
			tr.append(t)
	if(len(tr) > 1):
		data = newsAPIAdv(" ".join(tr))
		totalResults -= data["totalResults"]

	return totalResults

def parseGeneralTwitter():
	terms = ["cryptocurrency", "blockchain"]
	#pTweet = parseGeneralTwitter(terms)
	num = 0;
	for i in range(0,len(terms)):
		num += getTwitter(terms[i])
	return num
def parseGeneralReddit():
	return getRedditSub(["cryptocurrency"])[0]["sub"]
def parseGeneralFacebook():
	#TODO: update/fix this
	return getFacebook("cryptocurrency")
	
'''
Parse the specific news for the coin.

@returns	int[]
'''
def parseCoinNews():
	#3*N calls -> 30
	conn = getConnected()
	cur = conn.cursor()
	cur.execute("SELECT * FROM cryptocounter_coin")
	row = cur.fetchall()

	news_dict = []
	for i in range(0, len(row)):
		news_inner = {}
		news_inner["id"] = row[i][0]
		news_inner["ticker"] = row[i][2]
		terms = eval(row[i][4])
		news_inner["terms"] = terms
		totalResults = 0;
		tr = []
		for t in terms:
			if(t not in tr):
				data = newsAPIAdv(t)
				totalResults += data["totalResults"]
				tr.append(t)
		if(len(tr) > 1):
			data = newsAPIAdv(" ".join(tr))
			totalResults -= data["totalResults"]
		news_inner["results"] = totalResults;
		news_dict.append(news_inner)

	return news_dict
	
'''
Parse the Twitter API for any new information on the coins being 
searched and return the array of data.

@params		String[] coinList
@returns	int	
'''
def parseCoinTwitter(coinList):
	id = 0
	coin = ""
	twitter = []
	for i in range(0, len(coinList)):
		if(coinList[i] == "MIOTA"):
			coin = "IOT"
		else:
			coin = coinList[i]
			
		tweet = {}
		data = getAPI(cryptoCompareList+"coinlist/")
		id = data["Data"][coin]["Id"]
		tweetRaw = getAPI(cryptoCompareList+"socialstats/?id="+id)
		tweet["name"] = coin
		tweet["statuses"] = 0
		if("statuses" in tweetRaw["Data"]["Twitter"]):
			tweet["statuses"] = tweetRaw["Data"]["Twitter"]["statuses"]
		else:
			tweet["statuses"] = -1
		
		twitter.append(tweet)

	return twitter

'''
Parse the Reddit data and return it as an array.

@params		String[] coinList
@returns	int[]
'''
def parseCoinReddit(coinList):
	id = 0
	coin = ""
	reddit = []
	for i in range(0, len(coinList)):
		if(coinList[i] == "MIOTA"):
			coin = "IOT"
		else:
			coin = coinList[i]
			
		red = {}
		data = getAPI(cryptoCompareList+"coinlist/")
		id = data["Data"][coin]["Id"]
		redRaw = getAPI(cryptoCompareList+"socialstats/?id="+id)
		red["name"] = coin
		red["subscribers"] = 0

		if("subscribers" in redRaw["Data"]["Reddit"]):
			red["subscribers"] = redRaw["Data"]["Reddit"]["subscribers"]
		else:
			red["subscribers"] = -1
		
		reddit.append(red)

	return reddit
	
'''
Parse the facebook like data and return it as an array.

@params		String[] coinList
@returns	int[]
'''
def parseCoinFacebook(coinList):
	id = 0
	coin = ""
	facebook = []
	for i in range(0, len(coinList)):
		if(coinList[i] == "MIOTA"):
			coin = "IOT"
		else:
			coin = coinList[i]
			
		fb = {}
		data = getAPI(cryptoCompareList+"coinlist/")
		id = data["Data"][coin]["Id"]
		fbRaw = getAPI(cryptoCompareList+"socialstats/?id="+id)
		fb["name"] = coin
		fb["likes"] = 0

		if("likes" in fbRaw["Data"]["Facebook"]):
			fb["likes"] = fbRaw["Data"]["Facebook"]["likes"]
		else:
			fb["likes"] = -1
		
		facebook.append(fb)

	return facebook



'''
Parse the specific news for the ICO.

@returns	int[]
'''
def parseICONews(row):
	#580+ calls

	ico_dict = []
	for i in range(0, len(row)):
		ico_inner = {}
		ico_inner["id"] = row[i][0]
		ico_inner["name"] = row[i][1]
		terms = eval(row[i][5])
		ico_inner["terms"] = terms
		totalResults = 0;
		tr = []
		for t in terms:
			if(t not in tr):
				data = newsAPIAdv(t)
				totalResults += data["totalResults"]
				tr.append(t)
		if(len(tr) > 1):
			data = newsAPIAdv(" ".join(tr))
			totalResults -= data["totalResults"]
		ico_inner["results"] = totalResults;
		ico_dict.append(ico_inner)

	return ico_dict
	
def parseICOTwitter(terms):
	#TODO: turn back on for real data
	print("Note: Working on ICO Twitter, this may take a long time")
	icoList = []
	for t in terms:
		list = {}
		list["name"] = t
		list["tweets"] = getTwitter(t)
		icoList.append(list)
	return icoList
def parseICOReddit(terms):
	return getRedditSub(terms)
def parseICOFacebook(terms):
	icoList = []
	for t in terms:
		list = {}
		list["name"] = t
		list["likes"] = getFacebook(t)
		icoList.append(list)
	return icoList

### Commands to be called by CRON ###

def addPriceInfo(plist):
	conn = getConnected()
	cur = conn.cursor()
	
	cur.execute("SELECT coin_id, ticker FROM cryptocounter_coin")
	DBcoins = cur.fetchall()

	for i in range(0, len(DBcoins)):
		coin_id = DBcoins[i][0]
		if(DBcoins[i][1] == "MIOTA"):
			ticker = "IOTA"
		else:
			ticker = DBcoins[i][1]

		for data in plist:
			if(data["ticker"] == ticker):
				dt = str(datetime.datetime.fromtimestamp(int(data["date"])))
				p = str(data["price"])
				cid = str(coin_id)
				cs = str(data["circ_supply"])
				mc = str(data["market_cap"])
				pc = str(data["percent_change"])
				cur.execute("INSERT INTO cryptocounter_price (date, price, coin_id_id, circ_supply, market_cap, percent_change) VALUES('{}',{},{},{},{},{})".format(dt,p,cid,cs,mc,pc))
				break
		
	conn.commit()
	conn.close()

#setTrackedCoins() -> once a day

def updateCurrentPrice(): #-> once every day
	#trackedCoins should live	
	hour = 3600
	day = hour * 24

	conn = getConnected()
	cur = conn.cursor()
	cur.execute("SELECT MIN(coin_id_id) as id, date FROM cryptocounter_price GROUP BY date ORDER BY date DESC LIMIT 1")

	DBcoins = cur.fetchall()
	dt = int(time.mktime(DBcoins[0][1].timetuple()))
	dl = int(dt-(dt%day))
	d = time.time()
	now = int(d-(d%day))

	if(now != dl):
		plist = parseCurrentPrice(trackedCoins)
		addPriceInfo(plist)
		print("Current price added: "+ str(datetime.datetime.fromtimestamp(int(now)).strftime('%Y-%m-%d %H:%M:%S')))
	else:
		print("ALERT: Skipping current price, duplicate")
		

def updateHistoricalPrice(days):#-> once upon first boot or every time we need info that can not be found
	hour = 3600
	day = hour * 24

	conn = getConnected()
	cur = conn.cursor()
	cur.execute("SELECT MIN(coin_id_id) as id, date FROM cryptocounter_price GROUP BY date ORDER BY date ASC")
	DBcoins = cur.fetchall()

	#formating dates
	dateList = []
	for j in range(0, len(DBcoins)):
		dt = int(time.mktime(DBcoins[j][1].timetuple()))
		dl = int(dt-(dt%day))
		dateList.append(dl)

	d = time.time()
	now = int(d-(d%day))
	past = now - day * days
	for i in range(past,now,day):
		if(i not in dateList):
			print("Cron is adding: "+str(datetime.datetime.fromtimestamp(int(i)).strftime('%Y-%m-%d %H:%M:%S')))
			plist = parseHistoricalPrice(trackedCoins,i)
			addPriceInfo(plist)

	#TODO: calculate %change
	#updatePC()

def updateICO():#-> once every day
	plist = parseICO()
	conn = getConnected()
	cur = conn.cursor()

	cur.execute("SELECT ico_name FROM cryptocounter_ico")
	DBico_raw = cur.fetchall()

	#format DBico
	DBico = []
	for i in range(0,len(DBico_raw)):
		DBico.append(DBico_raw[i][0])

	for data in plist:
		if(data["ico_name"] not in DBico):

			n = str(data["ico_name"])
			s = str(data["start"])+"-00"
			e = str(data["end"])+"-00"
			d = str(data["description"])
			st = str(data["search_terms"])
			cur.execute("INSERT INTO cryptocounter_ico (ico_name, startdate, enddate, description, search_terms) VALUES('{}','{}','{}','{}','{}')".format(n,s,e,d,st))

		
	conn.commit()
	conn.close()
	
def updateOverallSocial():
	#break
	hour = 3600
	day = 24 * hour
	
	conn = getConnected()
	cur = conn.cursor()

	cur.execute("SELECT MIN(id) as id, date FROM cryptocounter_overallsocial GROUP BY date ORDER BY date ASC LIMIT 1")

	DBsocial = cur.fetchall()
	dl = 0
	d = time.time()
	now = int(d-(d%day))
	if(len(DBsocial) > 0):
		dt = int(time.mktime(DBsocial[0][1].timetuple()))
		dl = int(dt-(dt%day))
	
	if(now != dl):
		terms = ["crypto","cryptocurrency","cryptocurrencies", "blockchain"]
		pNews = parseGeneralNews(terms)
		pReddit = parseGeneralReddit()
		pFB = parseGeneralFacebook()
		
		dt = str(datetime.datetime.fromtimestamp(now))
		cur.execute("INSERT INTO cryptocounter_overallsocial (date, num_tweets, num_subs, num_likes, num_articles, num_trends) VALUES('{}',{},{},{},{},{})".format(dt,-1,pReddit,pFB,pNews,-1))
		print("Current overall social added: "+ str(datetime.datetime.fromtimestamp(int(now)).strftime('%Y-%m-%d %H:%M:%S')))
	else:
		print("ALERT: Skipping current overall social, duplicate")

		
	conn.commit()
	conn.close()

def updateSocialCoin():
	hour = 3600
	day = 24 * hour
	
	conn = getConnected()
	cur = conn.cursor()

	cur.execute("SELECT MIN(id) as id, date FROM cryptocounter_socialcoin GROUP BY date ORDER BY date ASC LIMIT 1")

	DBsocial = cur.fetchall()
	dl = 0
	d = time.time()
	now = int(d-(d%day))
	if(len(DBsocial) > 0):
		dt = int(time.mktime(DBsocial[0][1].timetuple()))
		dl = int(dt-(dt%day))
	
	if(now != dl):
		pNews = parseCoinNews()
		pTweet = parseCoinTwitter(trackedCoins)
		pReddit = parseCoinReddit(trackedCoins)
		pFB = parseCoinFacebook(trackedCoins)
		
		dt = str(datetime.datetime.fromtimestamp(now))
		for i in range(0,len(pNews)):
			coinID = pNews[i]["id"] 
			coinNews = pNews[i]["results"]
			coinTweet = pTweet[i]["statuses"]
			coinSub = pReddit[i]["subscribers"]
			coinLikes = pFB[i]["likes"]
			
			cur.execute("INSERT INTO cryptocounter_socialcoin (date, num_tweets, num_subs, num_likes, num_articles, num_trends, coin_id_id) VALUES('{}',{},{},{},{},{},{})".format(dt,coinTweet,coinSub,coinLikes,coinNews,-1,coinID))
		print("Current social coin added: "+ str(datetime.datetime.fromtimestamp(int(now)).strftime('%Y-%m-%d %H:%M:%S')))
	else:
		print("ALERT: Skipping current social coin, duplicate")

		
	conn.commit()
	conn.close()


def updateSocialICO():
	#break
	hour = 3600
	day = 24 * hour
	
	conn = getConnected()
	cur = conn.cursor()
	
	cur.execute("SELECT * FROM cryptocounter_ico")
	icoInfo = cur.fetchall()
	
	icoList = []
	for z in range(0, len(icoInfo)):
		icoList.append(icoInfo[z][1])
	
	cur.execute("SELECT MIN(id) as id, date FROM cryptocounter_socialico GROUP BY date ORDER BY date ASC LIMIT 1")

	DBsocial = cur.fetchall()
	dl = 0
	d = time.time()
	now = int(d-(d%day))
	if(len(DBsocial) > 0):
		dt = int(time.mktime(DBsocial[0][1].timetuple()))
		dl = int(dt-(dt%day))
	
	if(now != dl):
		pNews = parseICONews(icoInfo)
		pReddit = parseICOReddit(icoList)
		pFB = parseICOFacebook(icoList)

		dt = str(datetime.datetime.fromtimestamp(now))
		for i in range(0,len(pNews)):
			icoID = pNews[i]["id"]
			icoNews = pNews[i]["results"]
			icoSub = pReddit[i]["sub"]
			icoLikes = pFB[i]["likes"]

			cur.execute("INSERT INTO cryptocounter_socialico (date, num_tweets, num_subs, num_likes, num_articles, num_trends, ico_id_id) VALUES('{}',{},{},{},{},{},{})".format(dt,-1,icoSub,icoLikes,icoNews,-1,icoID))
		print("Current social ICO added: "+ str(datetime.datetime.fromtimestamp(int(now)).strftime('%Y-%m-%d %H:%M:%S')))
	else:
		print("ALERT: Skipping current social ICO, duplicate")

		
	conn.commit()
	conn.close()

def updateTicker():
	conn = getConnected()
	cur = conn.cursor()
	
	cur.execute("SELECT * FROM cryptocounter_generalmarket")
	gm = cur.fetchall()
	
	cm = getAPI("https://api.coinmarketcap.com/v1/global/")
	
	cap = cm["total_market_cap_usd"]
	vol = cm["total_24h_volume_usd"]
	dom = cm["bitcoin_percentage_of_market_cap"]
	d = cm["last_updated"]
	dt = str(datetime.datetime.fromtimestamp(d))
	if(len(gm) > 0):
		#update
		cur.execute("UPDATE cryptocounter_generalmarket SET market_cap = {}, volume = {}, btc_dominance = {}, date_added = '{}' WHERE id=1".format(cap,vol,dom,dt))
		print("Current ticker info updated: "+ str(datetime.datetime.fromtimestamp(d).strftime('%Y-%m-%d %H:%M:%S')))
	else:
		#insert
		cur.execute("INSERT INTO cryptocounter_generalmarket (market_cap, volume, btc_dominance, date_added) VALUES({},{},{},'{}')".format(cap,vol,dom,dt))
		print("Current ticker info added: "+ str(datetime.datetime.fromtimestamp(d).strftime('%Y-%m-%d %H:%M:%S')))

	conn.commit()
	conn.close()
	
def updateGoogleInfo():
	#get google for general, coin, and ICO
	#TODO: If works on after school, add limits to SELECT
	conn = getConnected()
	cur = conn.cursor()
	cc = "cryptocounter_"

	## general ##
	cur.execute("SELECT id, date FROM "+cc+"overallsocial")
	gen = cur.fetchall()
	genGoogle = getGoogleTrends("cryptocurrency")
	for i in range(0, len(genGoogle)):
		for j in range(0, len(gen)):
			if(str(gen[j][1])[:-6] == genGoogle[i]["date"]):
				gid = gen[j][0]
				gtrend = genGoogle[i]["trend"]
				cur.execute("UPDATE "+cc+"overallsocial SET  num_trends={} WHERE id={}".format(gtrend,gid))
				
	## coin ##
	
	cur.execute("SELECT coin_id, coin_name FROM "+cc+"Coin")
	coinNames = cur.fetchall()
	
	for p in range(0, len(coinNames)): #for each coin
		genGoogle = getGoogleTrends(coinNames[p][1]) #get gt
		if(genGoogle == -1):
			continue
		for i in range(0, len(genGoogle)): #for each date in gt
			cur.execute("SELECT "+cc+"socialcoin.id, "+cc+"Coin.coin_name, "+cc+"socialcoin.date FROM "+cc+"socialcoin INNER JOIN "+cc+"Coin ON "+cc+"socialcoin.coin_id_id ="+cc+"Coin.coin_id WHERE "+cc+"Coin.coin_name ='"+coinNames[p][1]+"'")
			genCoin = cur.fetchall()
			for j in range(0, len(genCoin)): #find date in DB
				if(str(genCoin[j][2])[:-6] == genGoogle[i]["date"] and genCoin[j][1] == coinNames[p][1]):
					gid = genCoin[j][0]
					gtrend = genGoogle[i]["trend"]
					cur.execute("UPDATE "+cc+"socialcoin SET  num_trends={} WHERE id={}".format(gtrend,gid))
	
	## ICO ##
	cur.execute("SELECT ico_id, ico_name FROM "+cc+"ico ORDER BY ico_name ASC")
	icoNames = cur.fetchall()
	
	for p in range(0, len(icoNames)): #for each coin
		genGoogle = getGoogleTrends(icoNames[p][1]) #get gt
		if(genGoogle == -1):
			continue
		for i in range(0, len(genGoogle)): #for each date in gt
			cur.execute("SELECT "+cc+"socialico.id, "+cc+"ico.ico_name, "+cc+"socialico.date FROM "+cc+"socialico INNER JOIN "+cc+"ico ON "+cc+"socialico.ico_id_id ="+cc+"ico.ico_id WHERE "+cc+"ico.ico_name ='"+icoNames[p][1]+"'")
			genICO = cur.fetchall()
			for j in range(0, len(genICO)): #find date in DB
				if(str(genICO[j][2])[:-6] == genGoogle[i]["date"] and genICO[j][1] == icoNames[p][1]):
					gid = genICO[j][0]
					gtrend = genGoogle[i]["trend"]
					cur.execute("UPDATE "+cc+"socialico SET  num_trends={} WHERE id={}".format(gtrend,gid))
	
	conn.commit()
	conn.close()

def updateTwitterInfo():
	#get google for general and ICO
	#TODO: If works on after school, add limits (to ICO) to SELECT
	print("NOTE: This will take over 5+ hours, you may use the site while cron is working")
	conn = getConnected()
	cur = conn.cursor()
	cc = "cryptocounter_"
	
	day = 86400
	d = time.time()
	now = int(d-(d%day))

	## general ##
	cur.execute("SELECT  id, date, num_tweets FROM "+cc+"overallsocial ORDER BY date ASC LIMIT 1")
	gen = cur.fetchall()
	dt = int(time.mktime(gen[0][1].timetuple()))
	ld = int(dt-(dt%day))
	
	if(ld == now):
		if(gen[0][2] == -1):
			numGenTweets = parseGeneralTwitter()
			cur.execute("UPDATE "+cc+"overallsocial SET  num_tweets={} WHERE id={}".format(numGenTweets,gen[0][0]))
		else:
			print("SKIPPING GENERAL TWEET: already recorded")
	else:	
		print("SKIPPING GENERAL TWEET: date mismatch")

	'''			
	## ICO ##
	cur.execute("SELECT "+cc+"socialico.id, "+cc+"ico.ico_name, "+cc+"socialico.date FROM "+cc+"socialico INNER JOIN "+cc+"ico ON "+cc+"socialico.ico_id_id ="+cc+"ico.ico_id")
	genICO = cur.fetchall()
	
	cur.execute("SELECT ico_id, ico_name FROM "+cc+"ico")
	icoNames = cur.fetchall()
	
	for p in range(0, len(icoNames)): #for each coin
		genGoogle = getGoogleTrends(icoNames[p][1]) #get gt
		if(genGoogle == -1):
			continue
		for i in range(0, len(genGoogle)): #for each date in gt
			for j in range(0, len(genICO)): #find date in DB
				if(str(genICO[j][2])[:-6] == genGoogle[i]["date"]):
					gid = genICO[j][0]
					gtrend = genGoogle[i]["trend"]
					cur.execute("UPDATE "+cc+"socialico SET  num_trends={} WHERE id={}".format(gtrend,gid))
	'''		
	conn.commit()
	conn.close()

	
### TESTING CODE BELOW ###
#truncate all coin and social DB for a clean start
def truncateDB(test=False):
	db_info = settings.DATABASES["default"]
	try:
		conn = psycopg2.connect("dbname="+db_info["NAME"]+" user="+db_info["USER"]+" host="+db_info["HOST"]+" password="+db_info["PASSWORD"])
	except:
		print("I am unable to connect to the db")

	tableList = ["coin", "price","ico","overallsocial","socialcoin","socialico","generalmarket"]
	cur = conn.cursor()
	for item in tableList:
		cur.execute("TRUNCATE TABLE cryptocounter_"+item+" RESTART IDENTITY CASCADE")
		if(not(test)):
			print("Truncated "+item)
	seqList = ["coin_coin", "ico_ico","price","overallsocial","socialcoin","socialico"]
	for item in seqList:
		cur.execute("ALTER SEQUENCE cryptocounter_"+item+"_id_seq RESTART 1")
	conn.commit()
	conn.close()


def main(test=False): #setup for initial run
	if(not(test)):
		#a = time.time()
		print("[Cron is setting tracked coins]")
		setTrackedCoins()
		print("[Cron is adding Historical Prices]")
		updateHistoricalPrice(historyDays)	#184,numbers of days
		print("[Cron is adding today's price]")
		updateCurrentPrice()
		print("[Cron is updating ICO data]")
		updateICO()
		print("[Cron is updating general ticker info]")
		updateTicker()
		print("[Cron is updating social coin data]")
		updateSocialCoin()
		print("[Cron is updating overall social data]") 
		updateOverallSocial()		
		print("[Cron is updating social ICO data]")
		updateSocialICO()
		print("\n\n[~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~]")
		print("[YOU CAN NOW VIEW THE UPDATED INFO IN THE SITE]")
		print("[~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~]\n\n")
		#b = time.time()
		#c = int(b-a)
		#print("\nThis took " + str(round(c/60,2)) + " minutes")
		print("[Cron is adding google trends to data]")
		updateGoogleInfo()
		#d = int(time.time() - a)
		#print("\nThis took " + str(round(d/60,2)) + " minutes")
		print("[Cron is adding number of tweets to data]")
		#updateTwitterInfo()
		if("c" in mode):
			print("[Cron is starting cronjobs]")
			sched.start() #start cron
	else:
		setTrackedCoins()
		updateHistoricalPrice(historyDays)	#184,numbers of days
		updateCurrentPrice()
		updateICO()
		updateTicker()
		updateSocialCoin()
		updateOverallSocial()		
		updateSocialICO()
		updateGoogleInfo()
		#updateTwitterInfo()



### CRON CALLS ###
sched = BlockingScheduler(timezone="UTC")
sched.add_job(main, 'cron', [True], hour=0, minute=0)
#sched.add_job(main, 'interval', [True], minutes=1)
'''
calling main(True) replaced below
sched.add_job(setTrackedCoins, 'cron', hour=0, minute=0)
sched.add_job(updateCurrentPrice, 'cron', hour=0, minute=0)
sched.add_job(updateICO, 'cron', hour=0,minute=0)
sched.add_job(updateOverallSocial, 'cron', hour=0,minute=0)
sched.add_job(updateSocialCoin, 'cron', hour=0,minute=0)
sched.add_job(updateSocialICO, 'cron', hour=0,minute=0)
'''
		
### MAIN TESTING CALLS ###
# Import the python xUnit framwork
import unittest

class TestCron(unittest.TestCase):

	def assertStringContains(self, needle, haystack):
		self.assertTrue(haystack.find(needle) >= 0, 'Looking for "{}" in "{}"'.format(needle, haystack))

	@classmethod
	def setUpClass(cls):
		truncateDB(True)

	def setUp(self):
		del trackedCoins[:]
		numCoins = 10

	def tearDown(self):
		truncateDB(True)
		numCoins = 10

	#testing API calls
	def testA_API_CMC(self):
		res = getAPI(coinMarketCap)
		self.assertStringContains('BTC',str(res))
		self.assertStringContains('ETH',str(res))
		self.assertStringContains('MIOTA',str(res))
		self.assertTrue(len(res) == 100, "Checking for 100 items")

	def testA_API_CC(self):
		res = getAPI(cryptoCompare+"pricemulti?fsyms=BTC,ETH,IOT&tsyms=USD")
		self.assertStringContains('BTC',str(res))
		self.assertStringContains('ETH',str(res))
		self.assertStringContains('IOT',str(res))
		self.assertTrue(len(res) == 3, "Checking for 3 coins")

	def testA_API_IWL(self):
		res = getAPI(icoWatchList)["ico"]
		self.assertTrue(len(res) == 3,"Checking for 3 ICO groups")
		self.assertTrue(len(res["live"]) > 1, "Checking for a live ICO")
		self.assertTrue(len(res["upcoming"]) > 1, "Checking for a upcoming ICO")
		self.assertTrue(len(res["finished"]) > 100, "Checking for finished ICO")

	#testing connection
	def testB_DBconnect(self):
		res = getConnected()
		self.assertIsNotNone(res)

	#testing getting tracked coins
	def testC_GetTrackedCoins(self):
		self.assertEqual(len(trackedCoins),0)
		getTrackedCoins()
		cur = getConnected().cursor()
		cur.execute("SELECT * FROM cryptocounter_coin")
		res = cur.fetchall()
		self.assertEqual(len(trackedCoins),len(res))

	#testing setting tracked coins
	def testC_SetTrackedCoins(self):
		self.assertEqual(len(trackedCoins),0)
		setTrackedCoins()
		self.assertEqual(len(trackedCoins),numCoins)

	#testing setting tracked coins, updating
	def testC_SetTrackedCoinsUpdate(self):
		self.assertEqual(len(trackedCoins),0)
		setTrackedCoins()
		self.assertEqual(len(trackedCoins),numCoins)
		self.numCoins = 25
		setTrackedCoins()
		self.assertEqual(len(trackedCoins),numCoins)
		self.numCoins = 100
		setTrackedCoins()
		self.assertEqual(len(trackedCoins),numCoins)

	#testing parseCurrentPrice given a coinList
	def testD_ParseCP_picked(self):
		tlist = ["BTC","ETH","MIOTA"]
		res = parseCurrentPrice(tlist)
		self.assertStringContains('BTC',str(res))
		self.assertStringContains('ETH',str(res))
		self.assertStringContains('IOTA',str(res))

	#testing parseCurrentPrice with the true coinList
	def testD_ParseCP_true(self):
		setTrackedCoins()
		res = parseCurrentPrice(trackedCoins)
		self.assertEqual(len(res),numCoins)

	#testing parseHistoricalPrice giving a coinList a date
	def testD_ParseHP_picked(self):
		tlist = ["BTC","ETH","MIOTA"]
		res = parseHistoricalPrice(tlist,1519430400)
		self.assertStringContains('BTC',str(res))
		self.assertStringContains('ETH',str(res))
		self.assertStringContains('IOTA',str(res))
		HPString = [{'ticker': 'BTC', 'price': 9705.73, 'circ_supply': '16968475.0', 'percent_change': -1, 'market_cap': '115426693710', 'date': 1519430400}, {'ticker': 'ETH', 'price': 833.49, 'circ_supply': '98724768.0', 'percent_change': -1, 'market_cap': '39500668024.0', 'date': 1519430400}, {'ticker': 'IOTA', 'price': 1.74, 'circ_supply': '2779530283.0', 'percent_change': -1, 'market_cap': '2757622025.0', 'date': 1519430400}]
		self.assertEqual(res[0]["ticker"],HPString[0]["ticker"])
		self.assertEqual(res[1]["ticker"],HPString[1]["ticker"])
		self.assertEqual(res[2]["ticker"],HPString[2]["ticker"])
		self.assertEqual(res[0]["date"],HPString[0]["date"])
		self.assertEqual(res[1]["date"],HPString[1]["date"])
		self.assertEqual(res[2]["date"],HPString[2]["date"])

	#testing parseCurrentPrice with true coinList and a date
	def testD_ParseHP_true(self):
		setTrackedCoins()
		res = parseHistoricalPrice(trackedCoins,1519430400)
		self.assertEqual(len(res),numCoins)

	#testing parseICO returns exspected output
	def testD_ParseICO(self):
		res = parseICO()
		self.assertTrue(len(res) > 100,"Checking for at least  100 ICO")

	#parseTwitterLive
	#parseTwitterHistory
	#parseGoogleTends
	#parseGeneralNews
	#getCoinNews

	#testing adding price info to DB
	def testF_DB_priceInfo(self):
		tlist = ["BTC","ETH","MIOTA"]
		res = parseCurrentPrice(tlist)
		addPriceInfo(res)
		#check DB of changes
	'''
	#testing updating current price
	def testF_DB_CurrentPrice(self):
		setTrackedCoins()
		updateCurrentPrice()
		#check DB of changes
	
	#testing updating current price, duplicate
	def testF_DB_CurrentPriceDuplicate(self):
		setTrackedCoins()
		updateCurrentPrice()
		updateCurrentPrice()
	
	#testing updating historical price, 7 days
	def testF_DB_historicalPrice(self):
		setTrackedCoins()
		d = time.time()
		now = int(d-(d%86400))
		past = now - 86400 * 7
		updateHistoricalPrice(past)

	#testing updating ICO
	def testF_DB_ICO(self):
		updateICO()
	'''
	#testing main without starting cronjobs
	'''
	def testG_DB_mainNoCron_Init(self):
		main(False)

	def testG_DB_mainNoCron_InitTime():
		a = time.time()
		main(False)
		b = time.time()
		c = int(b-a)
		print("\nSetup took " + round(c/60,2) + " minutes")

	def testH_DB_mainNoCron_Full(self):
		main(False)
		main(False)
	'''

import getopt

fullCmdArguments = sys.argv
argumentList = fullCmdArguments[1:]
unixOptions = "hce:rtp:d"
gnuOptions = ["help", "cron", "cronEnd=" "reset", "test", "history=", "debug"]

try:  
    arguments, values = getopt.getopt(argumentList, unixOptions, gnuOptions)
except getopt.error as err:  
    # output error, and return with an error code
    print (str(err))
    sys.exit(2)
	
for currentArgument, currentValue in arguments:
	if currentArgument in ("-h", "--help"):
		print("----------------------------------------------------------------------------")
		print("long argument       short argument    definition")  
		print("----------------------------------------------------------------------------")
		print("--help                 -h             Show this help message and exit")
		print("--cron                 -c             Enable cron mode")
		print("--reset                -r             Truncate all tables that cron interacts with")
		print("--test                 -t             Start xUnit tests")
		print("--history [days]       -p             Sets the number of days to go back in history")
		print("                                 		Default: 184 days (6 months)")
		print("--debug                -d             Debug mode of testing as we code")
		print("-----------------------------------------------------------------------------")
		sys.exit(0)
	elif currentArgument in ("-c", "--cron"):
		print ("Enabling cron mode")
		mode.append("c")
	elif currentArgument in ("-r", "--reset"):
		print ("Resetting tables cron interacts with")
		truncateDB(False) #reset tables
		sys.exit(0)
	elif currentArgument in ("-t", "--test"):
		print ("Starting xUnit tests")
		sys.argv = [sys.argv[0], "-v"]
		unittest.main()
		sys.exit(0)
	elif currentArgument in ("-p", "--history"):
		if(not(currentValue.isdigit())):
			print("option --history requires an int argument")
			sys.exit(1)
		print (("Changed the default history log to {} days").format(int(currentValue)))
		historyDays = int(currentValue)
	elif currentArgument in ("-d", "--debug"):
		print("Currently in debug mode:")
		### Add testing code below ###
		#truncateDB(True)
		setTrackedCoins()
		#updateICO()
		#updateSocialICO()
		#updateTwitterInfo()
		print(getFacebook("cryptocurrency"))
		#print(tmp)
		### End of testing code ###
		sys.exit(0)

if __name__ == '__main__':
	main() #setup init calls
