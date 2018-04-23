# functions to retrieve data to provide to templates
from .models import Coin, Price, Ico, WatchItem, WatchIco, GeneralMarket, SocialCoin
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

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
                temp = {'coin_id':coin.coin_id, 'coin_name':coin.coin_name, 'ticker':coin.ticker, 'price':pData.price,
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
            temp = {'ico_id':ico.ico_id, 'daysRemaining':daysRemaining, 'startdate':ico.startdate, 'enddate':ico.enddate,
            'ico_name':ico.ico_name, 'description':ico.description}
            data.append(temp)
        except:
            print('No ICO data found')
    return data

# return all data on an individual coin
def getCoinDetails(cname):
    coinHistory = []
    coinSocialHistory = []
    # get coin info
    try:
        coin = Coin.objects.get(coin_name=cname)
    except:
        print('Coin does not exist in database')

    # get the coin's current price
    time = datetime.now() - timedelta(days=31)

    # try to get the pricing data for coin if there's any
    try:
        prices = Price.objects.filter(coin_id=coin.coin_id, date__gte=time).order_by('-date')
        coinPrice = prices[0]

        # create data points
        for c in prices:
            temp = {}
            pyDate = c.date
            year = pyDate.year
            day = pyDate.day
            month = pyDate.month - 1
            temp['year'] = year
            temp['month'] = month
            temp['day'] = day
            temp['price'] = c.price
            coinHistory.append(temp)
    except:
        print('No pricing data for coin found')

    # get coin's social trends
    try:
        social = SocialCoin.objects.filter(coin_id=coin.coin_id, date__gte=time).order_by('-date')

        # create data points
        for c in social:
            temp = {}
            pyDate = c.date
            year = pyDate.year
            day = pyDate.day
            month = pyDate.month - 1
            temp['year'] = year
            temp['month'] = month
            temp['day'] = day
            temp['num_tweets'] = c.num_tweets
            temp['num_subs'] = c.num_subs
            temp['num_likes'] = c.num_likes
            temp['num_articles'] = c.num_articles
            coinSocialHistory.append(temp)
    except:
        print('No social data for coin found')

    # send back the relevant info
    coinData = {'coin_name':coin.coin_name, 'ticker':coin.ticker, 'price':coinPrice.price,
    'circ_supply':coinPrice.circ_supply, 'percent_change':coinPrice.percent_change, 'market_cap':coinPrice.market_cap}

    return {'coinData':coinData, 'coinHistory':coinHistory, 'coinSocial':coinSocialHistory}

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
            temp = {'coin_id':names.coin_id, 'coin_name':names.coin_name, 'ticker':names.ticker, 'price':pData.price,
            'circ_supply':pData.circ_supply, 'percent_change':pData.percent_change, 'market_cap':pData.market_cap}
            coinList.append(temp)
    except:
        print('No watched coins watched by user')

    return coinList

# returns ICOs a user watches
def getWatchedIcos(uname):
    icoList = []
    # get the user
    user = User.objects.get(username = uname)
    # get watched coins
    try:
        # get user's watched coins
        watchIcos = WatchIco.objects.filter(username=user)
        # get pricing for each coin
        for i in watchIcos:
            # get ICO info
            try:
                ico = Ico.objects.get(ico_id=i.ico_id.ico_id)

                currTime = datetime.now(timezone.utc)
                # determine if ICO is live
                daysRemaining = ico.enddate.date() - currTime.date()
                temp = {'ico_id':ico.ico_id, 'daysRemaining':daysRemaining, 'startdate':ico.startdate, 'enddate':ico.enddate,
                'ico_name':ico.ico_name, 'description':ico.description}
                icoList.append(temp)
            except:
                print('ICO does not exist in database')

    except:
        print('No watched ICOs by user')

    return icoList

# add a coin to a user's Watchlist
def addWatchedCoin(uname, cid):
    # check if coin already being tracked by user
    if WatchItem.objects.filter(username__username=uname, coin_id=cid).exists():
        print("Coin is already being tracked by user")
        return
    # get user instance
    user = User.objects.get(username = uname)
    coin = Coin.objects.get(coin_id = cid)
    # add coin to user's tracked coins
    item = WatchItem(username = user, coin_id = coin)
    item.date_added=datetime.now(timezone.utc)
    item.save()
    if item is None:
        print("Failed adding coin")
        return
    else:
        print("Coin now being tracked")
    return

# remove a coin from watchlist
def deleteWatchedCoin(uname, cid):
    # check if coin not being tracked by user
    if not WatchItem.objects.filter(username__username=uname, coin_id=cid).exists():
        print("Coin is not being tracked by user")
        return
    # get user instance
    user = User.objects.get(username = uname)
    coin = Coin.objects.get(coin_id = cid)

    # remove coin
    item = WatchItem.objects.get(username=user, coin_id=coin).delete()
    return

# add an ICO to a user's Watchlist
def addWatchedIco(uname, iid):
    # check if ICO already being tracked by user
    if WatchIco.objects.filter(username__username=uname, ico_id=iid).exists():
        print("ICO is already being tracked by user")
        return
    # get user instance
    user = User.objects.get(username = uname)
    # get ico instance
    ico = Ico.objects.get(ico_id = iid)
    # add ICO to user's tracked ICOs
    item = WatchIco(username = user, ico_id = ico)
    item.date_added=datetime.now(timezone.utc)
    item.save()
    if item is None:
        print("Failed adding ICO")
        return
    else:
        print("ICO now being tracked")
    return

# remove a coin from watchlist
def deleteWatchedIco(uname, iid):
    # check if coin not being tracked by user
    if not WatchIco.objects.filter(username__username=uname, ico_id=iid).exists():
        print("ICO is not being tracked by user")
        return
    # get user instance
    user = User.objects.get(username = uname)
    ico = Ico.objects.get(ico_id = iid)

    # remove coin
    item = WatchIco.objects.get(username=user, ico_id=ico).delete()
    return

# coin/ico name and ticker for search bar
def getSearchTerms():
    terms = []

    # get all coins
    coins = Coin.objects.all()
    # iterate over each coin
    for c in coins:
        terms.append(str(c.coin_name))
        terms.append(str(c.ticker))

    # get all icos
    icos = Ico.objects.all()
    # iterate over each ico
    for i in icos:
        terms.append(str(i.ico_name))

    return terms

# retrieve banner stats
def getBannerData():
    stats = GeneralMarket.objects.first()
    return stats

# check if coin anme
def isCoinName(cname):
    try:
        c = Coin.objects.get(coin_name = cname)
        return True
    except ObjectDoesNotExist:
        return False

# check if coin ticker
def isCoinTicker(tick):
    try:
        c = Coin.objects.get(ticker = tick)
        return c.coin_name
    except ObjectDoesNotExist:
        return None

# check if ICO name
def isIcoName(iname):
    try:
        i = Ico.objects.get(ico_name = iname)
        return True
    except ObjectDoesNotExist:
        return False
