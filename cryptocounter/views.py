from django.shortcuts import render

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.http import HttpResponseRedirect
from django import forms
from .forms import UserRegistrationForm, UserLoginForm, UserAccountForm

from .utils import *

# Create your views here.
def market(request):
    prices = getCurrPrices()
    return render(request, 'cryptocounter/market.html', {'prices':prices})

def ico(request):
    icoData = getIcoInfo()
    return render(request, 'cryptocounter/ico.html', {'icos':icoData})

def socialTrends(request):
    return render(request, 'cryptocounter/trends.html')

def watchlist(request):
    # make sure user is logged in
    if request.user.is_authenticated:
        # get username
        username = request.user.username
        # get watched coins
        watchCoins = getWatchedCoins(username)
        watchIcos = getWatchedIcos(username)
        return render(request, 'cryptocounter/watchlist.html', {'watchCoins':watchCoins,'watchIcos':watchIcos})
    else:
        return HttpResponseRedirect('/login')

def addWatchlistCoin(request, cid):
    # only for adding a coin
    if request.method == 'GET':
        # check to see if user is logged in
        if request.user.is_authenticated:
            # try to add coin to track
            addWatchedCoin(request.user.username, cid)
            return HttpResponseRedirect('/watchlist')
        # user not logged in
        else:
            return HttpResponseRedirect('/login')
    else:
        return HttpResponseRedirect('/market')

def deleteWatchlistCoin(request, cid):
    # only for adding a coin
    if request.method == 'GET':
        # check to see if user is logged in
        if request.user.is_authenticated:
            # try to add coin to track
            deleteWatchedCoin(request.user.username, cid)
            return HttpResponseRedirect('/watchlist')
        # user not logged in
        else:
            return HttpResponseRedirect('/login')
    else:
        return HttpResponseRedirect('/market')

def addWatchlistIco(request, iid):
    # only for adding a coin
    if request.method == 'GET':
        # check to see if user is logged in
        if request.user.is_authenticated:
            # try to add coin to track
            addWatchedIco(request.user.username, iid)
            return HttpResponseRedirect('/watchlist')
        # user not logged in
        else:
            return HttpResponseRedirect('/login')
    else:
        return HttpResponseRedirect('/ico')

def deleteWatchlistIco(request, iid):
    # only for adding a coin
    if request.method == 'GET':
        # check to see if user is logged in
        if request.user.is_authenticated:
            # try to add coin to track
            deleteWatchedIco(request.user.username, iid)
            return HttpResponseRedirect('/watchlist')
        # user not logged in
        else:
            return HttpResponseRedirect('/login')
    else:
        return HttpResponseRedirect('/ico')

def coinDetails(request, cname):
    coinData = getCoinDetails(cname)
    coinTweets = getCoinTweets(cname)
    return render(request, 'cryptocounter/coinTemplate.html', {'coin':coinData['coinData'], 'coinHistory':coinData['coinHistory'], 'coinSocial':coinData['coinSocial'], 'coinTweets':coinTweets['coinTweets']})

def icoDetails(request, iname):
    icoData = getIcoDetails(iname)
    icoTweets = getICOTweets(iname)
    return render(request, 'cryptocounter/icoTemplate.html', {'ico':icoData['icoData'], 'icoTweets':icoTweets['icoTweets']})

def login(request):
    error = None
    if request.method == 'POST':
        # get form data
        form = UserLoginForm(request.POST)
        # clean the form data, checks for security risks
        if form.is_valid():
            # parse form data
            userObj = form.cleaned_data
            username = userObj['username']
            password = userObj['password']

            # Check credentials
            user = authenticate(username = username, password = password)
            if user is not None:
                # log the user in
                auth_login(request, user)
                # redirect to watchlist
                return HttpResponseRedirect('/watchlist')
            else:
                #raise forms.ValidationError('Username or password incorrect')
                error = 'Username or password is incorrect'
                return render(request, 'cryptocounter/index.html', {'form':form, 'error':error})
    else:
        form = UserLoginForm()
    return render(request, 'cryptocounter/index.html', {'form':form, 'error':error})

