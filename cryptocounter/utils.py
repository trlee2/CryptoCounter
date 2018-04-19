# functions to retrieve data to provide to templates
from .models import Coin, Price, Ico, WatchItem, WatchIco
from django.contrib.auth.models import User

from datetime import datetime, timedelta, timezone

# return the current pricing info of all coins for market page
def getCurrPrices():
    data = []
    # get all tracked coins
    coins = Coin.objects.all()

    # get time range
    #time = datetime.now() - timedelta(hours=24)

    # check if there are any coins in the DB
    if coins.exists():
        # get each coin price
        for coin in coins:
            # get only the most recent price if there is one
            try:
                pData = Price.objects.filter(coin_id=coin.coin_id).order_by('-date')
                pData = pData[0]
                # create table row
                temp = {'coin_name':coin.coin_name, 'ticker':coin.ticker, 'price':pData.price,
                'circ_supply':pData.circ_supply, 'percent_change':pData.percent_change, 'market_cap':pData.market_cap}
                data.append(temp)
            except:
                print('No pricing data for coin found')
    return data

# return all ICO data for ico page
def getIcoInfo():
    data = []
    # get all tracked ICOs
    icoData = Ico.objects.all()
    currTime = datetime.now(timezone.utc)
    for ico in icoData:
        # determine if ICO is live
        try:
            daysRemaining = ico.enddate.date() - currTime.date()
            temp = {'daysRemaining':daysRemaining, 'startdate':ico.startdate, 'enddate':ico.enddate,
            'ico_name':ico.ico_name, 'description':ico.description}
            data.append(temp)
        except:
            print('No ICO data found')
    return data

# return all data on an individual coin
def getCoinDetails(cname):
    # get coin info
    try:
        coin = Coin.objects.get(coin_name=cname)
    except:
        print('Coin does not exist in database')

    # get the coin's current price
    time = datetime.now() - timedelta(days=30)

    # try to get the pricing data for coin if there's any
    try:
        coinHistory = Price.objects.filter(coin_id=coin.coin_id, date__gte=time).order_by('-date')
        coinPrice = coinHistory[0]
    except:
        print('No pricing data for coin found')
        return []

    # TODO: get coin's social trends

    # send back the relevant info
    coinData = {'coin_name':coin.coin_name, 'ticker':coin.ticker, 'price':coinPrice.price,
    'circ_supply':coinPrice.circ_supply, 'percent_change':coinPrice.percent_change, 'market_cap':coinPrice.market_cap}

    return {'coinData':coinData, 'coinHistory':coinHistory}

# return all data on an individual ICO
def getIcoDetails(iname):
    # get ICO info
    try:
        ico = Ico.objects.get(ico_name=iname)
    except:
        print('ICO does not exist in database')

    # get the coin's current price
    currTime = datetime.now(timezone.utc)

    # determine if ICO is live
    try:
        daysRemaining = ico.enddate.date() - currTime.date()
        temp = {'daysRemaining':daysRemaining, 'startdate':ico.startdate, 'enddate':ico.enddate,
        'ico_name':ico.ico_name, 'description':ico.description}
    except:
        print('No ICO data found')

    # TODO: get ICO's social trends

    # send back the relevant info
    icoData = temp

    return icoData

# add a coin to user's watchlist when on Market page
def addWatchedCoin(username, coin):
    #TODO
    return

# returns coins a user watches
def getWatchedCoins(uname):
    coinList = []
    # get watched coins
    try:
        # get user's watched coins
        watchCoins = WatchItem.objects.filter(username__username=uname)
        # get pricing for each coin
        for c in watchCoins:
            p = Price.objects.filter(coin_id = c.coin_id).order_by('-date')
            names = Coin.objects.get(coin_id = c.coin_id.coin_id)
            pData = p[0]
            temp = {'coin_name':names.coin_name, 'ticker':names.ticker, 'price':pData.price,
            'circ_supply':pData.circ_supply, 'percent_change':pData.percent_change, 'market_cap':pData.market_cap}
            coinList.append(temp)
    except:
        print('No watched coins watched by user')

    return coinList

# returns ICOs a user watches
def getWatchedIcos(uname):
    icoList = []
    # get watched coins
    try:
        # get user's watched coins
        watchIcos = WatchItem.objects.filter(username__username=uname)
        # get pricing for each coin
        for i in watchIcos:
            # get ICO info
            try:
                ico = Ico.objects.get(ico_name=i.ico_id.ico_id)
            except:
                print('ICO does not exist in database')

            currTime = datetime.now(timezone.utc)
            # determine if ICO is live
            try:
                daysRemaining = ico.enddate.date() - currTime.date()
                temp = {'daysRemaining':daysRemaining, 'startdate':ico.startdate, 'enddate':ico.enddate,
                'ico_name':ico.ico_name, 'description':ico.description}
                icoList.append(temp)
            except:
                print('No ICO data found')
    except:
        print('No watched ICOs by user')

    return icoList
