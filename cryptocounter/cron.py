import requests
import json
import psycopg2
import sys
sys.path.insert(0, '../CryptoSite/')
import settings
import pprint
 
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
Pulls the list of coins currently being tracked from the database 
and puts them in the trackedCoins array

@returns	void
'''
def getTrackedCoins():
	db_info = settings.DATABASES["default"]
	try:
		conn = psycopg2.connect("dbname="+db_info["NAME"]+" user="+db_info["USER"]+" host="+db_info["HOST"]+" password="+db_info["PASSWORD"])
	except:
		print("I am unable to connect to the db")

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
	db_info = settings.DATABASES["default"]
	try:
		conn = psycopg2.connect("dbname="+db_info["NAME"]+" user="+db_info["USER"]+" host="+db_info["HOST"]+" password="+db_info["PASSWORD"])
	except:
		print("I am unable to connect to the db")

	cur = conn.cursor()
	market = getAPI(coinMarketCap+"?limit="+str(numCoins))
	for i in range(0, len(market)):
		if(market[i]["symbol"] not in trackedCoins):
			#TODO: find true blockchain, fix block_chain (change symbol->name)
			cur.execute("INSERT INTO cryptocounter_coin (coin_id, coin_name, ticker, block_chain, search_terms) VALUES ("+str(trackedLength)+",'"+market[i]["name"]+"','"+market[i]["symbol"]+"','"+market[i]["symbol"]+"','[\""+market[i]["symbol"]+"\",\""+market[i]["name"]+"\"]')")
			trackedLength +=1

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
			coins += "IOTA"
		else:
			coins += coinList[i]
		if(i != len(coinList)-1):
			coins += ","

	data = getAPI(cryptoCompare+"pricemulti?fsyms="+coins+"&tsyms=USD")
	market = getAPI(coinMarketCap) #TODO:fix to include if rank is > 100

	prices = ["price"]
	for key in data.keys():
		want = {}
		for i in range(0, len(market)):
			if(key == "IOTA" and market[i]["symbol"] == "MIOTA"):
				want = market[i]
				break
			elif(key == market[i]["symbol"]):
				want = market[i]
				break

		price = {}
		price["ticker"] = key
		price["price"] = data[key]["USD"]
		price["circ-supply"] = want["available_supply"]
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
	prices = ["price"]
	for i in range(0, len(coinList)):
		cList = coinList[i]
		if(coinList[i] == "MIOTA"):
			cList = "IOTA"
		data = getAPI(cryptoCompare+"pricehistorical?fsym="+cList+"&tsyms=USD&ts="+str(date))
		market = getAPI(coinMarketCap) #TODO:fix to include if rank is > 100

		for key in data.keys():
			want = {}
			for j in range(0, len(market)):
				if(key == "IOTA" and market[j]["symbol"] == "MIOTA"):
					want = market[j]
					break
				elif(key == market[j]["symbol"]):
					want = market[j]
					break

			price = {}
			price["ticker"] = key
			price["price"] = data[key]["USD"]
			price["circ-supply"] = want["available_supply"]
			price["percent_change"] = -1
			price["market_cap"] = want["market_cap_usd"]
			price["date"] = date
			prices.append(price)

	return prices

'''
Parse the JSON data from the icowatchlist API and compare it with 
the ICO already in the database. Add any ICOs not in our database 
to our database.
		
@returns	String[]	
'''
def parseICO():
	data = getAPI(icoWatchList)

	ico_dict = ["ico"]
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
@returns	String[][]	
'''
#def parseTwitterLive(coinList):
#	print("TODO")

'''
Parse the Twitter API for old information on the coins being 
searched and return the array of data.

@params		String[] coinList
@returns	String[][]	
'''
#def parseTwitterHistory(coinList):
#	print("TODO")

'''
AParse the Google Trends data and return it as an array.

@params		String[] coinList
@returns	String[][]
'''
#def getGoogleTrends(coinList):
#	print("TODO")

'''
Parse the general news of cryptocurrencies and return as array.

@params		String[] coinList
@returns	String[][]	
'''
#def getGeneralNews(coinList):
#	print("TODO")

'''
Parse the specific news for the coin.

@params		String coin
@returns	String[][]	
'''
#def getCoinNews(coin):
#	print("TODO")

'''
A generic function for adding our parsed data to the database.

@params		String table, String[] column, String[] data
@returns	void	
'''
def addToDB(table,column,data):
	print("TODO")

'''
A generic function for printing out information, mimics the 
addToDB function excepts does not write to DB.

@params		String table, String[] column, String[] data
@returns	void	
'''
def addToDB_print(table,column, data):
	db_info = settings.DATABASES["default"]
	try:
		conn = psycopg2.connect("dbname="+db_info["NAME"]+" user="+db_info["USER"]+" host="+db_info["HOST"]+" password="+db_info["PASSWORD"])
	except:
		print("I am unable to connect to the db")

	cur = conn.cursor()
	
	cur.execute("SELECT * FROM cryptocounter_coin")
	row = cur.fetchall()

	info = data[0] #price,ico
	pprint.pprint(data)
	for j in range(0, len(row)):
		coin_id = -1
		for i in range(1,len(data)):			
			if(data[i]["ticker"] == "IOTA" and row[j][2] == "MIOTA"):
				coin_id = row[j][0]
				break			
			elif(row[j][2] == data[i]["ticker"]):
				coin_id = row[j][0]
				break
		#print(data[i].keys())
		#cur.execute("INSERT INTO "+table+" (coin_id, coin_name, ticker, block_chain, search_terms) VALUES ("+str(trackedLength)+",'"+market[i]["name"]+"','"+market[i]["symbol"]+"','"+market[i]["symbol"]+"','[\""+market[i]["symbol"]+"\",\""+market[i]["name"]+"\"]')")
			


### Commands to be called by CRON ###

#setTrackedCoins() -> once a day

def updateCurrentPrice(): #-> once every ___ ( 5 min or hour)
	#trackedCoins should live
	plist = parseCurrentPrice(trackedCoins)
	addToDB_print("cryptocounter_price",["id","date","price","coin_id_id","circ_supply","market_cap","percent_change"],plist)

def updateHistoricalPrice(date):#-> once upon first boot or every time we need info that can not be found
	#trackedCoins should live
	plist = parseHistoricalPrice(trackedCoins,date)
	addToDB_print("cryptocounter_price",["id","date","price","coin_id_id","circ_supply","market_cap","percent_change"],plist)

def updateICO():#-> once every ___ (day or week)
	plist = parseICO()
	addToDB_print("cruptocounter_ico",["ico_id","ico_name","start","end","description","search_terms"],plist)


### TESTING CODE BELOW ###
## currently just testing calls

def main():
	setTrackedCoins()
	updateCurrentPrice()
	#updateHistoricalPrice(1521746133)
	#updateICO()
	

def testcron():
	print("testing cron jobs")

main()