def register(request):
    errorUname = ''
    errorEmail = ''
    errorPassword = ''
    errorExists = False
    if request.method == 'POST':
        # get form data
        form = UserRegistrationForm(request.POST)
        # clean the form data, checks for security risks
        if form.is_valid():
            # parse form data
            userObj = form.cleaned_data
            firstName = userObj['firstName']
            lastName = userObj['lastName']
            email = userObj['email']
            username = userObj['username']
            password = userObj['password']
            confirmPassword = userObj['confirmPassword']

            # username in use
            if User.objects.filter(username=username).exists():
                #raise forms.ValidationError('Sorry, that username has already been taken!')
                errorUname = 'Sorry, that username has already been taken!'
                errorExists = True
            # email in use
            if User.objects.filter(email=email).exists():
                #raise forms.ValidationError('Sorry, that email is already in use!')
                errorEmail = 'Sorry, that email is already in use!'
                errorExists = True
            # passwords don't match
            if password != confirmPassword:
                #raise forms.ValidationError('Sorry, passwords do not match!')
                errorPassword = 'Passwords do not match!'
                errorExists = True

            if errorExists:
                return render(request, 'cryptocounter/register.html', {'form':form, 'errorUname':errorUname, 'errorEmail':errorEmail, 'errorPassword':errorPassword})
            # create user
            else:
                newUser = User.objects.create_user(username, email, password)
                newUser.first_name = firstName
                newUser.last_name = lastName
                newUser.save()
                # log the user in
                user = authenticate(username = username, password = password)
                auth_login(request, user)
                # redirect to watchlist
                return HttpResponseRedirect('/watchlist')
    else:
        form = UserRegistrationForm()
    return render(request, 'cryptocounter/register.html', {'form':form, 'errorUname':errorUname, 'errorEmail':errorEmail, 'errorPassword':errorPassword})

def account(request):
    errorExists = False
    errorEmail = ''
    errorPassword = ''
    success = False
    # retrieve account details
    if request.method == 'GET':
        # check to see if user is logged in
        if request.user.is_authenticated:
            u = User.objects.get(username = request.user.username)
            form = UserAccountForm({'firstName':u.first_name, 'lastName':u.last_name, 'email':u.email, 'username':u.username})
            return render(request, 'cryptocounter/account.html', {'form':form, 'errorEmail':errorEmail, 'errorPassword':errorPassword, 'success':success})
    # updating account info
    elif request.method == 'POST':
        u = User.objects.get(username = request.user.username)
        # get form data
        form = UserAccountForm(request.POST)
        # clean the form data, checks for security risks
        if form.is_valid():
            # parse form data
            userObj = form.cleaned_data
            firstName = userObj['firstName']
            lastName = userObj['lastName']
            email = userObj['email']
            username = userObj['username']
            password = userObj['password']
            confirmPassword = userObj['confirmPassword']

            # email in use
            if User.objects.filter(email=email).exclude(username=username).exists():
                #raise forms.ValidationError('Sorry, that email is already in use!')
                errorEmail = 'Sorry, that email is already in use!'
                errorExists = True
            # passwords don't match
            if password != confirmPassword:
                #raise forms.ValidationError('Sorry, passwords do not match!')
                errorPassword = 'Passwords do not match!'
                errorExists = True

            if errorExists:
                return render(request, 'cryptocounter/account.html', {'form':form, 'errorEmail':errorEmail, 'errorPassword':errorPassword, 'success':success})
            # update user
            else:
                user = User.objects.get(username__exact = username)
                user.first_name = firstName
                user.last_name = lastName
                user.email = email
                if (password != u.password) and (len(password) != 0):
                    user.set_password(password)
                user.save()

                loguser = authenticate(username = user.username, password = user.password)
                auth_login(request, loguser)
                # success
                success = True
                return render(request, 'cryptocounter/account.html', {'form':form, 'errorEmail':errorEmail, 'errorPassword':errorPassword, 'success':success})
    return HttpResponseRedirect('/login')

def deleteAccount(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            username = request.user.username
            auth_logout(request)
            user = User.objects.get(username__exact = username).delete()
    return HttpResponseRedirect('/login')

def header(request):
    loggedin = request.user.is_authenticated
    terms = getSearchTerms()
    stats = getBannerData()
    return render(request, 'cryptocounter/header.html', {'loggedin':loggedin, 'searchTerms':terms, 'banner':stats})

def footer(request):
    return render(request, 'cryptocounter/footer.html')

def search(request):
    # get the search input
    t = request.GET.get('term', '')

    # check if coin ticker
    n = isCoinTicker(t)
    if n is not None:
        return HttpResponseRedirect('/coindetails/'+n+'/')
    # check if coin name
    elif isCoinName(t):
        return HttpResponseRedirect('/coindetails/'+t+'/')
    # check if ico name
    elif isIcoName(t):
        return HttpResponseRedirect('/icodetails/'+t+'/')
    # coin does not exist
    else:
        return HttpResponseRedirect('/market')
