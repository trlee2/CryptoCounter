# functions to retrieve data to provide to templates
from .models import Coin, Price, Ico

from datetime import datetime, timedelta

# return the current pricing info of all coins for market page
def getCurrPrices():
    data = []
    # get all tracked coins
    coins = Coin.objects.all()
    # get time range
    time = datetime.now() - timedelta(hours=24)
    # get each coin price
    for coin in coins:
        # get only the most recent price
        pData = Price.objects.filter(coin_id=coin.coin_id).get(date__gte=time)
        # create table row
        temp = {'coin_name':coin.coin_name, 'ticker':coin.ticker, 'price':pData.price,
        'circ_supply':pData.circ_supply, 'percent_change':pData.percent_change, 'market_cap':pData.market_cap}
        data.append(temp)
    return data

# return all ICO data for ico page
def getIcoInfo():
    # get all tracked ICOs
    icoData = Ico.objects.all()
    return icoData

# return all data on an individual coin
def getCoinDetails(cname):
    # get coin info
    coin = Coin.objects.get(coin_name=cname)
    # get the coin's current price
    time = datetime.now() - timedelta(hours=24)
    coinPrice = Price.objects.filter(coin_id=coin.coin_id).get(date__gte=time)
    # TODO: get coin's social trends

    # send back the relevant info
    coinData = {'coin_name':coin.coin_name, 'ticker':coin.ticker, 'price':coinPrice.price,
    'circ_supply':coinPrice.circ_supply, 'percent_change':coinPrice.percent_change, 'market_cap':coinPrice.market_cap}
    return coinData
