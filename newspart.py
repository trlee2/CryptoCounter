
import pprint

from newsapi import NewsApiClient

coin = ['bitcoin','eth','ripple']

def parseCoinNews(keyword):

		api = NewsApiClient(api_key='e9f31afd6dd54e14930244b5f52cdc45')

		newsapi = "https://newsapi.org/v2/everything?"

		#result = api.get_everything(q = 'bitcoin')

		for i in keyword: 
				
				result = api.get_everything(q = i)
				#pprint.pprint (result)

				#for i in data.keys(): 

				#print(result.keys())

				#print(result.get('status'))

				if (result.get('status') =='ok'):
					print(result.get('totalResults'))
				else:
					print("status is not suitable for getting total numbers")
				#for key, value in result.items():
				#	print(key, value)
				
				#return result.get('totalResults')



parseCoinNews(coin)
'''
def getAPI(api):
	res = requests.get(api)
	data = res.json()
	return data

'''

#def parseGeneralNews(coinList):






#def parseCoinNews(String coin):





