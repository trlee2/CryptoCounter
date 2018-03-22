import requests
import json
#import pprint
'''
pip install requests
pip install django-crontab
'''


'''
This is the code for updaing the database with new information on 
the coins and ICO ran by cronjobs fround in the 
CryptoSite/settings.py file.
'''
numCoins = 10; #Top coins from coinMarketCap.com
coinMarketCap = "https://api.coinmarketcap.com/v1/ticker/?limit="+str(numCoins)
cryptocompare = "https://min-api.cryptocompare.com/data/"

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
and return an array of their names.

@returns	String[]	
'''
def getTrackedCoins():
	#print("TODO")
	return ['BTC','ETH']

'''
Scans the coinmarketcap API for the top numCoins and compares it 
with the list retrieved from getTrackedCoins(). If a coin is not 
found on the current list, add the new coin to both the database 
and the the list of searched coins.

@params		int numCoins
@returns	void	
'''
def setTrackedCoins(numCoins):
	print("TODO")

'''
Parse the JSON data from the cryptocompare API and return an array 
of current prices for each coin.

@params		String[] coinList
@returns	Array of coin:price
'''
def parseCurrentPrice(coinList):
	coins = ""
	for i in range(0, len(coinList)):
		coins += coinList[i]
		if(i != len(coinList)-1):
			coins += ","

	data = getAPI(cryptocompare+"pricemulti?fsyms="+coins+"&tsyms=USD")
	
	prices = {}
	for key in data.keys():
		prices[key] = data[key]["USD"]

	return prices

'''
Parse the JSON data from the cryptocompare API and return an array 
of historical data for each coin on date. 

@params		String[] coinList, int date
@returns	Array of coin:price
'''
def parseOldPrice(coinList, date):
	prices = []
	for i in range(0, len(coinList)):
		data = getAPI(cryptocompare+"pricehistorical?fsym="+coinList[i]+"&tsyms=USD&ts="+str(date))
		for key in data.keys():
			price = {}
			price["coin_name"] = data[key]
			price["price"] = data[key]["USD"]
			prices[i] = price

	return prices

'''
Parse the JSON data from the icowatchlist API and compare it with 
the ICO already in the database. Add any ICOs not in our database 
to our database.
		
@returns	String[]	
'''
def parseICO():
	print("TODO")

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
	print(data)

### TESTING CODE BELOW ###
## currently just testing calls

def main():
	data = getAPI(coinMarketCap)

	clist = getTrackedCoins()
	plist = parseCurrentPrice(clist)
	#plist = parseOldPrice(clist,1452680440)

	addToDB_print("test",["testc"],plist)

main()