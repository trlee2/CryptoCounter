import requests
import json
import psycopg2
import sys
import CryptoSite.settings as settings
import datetime
import time
import pprint
#from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
 
'''
pip install requests
pip install apscheduler

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
			cur.execute("INSERT INTO cryptocounter_ico (ico_name, startDate, endDate, description, search_terms) VALUES('{}','{}','{}','{}','{}')".format(n,s,e,d,st))

		
	conn.commit()
	conn.close()

def testcron():
	print(datetime.datetime.now())

### CRON CALLS ###
#sched = BackgroundScheduler()
sched = BlockingScheduler(timezone="UTC")
sched.add_job(setTrackedCoins, 'cron', hour=0, minute=0)
sched.add_job(updateCurrentPrice, 'cron', hour=0, minute=5)
sched.add_job(updateICO, 'cron', hour=0,minute=10)
#sched.add_job(testcron, 'interval', minutes=1*2)

def main(test=True): #setup for initial run
	if(test):
		print("[Cron is setting tracked coins]")
	setTrackedCoins()
	if(test):
		print("[Cron is adding Historical Prices]")
	updateHistoricalPrice(184)	#184,numbers of days
	if(test):
		print("[Cron is adding today's price]")
	updateCurrentPrice()
	if(test):
		print("[Cron is updating ICO data]")
	updateICO()
	if(test):
		print("[Cron is starting cronjobs]")
	if(test):
		#sched.start() #start cron
		pass



### TESTING CODE BELOW ###

#truncate all coin and social DB for a clean start
def truncateDB(text=True):
	db_info = settings.DATABASES["default"]
	try:
		conn = psycopg2.connect("dbname="+db_info["NAME"]+" user="+db_info["USER"]+" host="+db_info["HOST"]+" password="+db_info["PASSWORD"])
	except:
		print("I am unable to connect to the db")

	tableList = ["coin", "price","ico","overallsocial","socialcoin","socialico"]
	cur = conn.cursor()
	for item in tableList:
		cur.execute("TRUNCATE TABLE cryptocounter_"+item+" RESTART IDENTITY CASCADE")
		if(text):
			print("Truncated "+item)
	cur.execute("ALTER SEQUENCE cryptocounter_coin_coin_id_seq RESTART 1")
	cur.execute("ALTER SEQUENCE cryptocounter_ico_ico_id_seq RESTART 1")
	cur.execute("ALTER SEQUENCE cryptocounter_price_id_seq RESTART 1")

	conn.commit()
	conn.close()


if __name__ == '__main__':
	main() #setup init calls
	#truncateDB() #reset tables






### MAIN TESTING CALLS ###
# Import the python xUnit framwork
import unittest

class TestCron(unittest.TestCase):

	def assertStringContains(self, needle, haystack):
		self.assertTrue(haystack.find(needle) >= 0, 'Looking for "{}" in "{}"'.format(needle, haystack))

	@classmethod
	def setUpClass(cls):
		truncateDB(False)

	def setUp(self):
		del trackedCoins[:]
		numCoins = 10

	def tearDown(self):
		truncateDB(False)
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