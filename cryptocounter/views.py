from django.shortcuts import render

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.http import HttpResponseRedirect
from django import forms
from .forms import UserRegistrationForm, UserLoginForm

from .models import WatchItem

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

def coinDetails(request, cname):
    coinData = getCoinDetails(cname)
    return render(request, 'cryptocounter/coinTemplate.html', {'coin':coinData['coinData'], 'coinHistory':coinData['coinHistory']})

def icoDetails(request, iname):
    icoData = getIcoDetails(iname)
    return render(request, 'cryptocounter/icoTemplate.html', {'ico':icoData})

def login(request):
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
                raise forms.ValidationError('Username or password incorrect')
    else:
        form = UserLoginForm()
    return render(request, 'cryptocounter/index.html', {'form' : form})

def register(request):
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
                raise forms.ValidationError('Sorry, that username has already been taken!')
            # email in use
            elif User.objects.filter(email=email).exists():
                raise forms.ValidationError('Sorry, that email is already in use!')
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
    return render(request, 'cryptocounter/register.html', {'form' : form})

def account(request):
    return render(request, 'cryptocounter/account.html')

def header(request):
    loggedin = request.user.is_authenticated
    terms = getSearchTerms()
    return render(request, 'cryptocounter/header.html', {'loggedin':loggedin, 'searchTerms':terms})

def footer(request):
    return render(request, 'cryptocounter/footer.html')
