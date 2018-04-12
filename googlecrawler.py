import requests
from bs4 import BeautifulSoup
import argparse

'''
pip install bs4 -> does not work
'''

#parser = argparse.ArgumentParser(description='Get Google Count.')
#parser.add_argument('word', help='word to count')
#args = parser.parse_args()

keyword = ["bitcoin","eth","BTc"]

def parseGoogleTrends(keyword):

		#keyword = ["bitcoin","eth","BTc"]


		for i in keyword: 
				r = requests.get('http://www.google.com/search',
				                 params={'q':'"'+i+'"',
				                         "tbs":"li:1"}
				                )

				soup = BeautifulSoup(r.text,"lxml")

				print (i+":" + soup.find('div',{'id':'resultStats'}).text)

				result_text = soup.find('div',{'id':'resultStats'}).text
				#parse the first 6 char and last 8 char 
				num_result = result_text[6:-8]
				#print the number of keyword 
				print (num_result)

				print (soup.find('div',{'id':'resultStats'}))



parseGoogleTrends(keyword)

