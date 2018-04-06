import requests
import json
import psycopg2
import sys
sys.path.insert(0, '../CryptoSite/')
import settings
import datetime
import pprint
#from django_cron import CronJobBase, Schedule
 
'''
pip install requests
'''

'''
This is the code for updaing the database with new information on 
the coins and ICO ran by cronjobs fround in the 
CryptoSite/settings.py file.
'''
numCoins = 10; #Top coins from coinMarketCap.com
trackedCoins = [] #coins currently being tracked
coinMarketCap = "https://api.coinmarketcap.com/v1/ticker/"
cryptoCompare = "https://min-api.cryptocompare.com/data/"
icoWatchList = "https://api.icowatchlist.com/public/v1/" 

'''
A universal function that retrieves the JSON data from each of the
APIs we are using and returns the raw JSON Object.

@params String api
@returns	JSON Object	
'''
def getAPI(api):
	res = requests.get(api)
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
		price["date"] = want["last_updated"]
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
Parse the Twitter API for any new information on the coins being 
searched and return the array of data.

@params		String[] coinList
@returns	int	
'''
#def parseTwitterLive(coinList):
#	print("TODO")

'''
Parse the Twitter API for old information on the coins being 
searched and return the array of data.

@params		String[] coinList
@returns	int	
'''
#def parseTwitterHistory(coinList):
#	print("TODO")

'''
AParse the Google Trends data and return it as an array.

@params		String[] coinList
@returns	int
'''
#def getGoogleTrends(coinList):
#	print("TODO")

'''
Parse the general news of cryptocurrencies and return as array.

@params		String[] coinList
@returns	int	
'''
#def getGeneralNews(coinList):
#	print("TODO")

'''
Parse the specific news for the coin.

@params		String coin
@returns	int	
'''
#def getCoinNews(coin):
#	print("TODO")

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

def updateCurrentPrice(): #-> once every ___ ( 5 min or hour)
	#trackedCoins should live	
	plist = parseCurrentPrice(trackedCoins)
	addPriceInfo(plist)
		

def updateHistoricalPrice(date):#-> once upon first boot or every time we need info that can not be found
	#trackedCoins should live
	plist = parseHistoricalPrice(trackedCoins,date)
	addPriceInfo(plist)

def updateICO():#-> once every ___ (day or week)
	plist = parseICO()
	conn = getConnected()
	cur = conn.cursor()

	cur.execute("SELECT ico_name FROM cryptocounter_ico")
	DBico = cur.fetchall()

	for data in plist:
		if(data["ico_name"] not in DBico):
			pprint.pprint(data)

			#dt = str(datetime.datetime.fromtimestamp(int(data["date"])))
			n = str(data["ico_name"])
			#s = str(datetime.datetime.strptime(data["start"],'%Y-%m-%d %H:%M:%S'))
			#e = str(datetime.datetime.strptime(data["end"],'%Y-%m-%d %H:%M:%S'))
			s = str(data["start"])+"-00"
			e = str(data["end"])+"-00"
			d = str(data["description"])
			st = str(data["search_terms"])
			tmp = "INSERT INTO cryptocounter_ico (ico_name, start, end, description, search_terms) VALUES('{}','{}','{}','{}','{}')".format(n,s,e,d,st)
			print(tmp)
			cur.execute(tmp)

		
	conn.commit()
	conn.close()


### TESTING CODE BELOW ###
## currently just testing calls

def main():
	#setTrackedCoins()
	#print(coinList)
	#updateCurrentPrice()
	#updateHistoricalPrice(1521746133)
	updateICO()
	#truncateDB()


	#truncate all coin and social DB for a clean start
def truncateDB():
	db_info = settings.DATABASES["default"]
	try:
		conn = psycopg2.connect("dbname="+db_info["NAME"]+" user="+db_info["USER"]+" host="+db_info["HOST"]+" password="+db_info["PASSWORD"])
	except:
		print("I am unable to connect to the db")

	tableList = ["coin", "price","ico","overallsocial","socialcoin","socialico"]
	cur = conn.cursor()
	for item in tableList:
		cur.execute("TRUNCATE TABLE cryptocounter_"+item+" RESTART IDENTITY CASCADE")
		print("Truncated "+item)
	cur.execute("ALTER SEQUENCE cryptocounter_coin_coin_id_seq RESTART 1")

	conn.commit()
	conn.close()


def testcron():
	print("testing cron jobs")

main()